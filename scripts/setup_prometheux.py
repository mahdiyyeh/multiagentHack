#!/usr/bin/env python3
"""Bootstrap Prometheux project + ranking ontology for SpaceRaid.

Prerequisites:
  1. Sign up at https://platform.prometheux.ai/login
  2. Copy your API token from Settings → API Keys → PMTX_TOKEN
  3. Optional: PROMETHEUX_ORG / PROMETHEUX_USERNAME (auto-read from JWT if omitted)

Usage:
  source .venv/bin/activate
  python scripts/setup_prometheux.py
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def _claims_from_token(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Missing {name}. Add it to .env and retry.", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    token = _require("PMTX_TOKEN") if os.getenv("PMTX_TOKEN") else _require("PROMETHEUX_API_KEY")
    claims = _claims_from_token(token)
    org = os.getenv("PROMETHEUX_ORG", "").strip() or str(claims.get("organization") or "")
    username = os.getenv("PROMETHEUX_USERNAME", "").strip() or str(claims.get("username") or "")
    if not org or not username:
        print("Could not resolve org/username. Set PROMETHEUX_ORG and PROMETHEUX_USERNAME in .env.", file=sys.stderr)
        sys.exit(1)
    print(f"Using org={org} username={username}")

    os.environ["PMTX_TOKEN"] = token

    import prometheux_chain as px

    jarvis_url = os.getenv("PROMETHEUX_JARVISPY_URL") or f"https://api.prometheux.ai/jarvispy/{org}/{username}"
    px.config.set("PMTX_TOKEN", token)
    px.config.set("JARVISPY_URL", jarvis_url.rstrip("/"))

    existing = os.getenv("PROMETHEUX_PROJECT_ID", "").strip()
    if existing:
        project_id = existing
        print(f"Using existing project: {project_id}")
    else:
        project_id = px.save_project(
            project_name="spaceraid-ranker",
            description="SpaceRaid explainable procurement ranking ontology",
        )
        print(f"Created project: {project_id}")
        print(f"\nAdd to .env:\nPROMETHEUX_PROJECT_ID={project_id}")

    vadalog = (ROOT / "backend" / "tools" / "prometheux_ranking.vadalog").read_text(encoding="utf-8")
    sample_facts = (
        'candidate("https://example.com/a", 0, 4500, 1, 90).\n'
        'candidate("https://example.com/b", 1, 12000, 0, 50).\n\n'
    )
    try:
        px.save_concept(
            project_id=project_id,
            definition=sample_facts + vadalog,
            concept_name="spaceraid_rank",
            description="SpaceRaid explainable procurement ranking",
        )
        print("Saved concept: spaceraid_rank")
    except Exception as exc:
        if "already exists" in str(exc) or "409" in str(exc):
            print("Concept spaceraid_rank already exists — continuing.")
        else:
            raise

    try:
        smoke = px.run_concept(
            project_id=project_id,
            concept_name="spaceraid_rank",
            params={"budget_pence": "5000"},
            force_rerun=True,
        )
        rows = (smoke.get("evaluation_results") or {}).get("resultSet", {}).get("scored", [])
        print(f"Smoke test: {len(rows)} scored row(s)")
        if rows:
            print("Sample:", rows[0])
        print("\nPrometheux ready. Restart ./run_backend.sh and run a raid.")
    except Exception as exc:
        msg = str(exc)
        if "NO_ACTIVE_COMPUTE" in msg or "No active compute" in msg:
            print("\nConcept saved, but smoke test needs compute.")
            print("In Prometheux: Manage → Compute → start a machine, then re-run:")
            print("  python scripts/setup_prometheux.py")
            print("\nProject ID is already in .env — ranking will work once compute is running.")
        else:
            raise

    env_path = ROOT / ".env"
    if env_path.is_file() and not existing:
        text = env_path.read_text(encoding="utf-8")
        if "PROMETHEUX_PROJECT_ID=" not in text:
            with env_path.open("a", encoding="utf-8") as fh:
                fh.write(f"\nPROMETHEUX_PROJECT_ID={project_id}\n")
            print(f"Appended PROMETHEUX_PROJECT_ID to {env_path}")


if __name__ == "__main__":
    main()
