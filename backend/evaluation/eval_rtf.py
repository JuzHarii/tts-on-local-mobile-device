import time
import requests
import os
import soundfile as sf

BASE_URL = "http://localhost:8000"
TEST_FILE = "evaluation/test_case.txt"

MODELS = ["baseline", "piper-finetuned"]

def get_audio_duration(wav_path):
    audio, sr = sf.read(wav_path)
    return len(audio) / sr

with open(TEST_FILE, encoding="utf-8") as f:
    sentences = [line.strip() for line in f if line.strip()]

for model in MODELS:
    print(f"\n===== RTF: {model.upper()} =====")

    total_gen_time = 0.0
    total_audio_time = 0.0

    for i, text in enumerate(sentences):
        start = time.time()

        r = requests.post(
            f"{BASE_URL}/tts",
            json={
                "text": text,
                "model": model,
                "speed": 1.0
            }
        )

        gen_time = time.time() - start

        wav_path = f"evaluation/tmp_{model}_{i}.wav"
        with open(wav_path, "wb") as f:
            f.write(r.content)

        audio_time = get_audio_duration(wav_path)

        total_gen_time += gen_time
        total_audio_time += audio_time

        os.remove(wav_path)

    rtf = total_gen_time / total_audio_time
    print(f"Total synth time: {total_gen_time:.2f}s")
    print(f"Total audio time: {total_audio_time:.2f}s")
    print(f"RTF = {rtf:.3f}")
