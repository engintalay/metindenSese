import re
import wave
from pathlib import Path

import numpy as np

from app.config import CHUNK_CHARS, PAUSE_SECONDS

SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")


def split_text(text: str, max_chars: int = CHUNK_CHARS) -> list[str]:
    sentences = [s.strip() for s in SENTENCE_END.split(text) if s and s.strip()]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        for piece in _hard_split(sentence, max_chars):
            if not current:
                current = piece
            elif len(current) + 1 + len(piece) <= max_chars:
                current = f"{current} {piece}"
            else:
                chunks.append(current)
                current = piece
    if current:
        chunks.append(current)
    return chunks


def _hard_split(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]
    parts: list[str] = []
    current = ""
    for word in sentence.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            parts.append(current)
            current = word
    if current:
        parts.append(current)
    return parts


def join_audio(parts: list[np.ndarray], sample_rate: int) -> np.ndarray:
    pause = np.zeros(int(sample_rate * PAUSE_SECONDS), dtype=np.float32)
    joined: list[np.ndarray] = []
    for index, part in enumerate(parts):
        if index:
            joined.append(pause)
        joined.append(part.astype(np.float32))
    return np.concatenate(joined) if joined else np.zeros(0, dtype=np.float32)


def write_wav(path: Path, samples: np.ndarray, sample_rate: int) -> Path:
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return path
