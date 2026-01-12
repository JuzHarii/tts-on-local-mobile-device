import whisper
import os

model = whisper.load_model("base")

def transcribe_dir(audio_dir):
    texts = []
    
    files = [f for f in os.listdir(audio_dir) if f.endswith(".wav")]
    
    files.sort(key=lambda x: int(x.split(".")[0]))

    for f in files:
        path = os.path.join(audio_dir, f)
        
        result = model.transcribe(path, language="vi", fp16=False)
        
        text = result["text"].strip()
        texts.append(text)
        print(f"Transcribed {f}: {text}") 

    return texts