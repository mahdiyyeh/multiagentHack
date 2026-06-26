from __future__ import annotations

import base64
import json
import re
import time
from typing import Any

from google import genai
from google.genai import types

from backend import config

_client: genai.Client | None = None


def _load_prompt(name: str) -> str:
    path = config.PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def _models_to_try() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for name in [config.GEMINI_MODEL, *config.GEMINI_MODEL_FALLBACKS]:
        if name and name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def _get_client() -> genai.Client:
    global _client
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required")
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _generate_with_fallback(parts: list[Any], *, retries: int = 2) -> str:
    client = _get_client()
    last_error: Exception | None = None
    for model_name in _models_to_try():
        for attempt in range(retries + 1):
            try:
                response = client.models.generate_content(model=model_name, contents=parts)
                text = response.text or ""
                if text:
                    return text
            except Exception as exc:
                last_error = exc
                msg = str(exc)
                if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
                    time.sleep(6 * (attempt + 1))
                    continue
                break
    raise last_error or RuntimeError("Gemini returned empty response")


def _mime_for_bytes(image_bytes: bytes) -> str:
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:2] == b"\xff\xd8":
        return "image/jpeg"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def audit_images(images_b64: list[str], mode: str) -> dict:
    if not images_b64:
        raise ValueError("at least one image is required")
    prompt_name = "audit_venue.md" if mode == "venue" else "audit_home.md"
    prompt = _load_prompt(prompt_name)
    if len(images_b64) > 1:
        prompt = (
            f"{prompt}\n\n"
            f"You are given {len(images_b64)} photos of the same space from different angles. "
            "Synthesize a single holistic audit across all views."
        )
    parts: list[Any] = [types.Part.from_text(text=prompt)]
    for image_b64 in images_b64:
        image_bytes = base64.b64decode(image_b64)
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=_mime_for_bytes(image_bytes)))
    text = _generate_with_fallback(parts)
    return _extract_json(text)


def audit_image(image_b64: str, mode: str) -> dict:
    return audit_images([image_b64], mode)


def plan_queries(flaws: list[dict], mode: str, budget: float, brief: str, broaden: bool) -> list[str]:
    prompt = _load_prompt("planner.md")
    payload = {
        "mode": mode,
        "budget_gbp": budget,
        "brief": brief,
        "broaden_search": broaden,
        "flaws": flaws,
    }
    text = _generate_with_fallback([f"{prompt}\n\nInput:\n{json.dumps(payload)}"])
    data = _extract_json(text)
    return data.get("queries", [])


def rank_candidates(candidates: list[dict], scores: dict, mode: str, brief: str) -> dict:
    prompt = (
        "Rank these procurement candidates. Return JSON only: "
        '{"ranked":[{"url":"...","rank":1,"score":8.5,"why":"...","provenance":["..."]}],'
        '"explanation":"why top beat others"}'
    )
    payload = {"mode": mode, "brief": brief, "scores": scores, "candidates": candidates}
    text = _generate_with_fallback([f"{prompt}\n\n{json.dumps(payload)}"])
    return _extract_json(text)
