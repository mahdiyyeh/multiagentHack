from __future__ import annotations

from typing import Any, Callable

from langgraph.graph import END, StateGraph

from backend.agents import (
    actor,
    auditor,
    clerk_ree,
    extractor,
    groundkeeper,
    narrator,
    planner,
    ranker,
    reporter,
    scout,
    skeptic,
)
from backend.state import RaidState


def _merge_events(state: RaidState, update: dict) -> dict:
    if "agent_events" in update:
        prior = state.get("agent_events", [])
        new = update["agent_events"]
        if new and prior and new[0] in prior:
            update = {**update, "agent_events": prior + new[len(prior) :]}
        elif new and not prior:
            pass
        elif new:
            update = {**update, "agent_events": prior + new}
    return update


def _wrap(fn: Callable[[RaidState], dict]):
    def node(state: RaidState) -> dict:
        update = fn(state)
        return _merge_events(state, update)
    return node


def _after_skeptic(state: RaidState) -> str:
    if state.get("skeptic_action") == "replan":
        return "planner"
    return "ranker"


def build_graph():
    graph = StateGraph(RaidState)
    graph.add_node("auditor", _wrap(auditor.run))
    graph.add_node("planner", _wrap(planner.run))
    graph.add_node("scout", _wrap(scout.run))
    graph.add_node("extractor", _wrap(extractor.run))
    graph.add_node("groundkeeper", _wrap(groundkeeper.run))
    graph.add_node("skeptic", _wrap(skeptic.run))
    graph.add_node("ranker", _wrap(ranker.run))
    graph.add_node("clerk", _wrap(clerk_ree.run))
    graph.add_node("actor", _wrap(actor.run))
    graph.add_node("narrator", _wrap(narrator.run))
    graph.add_node("reporter", _wrap(reporter.run))

    graph.set_entry_point("auditor")
    graph.add_edge("auditor", "planner")
    graph.add_edge("planner", "scout")
    graph.add_edge("scout", "extractor")
    graph.add_edge("extractor", "groundkeeper")
    graph.add_edge("groundkeeper", "skeptic")
    graph.add_conditional_edges("skeptic", _after_skeptic, {"planner": "planner", "ranker": "ranker"})
    graph.add_edge("ranker", "clerk")
    graph.add_edge("clerk", "actor")
    graph.add_edge("actor", "narrator")
    graph.add_edge("narrator", "reporter")
    graph.add_edge("reporter", END)
    return graph.compile()


def run_raid(initial: RaidState) -> RaidState:
    app = build_graph()
    result = app.invoke(initial)
    return result
