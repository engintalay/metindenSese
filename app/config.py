from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
OUTPUTS_DIR = ROOT_DIR / "outputs"

HOST = "0.0.0.0"
PORT = 10001

# "auto": NVIDIA (CUDA) varsa onu kullan, yoksa CPU. Elle "cpu" veya "cuda" yazılabilir.
DEVICE = "auto"

LANGUAGES = {
    "tr": {
        "name": "Türkçe",
        "piper": "tr_TR-dfki-medium.onnx",
    },
    "de": {
        "name": "Almanca",
        "piper": "de_DE-thorsten-medium.onnx",
    },
    "es": {
        "name": "İspanyolca",
        "piper": "es_ES-davefx-medium.onnx",
    },
    "en": {
        "name": "İngilizce",
        "piper": "en_US-lessac-medium.onnx",
    },
}
