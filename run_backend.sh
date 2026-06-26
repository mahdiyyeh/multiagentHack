#!/usr/bin/env bash
# Run from repo root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
