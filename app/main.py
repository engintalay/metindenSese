import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.audio import join_audio, split_text, write_wav
from app.config import HOST, LANGUAGES, MAX_TEXT_LENGTH, OUTPUTS_DIR, PORT, ROOT_DIR
from app.engines import PiperEngine, XTTSEngine, detect_device

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
    if req.engine not in ENGINES:
        raise HTTPException(status_code=400, detail="Bilinmeyen motor")
    engine = ENGINES[req.engine]
    if not engine.supports(req.lang):
        raise HTTPException(status_code=400, detail="Desteklenmeyen dil")

    chunks = split_text(req.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Metinde seslendirilecek içerik yok")

    try:
        parts = []
        sample_rate = None
        for chunk in chunks:
            samples, sample_rate = engine.synthesize(chunk, req.lang)
            parts.append(samples)
        audio = join_audio(parts, sample_rate)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ses üretilemedi: {exc}")

    OUTPUTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{req.engine}-{req.lang}-{uuid.uuid4().hex[:6]}.wav"
    out_path = write_wav(OUTPUTS_DIR / filename, audio, sample_rate)
    return FileResponse(out_path, media_type="audio/wav", filename=filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT)
