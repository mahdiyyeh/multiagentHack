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


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Extractor", "Extracting prices and specs from pages...")
    results = state.get("search_results", [])
    urls = [r.get("url") for r in results if r.get("url")][:8]
    calls = state.get("tavily_calls", 0)
    candidates: list[dict] = []

    if urls:
        events = append_log(state, "Extractor", f"Extracting {len(urls)} URLs")
        try:
            extracted = tavily_client.extract(urls)
            calls += 1
            clickhouse_logger.log_event(state["job_id"], "Extractor", "extract", {"count": len(extracted)})
            for item in extracted:
                raw = item.get("raw_content") or item.get("content") or ""
                url = item.get("url", "")
                title = item.get("title", url)
                candidates.append({
                    "url": url,
                    "title": title,
                    "price_gbp": _parse_price(raw),
                    "capacity": _parse_capacity(raw),
                    "raw_extract": raw[:4000],
                    "grounded": False,
                    "grounding_issues": [],
                    "confidence": 0.0,
                    "provenance": [f"tavily:extract:{url}"],
                })
        except Exception as exc:
            events = append_log(state, "Extractor", f"Extract failed: {exc}")

    if not candidates:
        for r in results[:5]:
            snippet = r.get("content", "")
            candidates.append({
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "price_gbp": _parse_price(snippet),
                "capacity": _parse_capacity(snippet),
                "raw_extract": snippet,
                "grounded": False,
                "grounding_issues": [],
                "confidence": 0.0,
                "provenance": [f"tavily:search:{r.get('url', '')}"],
            })

    events = emit_event(state, "agent_done", "Extractor", f"Parsed {len(candidates)} candidates")
    return {"candidates": candidates, "tavily_calls": calls, "agent_events": events}
