#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x .venv/bin/python ]; then
    echo "Önce scripts/install.sh çalıştırın." >&2
    exit 1
fi

PIPER_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main"
PIPER_VOICES=(
    "tr/tr_TR/dfki/medium/tr_TR-dfki-medium"
    "de/de_DE/thorsten/medium/de_DE-thorsten-medium"
    "es/es_ES/davefx/medium/es_ES-davefx-medium"
    "en/en_US/lessac/medium/en_US-lessac-medium"
)

mkdir -p models
cd models

echo "[1/2] Piper ses modelleri indiriliyor..."
for voice in "${PIPER_VOICES[@]}"; do
    name="$(basename "$voice")"
    for ext in onnx onnx.json; do
        if [ -f "${name}.${ext}" ]; then
            echo "  zaten var: ${name}.${ext}"
        else
            echo "  indiriliyor: ${name}.${ext}"
            curl -fL --retry 3 -o "${name}.${ext}" "${PIPER_BASE}/${voice}.${ext}"
        fi
    done
done
cd "$ROOT_DIR"

echo "[2/2] XTTS v2 modeli indiriliyor (CPML lisansı, ticari olmayan kullanım)..."
if [ -f models/xtts_v2/model.pth ]; then
    echo "  zaten var: models/xtts_v2"
else
    COQUI_TOS_AGREED=1 .venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='coqui/XTTS-v2',
    local_dir='models/xtts_v2',
    allow_patterns=['*.json', '*.pth', '*.pth.tar', '*.wav'],
)
"
fi

echo "Modeller hazır."
