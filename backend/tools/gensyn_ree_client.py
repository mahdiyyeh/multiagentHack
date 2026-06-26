from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import httpx

from backend import config

logger = logging.getLogger(__name__)

RECEIPTS_DIR = config.BASE_DIR / "receipts"


def build_canonical(state: dict[str, Any]) -> dict[str, Any]:
    ranked = state.get("ranked", [])[:5]
    images = state.get("images_b64") or ([state.get("image_b64", "")] if state.get("image_b64") else [])
    image_hash = hashlib.sha256("".join(images).encode()).hexdigest()[:16]
    return {
        "audit_version": "1.0",
        "image_hash": image_hash,
        "mode": state.get("mode"),
        "scores": state.get("scores", {}),
        "ranked_shortlist": [
            {"url": c.get("url"), "price_gbp": c.get("price_gbp"), "rank": c.get("rank")}
            for c in ranked
        ],
    }


def _canonical_blob(canonical: dict[str, Any]) -> str:
    return json.dumps(canonical, sort_keys=True)


def _deterministic_receipt(canonical: dict[str, Any], job_id: str = "") -> dict[str, str]:
    blob = _canonical_blob(canonical)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    receipt_id = f"sha256:{digest}"

    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    if job_id:
        receipt_path = RECEIPTS_DIR / f"{job_id}.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "receipt_id": receipt_id,
                    "receipt_type": "deterministic_fallback",
                    "canonical": canonical,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    return {
        "receipt_id": receipt_id,
        "receipt_type": "deterministic_fallback",
        "verify_url": "",
    }


def _hosted_receipt(canonical: dict[str, Any]) -> dict[str, str] | None:
    api_url = (config.GENSYN_REE_API_URL or "").rstrip("/")
    if not api_url or not config.GENSYN_REE_API_KEY:
        return None
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{api_url}/ree/run",
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
            logger.warning("Gensyn hosted REE returned %s: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        logger.warning("Gensyn hosted REE request failed: %s", exc)
    return None


def _local_ree_receipt(canonical: dict[str, Any]) -> dict[str, str] | None:
    repo = Path(config.GENSYN_REE_LOCAL_REPO or "")
    ree_py = repo / "ree.py"
    if not config.GENSYN_REE_USE_LOCAL or not ree_py.is_file():
        return None
    prompt = _canonical_blob(canonical)
    model = config.GENSYN_REE_MODEL
    try:
        proc = subprocess.run(
            [
                "python3",
                str(ree_py),
                "run",
                "--model-name",
                model,
                "--prompt-text",
                prompt,
                "--max-new-tokens",
                "32",
                "--cpu-only",
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if proc.returncode != 0:
            logger.warning("Local Gensyn REE failed: %s", proc.stderr[-500:])
            return None
        for line in proc.stdout.splitlines():
            if "receipt" in line.lower() and line.strip().endswith(".json"):
                receipt_path = Path(line.strip())
                if receipt_path.is_file():
                    data = json.loads(receipt_path.read_text(encoding="utf-8"))
                    receipt_hash = data.get("receipt_hash", "")
                    if receipt_hash:
                        return {
                            "receipt_id": f"ree:{receipt_hash}",
                            "receipt_type": "gensyn_ree_local",
                            "verify_url": str(receipt_path),
                        }
    except Exception as exc:
        logger.warning("Local Gensyn REE subprocess failed: %s", exc)
    return None


def create_receipt(canonical: dict[str, Any], job_id: str = "") -> dict[str, str]:
    hosted = _hosted_receipt(canonical)
    if hosted and hosted.get("receipt_id"):
        return hosted

    local = _local_ree_receipt(canonical)
    if local and local.get("receipt_id"):
        return local

    return _deterministic_receipt(canonical, job_id)


def verify_deterministic_receipt(receipt_path: Path) -> bool:
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    canonical = data.get("canonical", {})
    expected = data.get("receipt_id", "")
    blob = _canonical_blob(canonical)
    digest = f"sha256:{hashlib.sha256(blob.encode()).hexdigest()}"
    return expected == digest
