import re

from backend.events import append_log, emit_event
from backend.state import RaidState, ScoreEvidence
from backend.tools import clickhouse_logger, gemini_client


def _normalize_score_evidence(raw: dict, scores: dict[str, int]) -> dict[str, ScoreEvidence]:
    normalized: dict[str, ScoreEvidence] = {}
    for dim, score in scores.items():
        entry = raw.get(dim, {})
        if isinstance(entry, str):
            entry = {"because": entry.strip(), "improvement": ""}
        elif not isinstance(entry, dict):
            entry = {}
        because = str(entry.get("because", "")).strip()
        improvement = str(entry.get("improvement", "")).strip()
        if not because:
            because = f"Visual audit supports {score}/10 on {dim.replace('_', ' ')} from the uploaded photo(s)."
        normalized[dim] = {"because": because, "improvement": improvement}
    return normalized


def run(state: RaidState) -> dict:
    images_b64 = state.get("images_b64") or ([state["image_b64"]] if state.get("image_b64") else [])
    count = len(images_b64)
    msg = f"Analyzing {count} photo{'s' if count != 1 else ''} with Gemini vision..."
    events = emit_event(state, "agent_start", "Auditor", msg)
    clickhouse_logger.log_event(state["job_id"], "Auditor", "start", {"image_count": count})

    try:
        result = gemini_client.audit_images(images_b64, state.get("mode", "home"))
    except Exception as exc:
        events = append_log(state, "Auditor", f"Audit failed: {exc}")
        return {"agent_events": events, "error": str(exc)}

    scores = result.get("scores", {})
    score_evidence = _normalize_score_evidence(result.get("score_evidence", {}), scores)

    flaws = sorted(result.get("flaws", []), key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f.get("severity", "low"), 2))
    flaws = flaws[:3]

    summary = ", ".join(f"{k} {v}/10" for k, v in list(scores.items())[:3])
    events = emit_event(
        state,
        "agent_done",
        "Auditor",
        f"Audit complete: {summary}",
        {"scores": scores, "score_evidence": score_evidence},
    )
    clickhouse_logger.log_event(state["job_id"], "Auditor", "done", {"scores": scores, "score_evidence": score_evidence})

    return {
        "scores": scores,
        "score_evidence": score_evidence,
        "flaws": flaws,
        "agent_events": events,
    }
