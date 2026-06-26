from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx

from backend import config


_in_memory: dict[str, list[dict[str, Any]]] = {}


def log_event(job_id: str, agent: str, event_type: str, payload: dict[str, Any]) -> None:
    row = {
        "job_id": job_id,
        "agent": agent,
        "event_type": event_type,
        **payload,
    }
    _in_memory.setdefault(job_id, []).append(row)

    if not config.CLICKHOUSE_HOST:
        return
    try:
        import clickhouse_connect

        client = clickhouse_connect.get_client(
            host=config.CLICKHOUSE_HOST,
            username=config.CLICKHOUSE_USER,
            password=config.CLICKHOUSE_PASSWORD,
            database=config.CLICKHOUSE_DATABASE,
        )
        client.insert(
            "agent_events",
            [[job_id, agent, event_type, json.dumps(payload)]],
            column_names=["job_id", "agent", "event_type", "payload"],
        )
    except Exception:
        pass


def get_dashboard(job_id: str) -> dict[str, Any]:
    rows = _in_memory.get(job_id, [])
    searches = sum(1 for r in rows if r.get("event_type") == "search")
    extracts = sum(1 for r in rows if r.get("event_type") == "extract")
    grounded = sum(1 for r in rows if r.get("grounded") is True)
    return {
        "total_searches": searches,
        "total_extracts": extracts,
        "total_grounded": grounded,
        "total_events": len(rows),
    }


def export_events(job_id: str) -> list[dict[str, Any]]:
    return _in_memory.get(job_id, [])
