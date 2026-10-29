import shutil
import subprocess
import wave
from pathlib import Path

from piper import PiperVoice

from app.config import DEVICE, LANGUAGES, MODELS_DIR


def detect_device() -> str:
    if DEVICE != "auto":
        return DEVICE
    if shutil.which("nvidia-smi") is None:
        return "cpu"
    try:
        subprocess.run(["nvidia-smi"], check=True, capture_output=True, timeout=10)
    except (subprocess.SubprocessError, OSError):
        return "cpu"
    try:
        import onnxruntime

        if "CUDAExecutionProvider" in onnxruntime.get_available_providers():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


class PiperEngine:
    name = "piper"

    def __init__(self, device: str):
        self.device = device
        self._voices: dict[str, PiperVoice] = {}

    def supports(self, lang: str) -> bool:
        return lang in LANGUAGES

    def _voice(self, lang: str) -> PiperVoice:
        if lang not in self._voices:
            model_path = MODELS_DIR / LANGUAGES[lang]["piper"]
            self._voices[lang] = PiperVoice.load(
                model_path, use_cuda=self.device == "cuda"
            )
        return self._voices[lang]

    def synthesize(self, text: str, lang: str, out_path: Path) -> Path:
        voice = self._voice(lang)
        with wave.open(str(out_path), "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        return out_path
