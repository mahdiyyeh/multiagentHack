import re

from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import clickhouse_logger, gemini_client


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

    flaws = sorted(result.get("flaws", []), key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f.get("severity", "low"), 2))
    flaws = flaws[:3]

    summary = ", ".join(f"{k} {v}/10" for k, v in list(result.get("scores", {}).items())[:3])
    events = emit_event(state, "agent_done", "Auditor", f"Audit complete: {summary}", {"scores": result.get("scores")})
    clickhouse_logger.log_event(state["job_id"], "Auditor", "done", {"scores": result.get("scores")})

    return {
        "scores": result.get("scores", {}),
        "score_evidence": result.get("score_evidence", {}),
        "flaws": flaws,
        "agent_events": events,
    }
