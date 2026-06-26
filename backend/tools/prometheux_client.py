from __future__ import annotations

import httpx

from backend import config
from backend.tools import gemini_client


def rank(candidates: list[dict], scores: dict, mode: str, brief: str) -> dict:
    if config.PROMETHEUX_API_KEY and config.PROMETHEUX_API_URL:
        try:
            with httpx.Client(timeout=45) as client:
                resp = client.post(
                    f"{config.PROMETHEUX_API_URL}/rank",
                    headers={"Authorization": f"Bearer {config.PROMETHEUX_API_KEY}"},
                    json={
                        "ontology_id": config.PROMETHEUX_ONTOLOGY_ID,
                        "candidates": candidates,
                        "scores": scores,
                        "mode": mode,
                        "brief": brief,
                    },
                )
                if resp.status_code < 400:
                    return resp.json()
        except Exception:
            pass
    return gemini_client.rank_candidates(candidates, scores, mode, brief)
