from backend import config
from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import prometheux_client


def run(state: RaidState) -> dict:
    engine = "Prometheux ontology" if config.PROMETHEUX_PROJECT_ID and config.PMTX_TOKEN else "provenance rules"
    events = emit_event(state, "agent_start", "Ranker", f"Ranking candidates via {engine}...")
    pool = state.get("verified") if state.get("verified") else state.get("candidates", [])
    if not pool:
        events = emit_event(state, "agent_done", "Ranker", "No candidates to rank")
        return {"ranked": [], "ranking_explanation": "No candidates found.", "agent_events": events}

    result = prometheux_client.rank(
        pool,
        state.get("scores", {}),
        state.get("mode", "home"),
        state.get("brief", ""),
        float(state.get("budget_gbp") or 0),
    )
    ranked_by_prometheux = bool(result.get("ranked_by_prometheux"))
    ranked_raw = result.get("ranked", [])
    by_url = {c.get("url"): c for c in pool if c.get("url")}
    ranked: list[dict] = []
    for item in ranked_raw:
        url = item.get("url")
        base = dict(by_url.get(url, item))
        base.update(item)
        ranked.append(base)
    if not ranked:
        ranked = [dict(c) for c in pool[:3]]
        for i, c in enumerate(ranked):
            c["rank"] = i + 1
            c.setdefault("why", "Best available grounded option")
            c.setdefault("provenance", c.get("provenance", []))
    explanation = result.get("explanation", "Ranked by value, grounding, and audit fit.")
    if ranked_by_prometheux:
        explanation = f"[Prometheux] {explanation}"
    events = append_log(state, "Ranker", explanation)
    events = emit_event(
        state,
        "agent_done",
        "Ranker",
        explanation,
        {"ranked": ranked[:3], "ranked_by_prometheux": ranked_by_prometheux},
    )
    return {"ranked": ranked, "ranking_explanation": explanation, "agent_events": events}
