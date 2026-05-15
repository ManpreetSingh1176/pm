#!/usr/bin/env sh
cd "$(dirname "$0")/.." || exit 1
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
