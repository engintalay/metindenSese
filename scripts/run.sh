#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x .venv/bin/uvicorn ]; then
    echo "Önce scripts/install.sh çalıştırın." >&2
    exit 1
fi

PORT="${PORT:-10001}"
HOST="${HOST:-0.0.0.0}"

echo "Metinden Sese başlatılıyor: http://${HOST}:${PORT}"
exec .venv/bin/uvicorn app.main:app --host "$HOST" --port "$PORT"
