from __future__ import annotations

import json
import re

import httpx

from backend import config

KNOWLEDGE_TEXT = "\n\n".join(
    (config.KNOWLEDGE_DIR / name).read_text(encoding="utf-8")
    for name in ["scoring_rubric.md", "home_procurement_rules.md", "venue_procurement_rules.md"]
    if (config.KNOWLEDGE_DIR / name).exists()
)


def verify_candidate(
    mode: str,
    budget: float,
    headcount: int,
    candidate: dict,
) -> dict:
    """Senso KB search with rule-based fallback."""
    if config.SENSO_API_KEY:
        try:
            return _senso_verify(mode, budget, headcount, candidate)
        except Exception:
            pass
    return _rule_verify(mode, budget, headcount, candidate)


def _senso_base_url() -> str:
    return (config.SENSO_API_URL or "https://apiv2.senso.ai/api/v1").rstrip("/")


def _parse_verdict(text: str) -> dict | None:
    text = (text or "").strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    match = re.search(r'\{[^{}]*"grounded"\s*:\s*(?:true|false)[^{}]*\}', text, re.I | re.S)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def _senso_verify(mode: str, budget: float, headcount: int, candidate: dict) -> dict:
    prompt = (
        "Apply the procurement ground truth rules from the knowledge base.\n"
        f"Mode: {mode}. Budget: £{budget}. Headcount: {headcount}.\n"
        f"URL: {candidate.get('url')}\n"
        f"Extracted page text:\n{(candidate.get('raw_extract') or '')[:2500]}\n"
        f"Parsed claims: price_gbp={candidate.get('price_gbp')}, capacity={candidate.get('capacity')}\n"
        "Decide if this candidate is grounded. Return ONLY valid JSON with keys: "
        'grounded (bool), issues (string array), confidence (0.0-1.0).'
    )
    headers = {
        "X-API-Key": config.SENSO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=45) as client:
        resp = client.post(
            f"{_senso_base_url()}/org/search",
            headers=headers,
            json={"query": prompt, "max_results": 5},
        )
        resp.raise_for_status()
        data = resp.json()

    verdict = _parse_verdict(data.get("answer") or "")
    if not verdict or "grounded" not in verdict:
        return _rule_verify(mode, budget, headcount, candidate)

    return {
        "grounded": bool(verdict.get("grounded")),
        "issues": list(verdict.get("issues") or []),
        "confidence": float(verdict.get("confidence", 0.8)),
    }


def _rule_verify(mode: str, budget: float, headcount: int, candidate: dict) -> dict:
    issues: list[str] = []
    raw = (candidate.get("raw_extract") or "").lower()
    price = candidate.get("price_gbp")
    capacity = candidate.get("capacity")

    if mode == "home":
        if price is None:
            issues.append("price_not_in_extract")
        elif price > budget:
            issues.append("over_budget")
        if price is not None and f"£{int(price)}" not in raw and f"£{price:.2f}" not in raw:
            issues.append("price_not_in_extract")
    else:
        if capacity is None:
            issues.append("capacity_not_in_extract")
        elif headcount and capacity < headcount:
            issues.append("under_capacity")
        if price is not None and price > budget:
            issues.append("over_budget")

    grounded = len(issues) == 0
    return {"grounded": grounded, "issues": issues, "confidence": 0.9 if grounded else 0.4}
