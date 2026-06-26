#!/usr/bin/env bash
# Run from repo root
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
set -a
# shellcheck disable=SC1091
source .env
set +a
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
