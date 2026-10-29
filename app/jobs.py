import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.audio import join_audio, split_text, write_wav
from app.config import OUTPUTS_DIR

_executor = ThreadPoolExecutor(max_workers=1)
_jobs: dict[str, "Job"] = {}
_lock = threading.Lock()


@dataclass
class Job:
    id: str
    engine_name: str
    lang: str
    total: int
    status: str = "queued"
    done: int = 0
    created_at: float = 0.0
    started_at: float | None = None
    finished_at: float | None = None
    output: Path | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        now = time.time()
        elapsed = None
        remaining = None
        if self.started_at is not None:
            elapsed = (self.finished_at or now) - self.started_at
            if self.status == "running" and self.done > 0:
                remaining = elapsed / self.done * (self.total - self.done)
        percent = round(100 * self.done / self.total) if self.total else 0
        return {
            "id": self.id,
            "status": self.status,
            "engine": self.engine_name,
            "lang": self.lang,
            "total": self.total,
            "done": self.done,
            "percent": percent,
            "elapsed_seconds": round(elapsed, 1) if elapsed is not None else None,
            "remaining_seconds": round(remaining) if remaining is not None else None,
            "output_name": self.output.name if self.output else None,
            "error": self.error,
        }


def render(engine, engine_name: str, lang: str, chunks: list[str], settings: dict, on_chunk=None) -> Path:
    engine.load(lang)
    parts = []
    sample_rate = None
    for chunk in chunks:
        samples, sample_rate = engine.synthesize(chunk, lang, settings)
        parts.append(samples)
        if on_chunk:
            on_chunk()
    audio = join_audio(parts, sample_rate)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{engine_name}-{lang}-{uuid.uuid4().hex[:6]}.wav"
    return write_wav(OUTPUTS_DIR / filename, audio, sample_rate)


def create_job(engine, engine_name: str, lang: str, text: str, settings: dict) -> Job:
    chunks = split_text(text)
    job = Job(
        id=uuid.uuid4().hex,
        engine_name=engine_name,
        lang=lang,
        total=len(chunks),
        created_at=time.time(),
    )
    with _lock:
        _jobs[job.id] = job
    _executor.submit(_run, job, engine, chunks, settings)
    return job


def _advance(job: Job) -> None:
    job.done += 1


def _run(job: Job, engine, chunks: list[str], settings: dict) -> None:
    job.started_at = time.time()
    try:
        job.status = "loading"
        engine.load(job.lang)
        job.status = "running"
        job.output = render(engine, job.engine_name, job.lang, chunks, settings, lambda: _advance(job))
        job.status = "done"
    except Exception as exc:
        job.status = "error"
        job.error = str(exc)
    finally:
        job.finished_at = time.time()


def get_job(job_id: str) -> Job | None:
    with _lock:
        return _jobs.get(job_id)
