from __future__ import annotations

import base64

import httpx

from backend import config


def synthesize(text: str) -> dict:
    if not config.ELEVENLABS_API_KEY:
        return {"audio_b64": "", "fallback_text": text}
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",
                headers={
                    "xi-api-key": config.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={"text": text, "model_id": "eleven_monolingual_v1"},
            )
            resp.raise_for_status()
            return {"audio_b64": base64.b64encode(resp.content).decode(), "fallback_text": text}
    except Exception:
        return {"audio_b64": "", "fallback_text": text}
