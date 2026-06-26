from backend.events import emit_event
from backend.state import RaidState
from backend.tools import elevenlabs_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Narrator", "Generating voice summary...")
    scores = state.get("scores", {})
    light = scores.get("natural_light", "?")
    total = state.get("total_gbp", 0)
    count = len(state.get("ranked", []))
    mode = state.get("mode", "home")
    text = (
        f"SpaceRaid complete. Your space scores {light} out of 10 on natural light. "
        f"I found {count} verified {'upgrades' if mode == 'home' else 'venues'} totalling £{total:.0f}."
    )
    audio = elevenlabs_client.synthesize(text)
    events = emit_event(state, "agent_done", "Narrator", "Audio summary ready")
    return {
        "audio_b64": audio.get("audio_b64", ""),
        "audio_fallback_text": audio.get("fallback_text", text),
        "agent_events": events,
    }
