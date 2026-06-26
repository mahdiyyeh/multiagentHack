from backend.events import emit_event
from backend.state import RaidState


def run(state: RaidState) -> dict:
    report = {
        "scores": state.get("scores", {}),
        "score_evidence": state.get("score_evidence", {}),
        "flaws": state.get("flaws", []),
        "candidates": state.get("candidates", []),
        "verified": state.get("verified", []),
        "ranked": state.get("ranked", []),
        "manifest": state.get("manifest", {}),
        "total_gbp": state.get("total_gbp", 0),
        "replan_count": state.get("replan_count", 0),
        "ranking_explanation": state.get("ranking_explanation", ""),
        "receipt_id": state.get("receipt_id", ""),
        "receipt_type": state.get("receipt_type", ""),
        "twilio_sent": state.get("twilio_sent", False),
        "mailto_link": state.get("mailto_link", ""),
        "audio_b64": state.get("audio_b64", ""),
        "audio_fallback_text": state.get("audio_fallback_text", ""),
        "mode": state.get("mode", "home"),
        "agent_trace": state.get("agent_events", []),
    }
    events = emit_event(state, "agent_done", "Reporter", "Final report ready", {"report": report})
    return {"final_report": report, "agent_events": events}
