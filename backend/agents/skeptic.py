from backend import config
from backend.events import append_log, emit_event
from backend.state import RaidState


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Skeptic", "Checking if enough viable candidates...")
    verified = state.get("verified", [])
    replan_count = state.get("replan_count", 0)
    min_needed = 2

    if len(verified) >= min_needed:
        events = emit_event(state, "agent_done", "Skeptic", f"{len(verified)} candidates pass — proceeding")
        return {"skeptic_action": "proceed", "agent_events": events}

    if replan_count < config.MAX_REPLANS:
        replan_count += 1
        msg = f"Only {len(verified)} viable — broadening search (replan {replan_count}/{config.MAX_REPLANS})"
        events = append_log(state, "Skeptic", msg)
        events = emit_event(state, "agent_done", "Skeptic", msg)
        return {
            "replan_count": replan_count,
            "broaden_search": True,
            "skeptic_action": "replan",
            "search_results": [],
            "candidates": [],
            "verified": [],
            "agent_events": events,
        }

    events = emit_event(state, "agent_done", "Skeptic", "Proceeding with available candidates")
    return {"skeptic_action": "proceed", "agent_events": events}
