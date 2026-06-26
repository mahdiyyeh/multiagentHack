from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.state import AgentEvent, RaidState


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_event(
    state: RaidState,
    event_type: str,
    agent: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> list[AgentEvent]:
    event: AgentEvent = {
        "type": event_type,
        "agent": agent,
        "message": message,
        "data": data or {},
        "ts": utc_now(),
    }
    events = list(state.get("agent_events", []))
    events.append(event)
    return events


def append_log(state: RaidState, agent: str, message: str, data: dict[str, Any] | None = None) -> list[AgentEvent]:
    return emit_event(state, "agent_log", agent, message, data)
