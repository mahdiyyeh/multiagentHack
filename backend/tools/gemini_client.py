from __future__ import annotations

import json
import re
from pathlib import Path

import google.generativeai as genai

from backend import config


def _load_prompt(name: str) -> str:
    path = config.PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def configure() -> None:
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required")
    genai.configure(api_key=config.GEMINI_API_KEY)


def audit_image(image_b64: str, mode: str) -> dict:
    configure()
    prompt_name = "audit_venue.md" if mode == "venue" else "audit_home.md"
    prompt = _load_prompt(prompt_name)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    image_part = {"mime_type": "image/jpeg", "data": __import__("base64").b64decode(image_b64)}
    response = model.generate_content([prompt, image_part])
    return _extract_json(response.text or "{}")


def plan_queries(flaws: list[dict], mode: str, budget: float, brief: str, broaden: bool) -> list[str]:
    configure()
    prompt = _load_prompt("planner.md")
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    payload = {
        "mode": mode,
        "budget_gbp": budget,
        "brief": brief,
        "broaden_search": broaden,
        "flaws": flaws,
    }
    response = model.generate_content(f"{prompt}\n\nInput:\n{json.dumps(payload)}")
    data = _extract_json(response.text or "{}")
    return data.get("queries", [])


def rank_candidates(candidates: list[dict], scores: dict, mode: str, brief: str) -> dict:
    configure()
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    prompt = (
        "Rank these procurement candidates. Return JSON only: "
        '{"ranked":[{"url":"...","rank":1,"score":8.5,"why":"...","provenance":["..."]}],'
        '"explanation":"why top beat others"}'
    )
    payload = {"mode": mode, "brief": brief, "scores": scores, "candidates": candidates}
    response = model.generate_content(f"{prompt}\n\n{json.dumps(payload)}")
    return _extract_json(response.text or "{}")
