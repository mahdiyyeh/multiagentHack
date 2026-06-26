import re

from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import clickhouse_logger, tavily_client


def _parse_price(text: str) -> float | None:
    for match in re.finditer(r"£\s*([\d,]+(?:\.\d{2})?)", text):
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            continue
    return None


def _parse_capacity(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(guests|people|capacity|delegates|standing)", text, re.I)
    return int(match.group(1)) if match else None


def _snippet_for_url(search_by_url: dict[str, dict], url: str) -> str:
    return (search_by_url.get(url, {}).get("content") or "").strip()


def _build_candidate(
    url: str,
    title: str,
    raw: str,
    provenance: str,
    search_by_url: dict[str, dict],
) -> dict:
    snippet = _snippet_for_url(search_by_url, url)
    price = _parse_price(raw)
    capacity = _parse_capacity(raw)

    if price is None and snippet:
        snippet_price = _parse_price(snippet)
        if snippet_price is not None:
            price = snippet_price
            raw = snippet
            provenance = f"tavily:search:{url}"

    if capacity is None and snippet:
        capacity = _parse_capacity(snippet)

    return {
        "url": url,
        "title": title,
        "price_gbp": price,
        "capacity": capacity,
        "raw_extract": raw[:4000],
        "grounded": False,
        "grounding_issues": [],
        "confidence": 0.0,
        "provenance": [provenance],
    }


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Extractor", "Extracting prices and specs from pages...")
    results = state.get("search_results", [])
    search_by_url = {r.get("url"): r for r in results if r.get("url")}
    urls = list(search_by_url.keys())[:8]
    calls = state.get("tavily_calls", 0)
    candidates: list[dict] = []
    seen_urls: set[str] = set()

    if urls:
        events = append_log(state, "Extractor", f"Extracting {len(urls)} URLs")
        try:
            extracted = tavily_client.extract(urls)
            calls += 1
            clickhouse_logger.log_event(state["job_id"], "Extractor", "extract", {"count": len(extracted)})
            for item in extracted:
                url = item.get("url", "")
                if not url:
                    continue
                seen_urls.add(url)
                raw = item.get("raw_content") or item.get("content") or ""
                title = item.get("title") or search_by_url.get(url, {}).get("title") or url
                candidates.append(
                    _build_candidate(url, title, raw, f"tavily:extract:{url}", search_by_url)
                )
        except Exception as exc:
            events = append_log(state, "Extractor", f"Extract failed: {exc}")

    for r in results[:8]:
        url = r.get("url", "")
        if not url or url in seen_urls:
            continue
        snippet = r.get("content", "")
        title = r.get("title", url)
        candidates.append(
            _build_candidate(url, title, snippet, f"tavily:search:{url}", search_by_url)
        )

    if not candidates:
        for r in results[:5]:
            url = r.get("url", "")
            snippet = r.get("content", "")
            candidates.append(
                _build_candidate(url, r.get("title", url), snippet, f"tavily:search:{url}", search_by_url)
            )

    priced = sum(1 for c in candidates if c.get("price_gbp") is not None)
    events = emit_event(
        state,
        "agent_done",
        "Extractor",
        f"Parsed {len(candidates)} candidates ({priced} with prices)",
    )
    return {"candidates": candidates, "tavily_calls": calls, "agent_events": events}
