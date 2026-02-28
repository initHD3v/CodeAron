import sys
import os

sys.path.append(os.getcwd())
from src.llm.inference import InferenceEngine

print("Testing 'Hai' directly...")
engine = InferenceEngine()
engine.load_model()
prompt = "<|begin of sentence|>User: Hai<|Assistant|>"
resp = ""
for chunk in engine.generate_stream(prompt, max_tokens=20):
    resp += chunk
    print(chunk, end='', flush=True)

if resp.strip():
    print("\n✅ Inference OK")
else:
    print("\n❌ Inference FAIL")
