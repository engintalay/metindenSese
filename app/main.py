from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.audio import split_text
from app.config import HOST, LANGUAGES, MAX_TEXT_LENGTH, PORT, ROOT_DIR
from app.engines import PiperEngine, XTTSEngine, detect_device
from app.jobs import create_job, get_job, render

app = FastAPI(title="Metinden Sese")
app.mount("/static", StaticFiles(directory=ROOT_DIR / "app" / "static"), name="static")

DEVICE = detect_device()
ENGINES = {
    "piper": PiperEngine(DEVICE),
    "xtts": XTTSEngine(DEVICE),
}


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    lang: str
    engine: str = "piper"


def _validate(req: SpeakRequest):
    if req.engine not in ENGINES:
        raise HTTPException(status_code=400, detail="Bilinmeyen motor")
    if req.lang not in LANGUAGES:
        raise HTTPException(status_code=400, detail="Desteklenmeyen dil")
    if not split_text(req.text):
        raise HTTPException(status_code=400, detail="Metinde seslendirilecek içerik yok")


@app.get("/")
def index():
    return FileResponse(ROOT_DIR / "app" / "static" / "index.html")


@app.get("/api/languages")
def list_languages():
    return [{"code": code, "name": info["name"]} for code, info in LANGUAGES.items()]


@app.get("/api/engines")
def list_engines():
    return {
        "device": DEVICE,
        "engines": list(ENGINES.keys()),
        "max_text_length": MAX_TEXT_LENGTH,
    }


@app.post("/api/speak")
def speak(req: SpeakRequest):
    _validate(req)
    engine = ENGINES[req.engine]
    try:
        out_path = render(engine, req.engine, req.lang, split_text(req.text))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ses üretilemedi: {exc}")
    return FileResponse(out_path, media_type="audio/wav", filename=out_path.name)


@app.post("/api/jobs", status_code=202)
def start_job(req: SpeakRequest):
    _validate(req)
    job = create_job(ENGINES[req.engine], req.engine, req.lang, req.text)
    return job.to_dict()


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="İş bulunamadı")
    return job.to_dict()


@app.get("/api/jobs/{job_id}/audio")
def job_audio(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="İş bulunamadı")
    if job.status != "done" or job.output is None:
        raise HTTPException(status_code=409, detail="Ses henüz hazır değil")
    return FileResponse(job.output, media_type="audio/wav", filename=job.output.name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT)
