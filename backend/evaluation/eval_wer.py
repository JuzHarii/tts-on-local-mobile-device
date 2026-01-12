from jiwer import wer, cer, Compose, ToLowerCase, RemovePunctuation
from asr_whisper import transcribe_dir

transform = Compose([
    ToLowerCase(),
    RemovePunctuation()
])

with open("evaluation/test_case.txt", encoding="utf-8") as f:
    refs = [line.strip() for line in f if line.strip()]

print("--- Transcribing Baseline ---")
hyp_baseline = transcribe_dir("evaluation/audio/baseline")

print("\n--- Transcribing Finetuned ---")
hyp_finetuned = transcribe_dir("evaluation/audio/finetuned")

def avg_metric(refs, hyps, metric_func):
    if not hyps:
        return 0
    
    clean_refs = [transform(r) for r in refs]
    clean_hyps = [transform(h) for h in hyps]
    
    total = sum(metric_func(r, h) for r, h in zip(clean_refs, clean_hyps))
    return total / len(refs)

print("\n" + "="*20)
print("=== BASELINE ===")
print(f"WER: {avg_metric(refs, hyp_baseline, wer):.4f}")
print(f"CER: {avg_metric(refs, hyp_baseline, cer):.4f}")

print("\n=== FINETUNED ===")
print(f"WER: {avg_metric(refs, hyp_finetuned, wer):.4f}")
print(f"CER: {avg_metric(refs, hyp_finetuned, cer):.4f}")
print("="*20)