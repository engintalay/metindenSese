import shutil
import subprocess
from pathlib import Path

import numpy as np
from piper import PiperVoice

from app.config import DEVICE, LANGUAGES, MODELS_DIR, XTTS_MODEL_DIR, XTTS_SPEAKER


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

    def load(self, lang: str) -> None:
        self._voice(lang)

    def synthesize(self, text: str, lang: str) -> tuple[np.ndarray, int]:
        voice = self._voice(lang)
        chunks = [chunk.audio_int16_array for chunk in voice.synthesize(text)]
        samples = np.concatenate(chunks).astype(np.float32) / 32768.0
        return samples, voice.config.sample_rate


class XTTSEngine:
    name = "xtts"

    def __init__(self, device: str):
        self.device = device
        self._tts = None

    def supports(self, lang: str) -> bool:
        return lang in LANGUAGES

    def _model(self):
        if self._tts is None:
            from TTS.api import TTS

            self._tts = TTS(model_path=str(XTTS_MODEL_DIR), config_path=str(XTTS_MODEL_DIR / "config.json"))
            self._tts.to(self.device)
        return self._tts

    def load(self, lang: str) -> None:
        self._model()

    def synthesize(self, text: str, lang: str) -> tuple[np.ndarray, int]:
        tts = self._model()
        wav = tts.tts(
            text=text,
            speaker=XTTS_SPEAKER,
            language=LANGUAGES[lang]["xtts"],
        )
        return np.asarray(wav, dtype=np.float32), tts.synthesizer.output_sample_rate
