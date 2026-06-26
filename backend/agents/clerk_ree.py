import hashlib

from backend.events import emit_event
from backend.state import RaidState
from backend.tools import gensyn_ree_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Clerk", "Generating verifiable receipt...")
    ranked = state.get("ranked", [])[:5]
    image_hash = hashlib.sha256(state.get("image_b64", "").encode()).hexdigest()[:16]
    canonical = {
        "audit_version": "1.0",
        "image_hash": image_hash,
        "mode": state.get("mode"),
        "scores": state.get("scores", {}),
        "ranked_shortlist": [
            {"url": c.get("url"), "price_gbp": c.get("price_gbp"), "rank": c.get("rank")}
            for c in ranked
        ],
    }
    receipt = gensyn_ree_client.create_receipt(canonical)
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
