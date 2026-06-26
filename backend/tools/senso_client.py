from __future__ import annotations

import json
from pathlib import Path

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
    """Senso API with rule-based fallback."""
    if config.SENSO_API_KEY:
        try:
            return _senso_verify(mode, budget, headcount, candidate)
        except Exception:
            pass
    return _rule_verify(mode, budget, headcount, candidate)


def _senso_verify(mode: str, budget: float, headcount: int, candidate: dict) -> dict:
    prompt = (
        f"Ground truth rules:\n{KNOWLEDGE_TEXT}\n\n"
        f"Mode: {mode}. Budget: £{budget}. Headcount: {headcount}.\n"
        f"Extracted text: {candidate.get('raw_extract', '')[:3000]}\n"
        f"Claims: price={candidate.get('price_gbp')}, capacity={candidate.get('capacity')}, url={candidate.get('url')}\n"
        'Return JSON: {"grounded":bool,"issues":[],"confidence":0.0-1.0}'
    )
    headers = {"Authorization": f"Bearer {config.SENSO_API_KEY}", "Content-Type": "application/json"}
    payload = {"query": prompt, "knowledge_base_id": config.SENSO_KB_ID}
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{config.SENSO_API_URL}/query", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    text = data.get("answer") or data.get("response") or json.dumps(data)
    return json.loads(text) if text.strip().startswith("{") else _rule_verify(mode, budget, headcount, candidate)


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
