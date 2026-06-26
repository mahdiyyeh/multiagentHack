from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path

from backend import config
from backend.tools import gemini_client

logger = logging.getLogger(__name__)

VADALOG_TEMPLATE = (Path(__file__).parent / "prometheux_ranking.vadalog").read_text(encoding="utf-8")
CONCEPT_NAME = "spaceraid_rank"

REASON_LABELS = {
    "grounded_under_budget": "Senso-grounded and within budget",
    "grounded": "Senso-verified; composite score leads despite budget pressure",
    "under_budget": "Within budget with strong confidence",
    "over_budget": "Over budget but best available composite score",
}

PROVENANCE_BY_TAG = {
    "grounded_under_budget": ["prometheux:rule:ground_pts", "prometheux:rule:price_pts", "senso:grounded"],
    "grounded": ["prometheux:rule:ground_pts", "prometheux:rule:price_pts", "senso:grounded"],
    "under_budget": ["prometheux:rule:price_pts", "prometheux:rule:conf_pts"],
    "over_budget": ["prometheux:rule:price_pts", "prometheux:rule:conf_pts"],
}


def _token() -> str:
    return config.PMTX_TOKEN or config.PROMETHEUX_API_KEY


def _claims_from_token(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _org_and_user() -> tuple[str, str]:
    org = config.PROMETHEUX_ORG
    user = config.PROMETHEUX_USERNAME
    if org and user:
        return org, user
    claims = _claims_from_token(_token())
    return str(claims.get("organization") or ""), str(claims.get("username") or "")


def _jarvispy_url() -> str:
    if config.PROMETHEUX_JARVISPY_URL:
        return config.PROMETHEUX_JARVISPY_URL.rstrip("/")
    org, user = _org_and_user()
    if org and user:
        return f"https://api.prometheux.ai/jarvispy/{org}/{user}"
    return (config.PROMETHEUX_API_URL or "").rstrip("/")


def _configured() -> bool:
    return bool(_token() and _jarvispy_url() and config.PROMETHEUX_PROJECT_ID)


def _configure_sdk() -> None:
    import prometheux_chain as px

    os.environ["PMTX_TOKEN"] = _token()
    px.config.set("PMTX_TOKEN", _token())
    px.config.set("JARVISPY_URL", _jarvispy_url())


def _esc(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _candidate_facts(candidates: list[dict]) -> list[str]:
    facts: list[str] = []
    for idx, cand in enumerate(candidates):
        url = _esc(str(cand.get("url") or f"candidate-{idx}"))
        price_pence = int(round(float(cand.get("price_gbp") or 0) * 100))
        grounded = 1 if cand.get("grounded") else 0
        confidence = int(round(float(cand.get("confidence") or 0.5) * 100))
        facts.append(f'candidate("{url}", {idx}, {price_pence}, {grounded}, {confidence}).')
    return facts


def _build_definition(candidates: list[dict]) -> str:
    facts = "\n".join(_candidate_facts(candidates))
    return f"{facts}\n\n{VADALOG_TEMPLATE}" if facts else VADALOG_TEMPLATE


def _rows_from_run(data: dict, predicate: str) -> list[list]:
    eval_results = data.get("evaluation_results") or {}
    result_set = eval_results.get("resultSet") or data.get("resultSet") or {}
    rows = result_set.get(predicate)
    if isinstance(rows, list):
        return rows
    return []


def _rows_from_fetch(data: dict) -> list[list]:
    records = data.get("records") or data.get("rows") or data.get("data") or []
    if isinstance(records, list):
        return records
    return []


def _tag_label(tag: str) -> str:
    return REASON_LABELS.get(tag, "Ranked by Prometheux ontology composite score")


def _map_rows(rows: list[list], candidates: list[dict]) -> dict:
    by_url = {str(c.get("url")): c for c in candidates if c.get("url")}
    scored: list[tuple[str, float, str]] = []
    for row in rows:
        if not row:
            continue
        url = str(row[0])
        try:
            score = float(row[1])
        except (TypeError, ValueError, IndexError):
            score = 0.0
        tag = str(row[2]) if len(row) > 2 else "default"
        scored.append((url, score, tag))

    scored.sort(key=lambda item: item[1], reverse=True)
    ranked: list[dict] = []
    for rank_idx, (url, score, tag) in enumerate(scored, start=1):
        base = dict(by_url.get(url, {"url": url}))
        provenance = list(base.get("provenance") or [])
        for item in PROVENANCE_BY_TAG.get(tag, ["prometheux:ontology:spaceraid_rank"]):
            if item not in provenance:
                provenance.append(item)
        ranked.append(
            {
                **base,
                "url": url,
                "rank": rank_idx,
                "score": round(score, 2),
                "why": _tag_label(tag),
                "provenance": provenance,
                "ranked_by_prometheux": True,
            }
        )

    top_tag = scored[0][2] if scored else "default"
    top_label = _tag_label(top_tag)
    explanation = (
        f"Prometheux ontology ranked {len(ranked)} candidates by budget fit, Senso grounding, "
        f"and confidence. Top pick: {top_label}."
    )
    return {
        "ranked": ranked,
        "explanation": explanation,
        "ranked_by_prometheux": True,
        "ranking_engine": "prometheux",
    }


def _run_prometheux(
    candidates: list[dict],
    scores: dict,
    mode: str,
    brief: str,
    budget_gbp: float,
) -> dict | None:
    import prometheux_chain as px

    _configure_sdk()
    project_id = config.PROMETHEUX_PROJECT_ID
    budget_pence = int(round(max(budget_gbp, 0) * 100))
    params = {
        "budget_pence": str(budget_pence),
    }

    definition = _build_definition(candidates)
    px.save_concept(
        project_id=project_id,
        definition=definition,
        concept_name=CONCEPT_NAME,
        description="SpaceRaid explainable procurement ranking",
    )
    run_data = px.run_concept(
        project_id=project_id,
        concept_name=CONCEPT_NAME,
        params=params,
        force_rerun=True,
    )

    rows = _rows_from_run(run_data, "scored")
    if not rows:
        fetch_data = px.fetch_results(
            project_id=project_id,
            output_predicate="scored",
            page=1,
            page_size=max(len(candidates), 10),
        )
        rows = _rows_from_fetch(fetch_data)

    if not rows:
        logger.warning("Prometheux run succeeded but returned no scored rows (scores=%s brief=%s)", scores, brief[:80])
        return None

    return _map_rows(rows, candidates)


def rank(
    candidates: list[dict],
    scores: dict,
    mode: str,
    brief: str,
    budget_gbp: float = 0,
) -> dict:
    if not _configured():
        logger.info("Prometheux not configured — using Gemini ranker fallback")
        result = gemini_client.rank_candidates(candidates, scores, mode, brief)
        result["ranked_by_prometheux"] = False
        result["ranking_engine"] = "gemini_fallback"
        return result

    try:
        result = _run_prometheux(candidates, scores, mode, brief, budget_gbp)
        if result and result.get("ranked"):
            logger.info("Ranked %d candidates via Prometheux ontology", len(result["ranked"]))
            return result
        logger.warning("Prometheux returned empty ranking — falling back to Gemini")
    except Exception as exc:
        logger.warning("Prometheux ranking failed: %s", exc)

    result = gemini_client.rank_candidates(candidates, scores, mode, brief)
    result["ranked_by_prometheux"] = False
    result["ranking_engine"] = "gemini_fallback"
    return result
