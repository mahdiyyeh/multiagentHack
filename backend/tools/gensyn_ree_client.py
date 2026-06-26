from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx

from backend import config


def create_receipt(canonical: dict[str, Any]) -> dict[str, str]:
    blob = json.dumps(canonical, sort_keys=True)
    if config.GENSYN_REE_API_KEY:
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    "https://api.gensyn.ai/ree/run",
                    headers={"Authorization": f"Bearer {config.GENSYN_REE_API_KEY}"},
                    json={"input": canonical},
                )
                if resp.status_code < 400:
                    data = resp.json()
                    return {
                        "receipt_id": data.get("receipt_id", ""),
                        "receipt_type": "gensyn_ree",
                        "verify_url": data.get("verify_url", ""),
                    }
        except Exception:
            pass

    digest = hashlib.sha256(blob.encode()).hexdigest()
    return {
        "receipt_id": f"sha256:{digest}",
        "receipt_type": "deterministic_fallback",
        "verify_url": "",
    }
