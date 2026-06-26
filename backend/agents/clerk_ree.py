from backend.events import emit_event
from backend.state import RaidState
from backend.tools import gensyn_ree_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Clerk", "Generating verifiable receipt...")
    canonical = gensyn_ree_client.build_canonical(state)
    receipt = gensyn_ree_client.create_receipt(canonical, state.get("job_id", ""))
    events = emit_event(
        state, "agent_done", "Clerk",
        f"Receipt: {receipt['receipt_id'][:32]}...",
        receipt,
    )
    return {
        "receipt_id": receipt["receipt_id"],
        "receipt_type": receipt["receipt_type"],
        "agent_events": events,
    }
