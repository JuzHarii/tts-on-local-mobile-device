import os
import uuid
import wave
from typing import Dict, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from piper import PiperVoice, SynthesisConfig

import pdfplumber
from docx import Document

# =========================
# APP INIT
# =========================
app = FastAPI(title="Multi-model Piper TTS with Speed Control + Upload")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả các thiết bị kết nối
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
OUT_DIR = os.path.join(BASE_DIR, "outputs")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# LOAD MODELS (1 LẦN)
# =========================
voices: Dict[str, PiperVoice] = {}

def load_model(name: str, onnx: str, config: str):
    print(f"Loading model: {name}")
    voices[name] = PiperVoice.load(
        os.path.join(MODEL_DIR, onnx),
        os.path.join(MODEL_DIR, config),
    )
    print(f"Loaded: {name}")

load_model("baseline", "nagiya_ver_1.onnx", "nagiya_ver_1.onnx.json")
load_model("piper-finetuned", "piper_model.onnx", "piper_model.json")

# =========================
# REQUEST SCHEMA (TEXT)
# =========================
class TTSRequest(BaseModel):
    text: str
    model: str = "baseline"
    speed: float = 1.0   # 0.5 | 1 | 1.5 | 2

# =========================
# SPEED → LENGTH SCALE
# =========================
def speed_to_length_scale(speed: float) -> float:
    if speed <= 0:
        return 1.0
    return 1.0 / speed

# =========================
# TEXT → TTS
# =========================
@app.post("/tts")
def tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(400, "Text is empty")

    if req.model not in voices:
        raise HTTPException(400, f"Model '{req.model}' not available")

    voice = voices[req.model]
    length_scale = speed_to_length_scale(req.speed)

    out_wav = os.path.join(OUT_DIR, f"{uuid.uuid4().hex}.wav")

    with wave.open(out_wav, "wb") as wav:
        voice.synthesize_wav(
            req.text,
            wav,
            syn_config=SynthesisConfig(
                noise_scale=0.667,
                length_scale=length_scale,
                noise_w_scale=0.8,
            ),
        )

    return FileResponse(
        out_wav,
        media_type="audio/wav",
        filename="tts.wav",
    )

# =========================
# FILE TEXT EXTRACTION
# =========================
def extract_text_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())

def extract_text_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    return "\n".join(texts)

# =========================
# SPLIT LONG TEXT
# =========================
def chunk_text(text: str, max_len: int = 800) -> List[str]:
    chunks = []
    buf = ""

    for line in text.split("\n"):
        if len(buf) + len(line) > max_len:
            if buf.strip():
                chunks.append(buf.strip())
            buf = line
        else:
            buf += " " + line

    if buf.strip():
        chunks.append(buf.strip())

    return chunks

# =========================
# MERGE WAV FILES
# =========================
def merge_wavs(wav_paths: List[str], out_path: str):
    with wave.open(wav_paths[0], "rb") as w:
        params = w.getparams()

    with wave.open(out_path, "wb") as out:
        out.setparams(params)
        for p in wav_paths:
            with wave.open(p, "rb") as w:
                out.writeframes(w.readframes(w.getnframes()))

# =========================
# UPLOAD PDF / DOCX → TTS
# =========================
@app.post("/tts/upload")
async def tts_from_file(
    file: UploadFile = File(...),
    model: str = Form("baseline"),
    speed: float = Form(1.0),
):
    if model not in voices:
        raise HTTPException(400, f"Model '{model}' not available")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(400, "Only PDF or DOCX supported")

    file_id = uuid.uuid4().hex
    upload_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    if ext == ".pdf":
        text = extract_text_pdf(upload_path)
    else:
        text = extract_text_docx(upload_path)
    
    os.remove(upload_path)
    if not text.strip():
        raise HTTPException(400, "No readable text in file")

    chunks = chunk_text(text)

    voice = voices[model]
    length_scale = speed_to_length_scale(speed)

    temp_wavs = []

    # TTS từng chunk → WAV RIÊNG
    for i, chunk in enumerate(chunks):
        temp_wav = os.path.join(OUT_DIR, f"{file_id}_{i}.wav")
        temp_wavs.append(temp_wav)

        with wave.open(temp_wav, "wb") as wav:
            voice.synthesize_wav(
                chunk,
                wav,
                syn_config=SynthesisConfig(
                    noise_scale=0.667,
                    length_scale=length_scale,
                    noise_w_scale=0.8,
                ),
            )

    # GHÉP WAV
    final_wav = os.path.join(OUT_DIR, f"{file_id}.wav")
    merge_wavs(temp_wavs, final_wav)

    # Cleanup
    for p in temp_wavs:
        os.remove(p)

    return FileResponse(
        final_wav,
        media_type="audio/wav",
        filename="tts_from_file.wav",
    )

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {
        "status": "ok",
        "models": list(voices.keys()),
        "features": [
            "text-to-speech",
            "upload-pdf-docx",
            "speed-control",
        ],
    }
