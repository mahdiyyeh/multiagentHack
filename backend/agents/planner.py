import re

from backend import config
from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import gemini_client


def _parse_headcount(brief: str) -> int:
    match = re.search(r"(\d+)\s*(people|guests|pax|delegates)", brief, re.I)
    return int(match.group(1)) if match else 40


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Planner", "Decomposing flaws into search strategies...")
    flaws = state.get("flaws", [])
    broaden = state.get("broaden_search", False)
    budget = state.get("budget_gbp", 200)
    if broaden:
        budget = round(budget * 1.2, 2)

    try:
        queries = gemini_client.plan_queries(
            flaws, state.get("mode", "home"), budget, state.get("brief", ""), broaden
        )
    except Exception:
        queries = []
        for flaw in flaws:
            intent = flaw.get("search_intent", flaw.get("flaw", "room upgrade UK"))
            queries.append(f"{intent} under £{budget} UK")
            if not broaden:
                domains = config.VENUE_DOMAINS if state.get("mode") == "venue" else config.HOME_DOMAINS
                queries.append(f"{intent} site:{domains[0]}")

    queries = queries[:6]
    events = append_log(state, "Planner", f"Generated {len(queries)} search queries", {"queries": queries})
    events = emit_event(state, "agent_done", "Planner", f"{len(queries)} queries ready")

    return {
        "search_queries": queries,
        "budget_gbp": budget,
        "headcount": _parse_headcount(state.get("brief", "")),
        "broaden_search": False,
        "agent_events": events,
    }
