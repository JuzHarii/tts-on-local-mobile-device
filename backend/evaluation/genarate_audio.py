import requests
import os

BASE_URL = "http://localhost:8000"
OUT_BASE = "evaluation/audio" 

os.makedirs(f"{OUT_BASE}/baseline", exist_ok=True)
os.makedirs(f"{OUT_BASE}/finetuned", exist_ok=True)

with open("evaluation/test_case.txt", encoding="utf-8") as f:
    sentences = [line.strip() for line in f if line.strip()]

def gen(model_name, out_dir):
    for i, text in enumerate(sentences):
        r = requests.post(
            f"{BASE_URL}/tts",
            json={
                "text": text,
                "model": model_name,
                "speed": 1.0
            }
        )
        if r.status_code == 200:
            with open(f"{out_dir}/{i}.wav", "wb") as wf:
                wf.write(r.content)
        else:
            print(f"Lỗi {r.status_code} khi tạo câu {i}")

print("Generating baseline audio...")
gen("baseline", f"{OUT_BASE}/baseline")

print("Generating finetuned audio...")
gen("piper-finetuned", f"{OUT_BASE}/finetuned")