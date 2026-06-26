#!/usr/bin/env python3
"""Verify a SpaceRaid deterministic receipt saved under receipts/."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.tools.gensyn_ree_client import verify_deterministic_receipt  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a SpaceRaid receipt JSON file")
    parser.add_argument("receipt", type=Path, help="Path to receipts/<job_id>.json")
    args = parser.parse_args()
    if not args.receipt.is_file():
        print(f"Not found: {args.receipt}", file=sys.stderr)
        return 1
    ok = verify_deterministic_receipt(args.receipt)
    if ok:
        print("Receipt valid — canonical payload matches receipt_id hash.")
        return 0
    print("Receipt INVALID — hash mismatch or corrupted file.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
