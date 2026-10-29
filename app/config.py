from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
OUTPUTS_DIR = ROOT_DIR / "outputs"

HOST = "0.0.0.0"
PORT = 10001

MAX_TEXT_LENGTH = 50000
CHUNK_CHARS = 250
PAUSE_SECONDS = 0.3

DEFAULT_SETTINGS = {
    "speed": 1.0,
    "noise_scale": 0.667,
    "noise_w_scale": 0.8,
    "temperature": 0.75,
    "top_p": 0.85,
}

SETTING_LIMITS = {
    "speed": (0.5, 1.5),
    "noise_scale": (0.0, 1.5),
    "noise_w_scale": (0.0, 1.5),
    "temperature": (0.1, 1.5),
    "top_p": (0.1, 1.0),
}

# "auto": NVIDIA (CUDA) varsa onu kullan, yoksa CPU. Elle "cpu" veya "cuda" yazılabilir.
DEVICE = "auto"

XTTS_MODEL_DIR = MODELS_DIR / "xtts_v2"
XTTS_SPEAKER = "Ana Florence"

LANGUAGES = {
    "tr": {
        "name": "Türkçe",
        "piper": "tr_TR-dfki-medium.onnx",
        "xtts": "tr",
    },
    "de": {
        "name": "Almanca",
        "piper": "de_DE-thorsten-medium.onnx",
        "xtts": "de",
    },
    "es": {
        "name": "İspanyolca",
        "piper": "es_ES-davefx-medium.onnx",
        "xtts": "es",
    },
    "en": {
        "name": "İngilizce",
        "piper": "en_US-lessac-medium.onnx",
        "xtts": "en",
    },
}
