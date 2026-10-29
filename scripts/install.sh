#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY_VERSION="3.11"

if command -v uv >/dev/null 2>&1; then
    echo "[1/3] Python ${PY_VERSION} kuruluyor (uv)..."
    uv python install "$PY_VERSION"
    echo "[2/3] Sanal ortam oluşturuluyor..."
    uv venv --allow-existing --python "$PY_VERSION" .venv
    echo "[3/3] Bağımlılıklar kuruluyor..."
    uv pip install --python .venv/bin/python -r requirements.txt
else
    if ! command -v "python${PY_VERSION}" >/dev/null 2>&1; then
        echo "Hata: python${PY_VERSION} bulunamadı. Python ${PY_VERSION} kurun veya uv yükleyin (https://docs.astral.sh/uv/)." >&2
        exit 1
    fi
    echo "[1/2] Sanal ortam oluşturuluyor..."
    [ -d .venv ] || "python${PY_VERSION}" -m venv .venv
    echo "[2/2] Bağımlılıklar kuruluyor..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

mkdir -p models outputs
echo "Kurulum tamamlandı. Modeller için: scripts/download_models.sh"
