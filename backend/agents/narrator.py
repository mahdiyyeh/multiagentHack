from backend.events import emit_event
from backend.state import RaidState
from backend.tools import elevenlabs_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Narrator", "Generating voice summary...")
    scores = state.get("scores", {})
    light = scores.get("natural_light", "?")
    total = state.get("total_gbp", 0)
    ranked = state.get("ranked", [])
    grounded = [c for c in ranked if c.get("grounded")]
    count = len(grounded) if grounded else len(ranked)
    mode = state.get("mode", "home")
    item_word = "upgrades" if mode == "home" else "venues"
    qualifier = "Senso-verified" if grounded else "ranked"

    text = (
        f"SpaceRaid complete. Your space scores {light} out of 10 on natural light. "
        f"I found {count} {qualifier} {item_word}"
    )
    if total > 0:
        text += f" totalling £{total:.0f}."
    else:
        text += "."

    audio = elevenlabs_client.synthesize(text)
    events = emit_event(state, "agent_done", "Narrator", "Audio summary ready")
    return {
        "audio_b64": audio.get("audio_b64", ""),
        "audio_fallback_text": audio.get("fallback_text", text),
        "agent_events": events,
    }
