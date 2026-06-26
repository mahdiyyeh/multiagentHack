from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import clickhouse_logger, senso_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Groundkeeper", "Verifying claims with Senso ground truth...")
    candidates = list(state.get("candidates", []))
    verified: list[dict] = []
    mode = state.get("mode", "home")
    budget = state.get("budget_gbp", 200)
    headcount = state.get("headcount", 40)

    for cand in candidates[:10]:
        verdict = senso_client.verify_candidate(mode, budget, headcount, cand)
        cand["grounded"] = verdict.get("grounded", False)
        cand["grounding_issues"] = verdict.get("issues", [])
        cand["confidence"] = verdict.get("confidence", 0.0)
        if cand["grounded"]:
            cand.setdefault("provenance", []).append("senso:grounded")
            verified.append(cand)
            clickhouse_logger.log_event(state["job_id"], "Groundkeeper", "grounded", {"url": cand.get("url"), "grounded": True})
        else:
            events = append_log(
                state, "Groundkeeper",
                f"Rejected {cand.get('url', '')}: {', '.join(cand['grounding_issues']) or 'not grounded'}",
            )

    events = emit_event(state, "agent_done", "Groundkeeper", f"{len(verified)} candidates grounded", {"verified": len(verified)})
    return {"candidates": candidates, "verified": verified, "agent_events": events}
