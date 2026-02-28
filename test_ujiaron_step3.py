import sys
import os
sys.path.append(os.getcwd())
from src.llm.inference import InferenceEngine

def run_scenario(name, prompt, engine):
    print("SCENARIO: " + name)
    print("-" * 50)
    full_response = ""
    stop_seqs = ["User:", "Assistant:", "Aron:", "</shell", "</file", "<｜"]
    for chunk in engine.generate_stream(prompt, max_tokens=500, temp=0.2, stop_sequences=stop_seqs):
        full_response += chunk
        print(chunk, end="", flush=True)
    print("\n" + "-" * 50)
    return full_response

def main():
    engine = InferenceEngine()
    engine.load_model()
    
    # 1. SALAM
    p1 = "<|begin of sentence|>system\nYou are Aron, a Senior AI Architect. Use Bahasa Indonesia.<|User|>Halo Aron, apa kabar?<|Assistant|>"
    r1 = run_scenario("Salam & Sapaan", p1, engine)
    
    # 2. ANALISA
    p2 = "<|begin of sentence|>system\nYou are Aron. Context: Local Project. Rules: Use <shell> for exploration. Never guess content. Always 'ls' first.<|User|>Cek struktur folder proyek ini.<|Assistant|>"
    r2 = run_scenario("Analisis Proyek", p2, engine)
    
    # 3. FILE
    p3 = "<|begin of sentence|>system\nYou are Aron. Rules: Use <file path=\"...\">content</file> to create/modify files.<|User|>Buat file 'version.txt' yang berisi '1.0.0-stable'.<|Assistant|>"
    r3 = run_scenario("Modifikasi File", p3, engine)

    # 4. ARCH
    p4 = "<|begin of sentence|>system\nYou are Aron. Semantic Memory context provided below.\n[LONG-TERM MEMORY]\nFile: src/core/orchestrator.py - Orchestrator class coordinates planning, routing, and execution.\nFile: src/llm/inference.py - InferenceEngine class handles model loading and generation.\n<|User|>Bagaimana hubungan antara Orchestrator dan InferenceEngine?<|Assistant|>"
    r4 = run_scenario("Tanya Arsitektur", p4, engine)

    print("\n=== FINAL OBSERVATION SUMMARY ===")
    
    if any(w in r1.lower() for w in ["halo", "kabar", "bantu"]):
        print("✅ Salam: LULUS")
    else:
        print("❌ Salam: GAGAL")

    if "<shell>ls" in r2.lower():
        print("✅ Analisis: LULUS")
    else:
        print("❌ Analisis: GAGAL")

    if "<file path=\"version.txt\">" in r3.lower():
        print("✅ Modifikasi: LULUS")
    else:
        print("❌ Modifikasi: GAGAL")

    if "orchestrator" in r4.lower() and "inference" in r4.lower():
        print("✅ Arsitektur: LULUS")
    else:
        print("❌ Arsitektur: GAGAL")

if __name__ == "__main__":
    main()
