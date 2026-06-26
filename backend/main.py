from __future__ import annotations

import asyncio
import base64
import uuid
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from backend.graph import run_raid
from backend.state import RaidState
from backend.tools import clickhouse_logger

app = FastAPI(title="SpaceRaid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: dict[str, dict[str, Any]] = {}
_job_queues: dict[str, asyncio.Queue] = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "spaceraid"}


MAX_IMAGES = 10


@app.post("/api/raid")
async def start_raid(
    images: list[UploadFile] = File(...),
    mode: str = Form("home"),
    budget: float = Form(200.0),
    brief: str = Form(""),
):
    if not images:
        return {"error": "at least one image is required"}
    if len(images) > MAX_IMAGES:
        return {"error": f"maximum {MAX_IMAGES} images allowed"}

    job_id = str(uuid.uuid4())
    images_b64: list[str] = []
    for upload in images:
        content = await upload.read()
        if not content:
            continue
        images_b64.append(base64.b64encode(content).decode())

    if not images_b64:
        return {"error": "no valid image data received"}

    initial: RaidState = {
        "job_id": job_id,
        "mode": "venue" if mode == "venue" else "home",
        "image_b64": images_b64[0],
        "images_b64": images_b64,
        "budget_gbp": budget,
        "brief": brief,
        "replan_count": 0,
        "broaden_search": False,
        "tavily_calls": 0,
        "agent_events": [],
    }

    queue: asyncio.Queue = asyncio.Queue()
    _job_queues[job_id] = queue
    _jobs[job_id] = {"status": "running", "report": None}

    asyncio.create_task(_run_job(job_id, initial, queue))
    return {"job_id": job_id}


async def _run_job(job_id: str, initial: RaidState, queue: asyncio.Queue):
    try:
        last_len = 0

        def stream_invoke():
            nonlocal last_len
            state = initial
            app_graph = __import__("backend.graph", fromlist=["build_graph"]).build_graph()
            for step in app_graph.stream(state):
                for _node, update in step.items():
                    state = {**state, **update}
                    events = state.get("agent_events", [])
                    for ev in events[last_len:]:
                        queue.put_nowait(ev)
                        clickhouse_logger.log_event(
                            job_id, ev.get("agent", ""), ev.get("type", "log"), ev.get("data", {})
                        )
                    last_len = len(events)
            return state

        final = await asyncio.to_thread(stream_invoke)
        report = final.get("final_report", {})
        _jobs[job_id] = {"status": "complete", "report": report}
        await queue.put({"type": "complete", "report": report})
    except Exception as exc:
        _jobs[job_id] = {"status": "error", "error": str(exc)}
        await queue.put({"type": "error", "message": str(exc)})
    finally:
        await queue.put(None)


@app.get("/api/raid/stream/{job_id}")
async def stream_raid(job_id: str):
    queue = _job_queues.get(job_id)
    if not queue:
        return {"error": "job not found"}

    async def event_generator():
        while True:
            item = await queue.get()
            if item is None:
                break
            yield {"event": "message", "data": __import__("json").dumps(item)}

    return EventSourceResponse(event_generator())


@app.get("/api/raid/status/{job_id}")
def raid_status(job_id: str):
    return _jobs.get(job_id, {"error": "not found"})


@app.get("/api/dashboard/{job_id}")
def dashboard(job_id: str):
    return clickhouse_logger.get_dashboard(job_id)
