from __future__ import annotations

from typing import Any, Literal, TypedDict


class Flaw(TypedDict, total=False):
    zone_id: int
    bbox_pct: list[float]
    severity: str
    search_intent: str
    pro: str
    con: str
    flaw: str


class Candidate(TypedDict, total=False):
    url: str
    title: str
    price_gbp: float | None
    capacity: int | None
    raw_extract: str
    flaw_id: int
    grounded: bool
    grounding_issues: list[str]
    confidence: float
    rank: int
    why: str
    provenance: list[str]


class AgentEvent(TypedDict, total=False):
    type: str
    agent: str
    message: str
    data: dict[str, Any]
    ts: str


class RaidState(TypedDict, total=False):
    job_id: str
    mode: Literal["home", "venue"]
    image_b64: str
    budget_gbp: float
    brief: str
    headcount: int
    scores: dict[str, int]
    score_evidence: dict[str, str]
    flaws: list[Flaw]
    search_queries: list[str]
    search_results: list[dict[str, Any]]
    candidates: list[Candidate]
    verified: list[Candidate]
    ranked: list[Candidate]
    replan_count: int
    broaden_search: bool
    tavily_calls: int
    skeptic_action: str
    ranking_explanation: str
    receipt_id: str
    receipt_type: str
    manifest: dict[str, Any]
    total_gbp: float
    twilio_sent: bool
    mailto_link: str
    audio_b64: str
    audio_fallback_text: str
    agent_events: list[AgentEvent]
    final_report: dict[str, Any]
    error: str
