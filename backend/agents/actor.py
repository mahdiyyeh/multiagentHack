from backend.events import append_log, emit_event
from backend.state import RaidState
from backend.tools import twilio_client


def run(state: RaidState) -> dict:
    events = emit_event(state, "agent_start", "Actor", "Taking real-world action...")
    mode = state.get("mode", "home")
    ranked = state.get("ranked", [])[:3]
    total = sum(c.get("price_gbp") or 0 for c in ranked)
    twilio_sent = False
    mailto_link = ""

    if mode == "home":
        manifest = {
            "items": [
                {"title": c.get("title"), "url": c.get("url"), "price_gbp": c.get("price_gbp"), "rank": c.get("rank")}
                for c in ranked
            ],
            "total_gbp": round(total, 2),
        }
        events = emit_event(state, "agent_done", "Actor", f"Buy manifest: £{manifest['total_gbp']:.0f} across {len(ranked)} items")
        return {"manifest": manifest, "total_gbp": manifest["total_gbp"], "twilio_sent": False, "agent_events": events}

    top = ranked[0] if ranked else {}
    subject = f"Venue enquiry — {state.get('brief', 'event space')[:60]}"
    body = (
        f"Hello,\n\nWe are interested in your space: {top.get('title', 'venue')}\n"
        f"URL: {top.get('url', '')}\n"
        f"Brief: {state.get('brief', '')}\n"
        f"Budget: £{state.get('budget_gbp', 0)}\n\n"
        "Please confirm availability and pricing.\n\nSpaceRaid autonomous agent"
    )
    result = twilio_client.send_enquiry(body)
    twilio_sent = result.get("twilio_sent", False)
    mailto_link = twilio_client.build_mailto(subject, body)
    if twilio_sent:
        events = append_log(state, "Actor", "Twilio: enquiry SMS sent to sandbox")
    else:
        events = append_log(state, "Actor", "mailto: enquiry link generated")
    events = emit_event(state, "agent_done", "Actor", "Venue enquiry action complete")
    return {
        "manifest": {"enquiry": body, "top_venue": top},
        "total_gbp": top.get("price_gbp") or 0,
        "twilio_sent": twilio_sent,
        "mailto_link": mailto_link,
        "agent_events": events,
    }
