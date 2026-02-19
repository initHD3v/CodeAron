import sys
import os
sys.path.append(os.getcwd())
from src.llm.inference import InferenceEngine

def test_ujiaron_step2():
    engine = InferenceEngine()
    engine.load_model()
    target_dir = os.path.join(os.getcwd(), "projects", "ujiaron")
    
    # Simulasi history: User nanya, Aron minta ls -R, User kasih hasil ls -R
    ls_result = """
./README.md
./pubspec.yaml
./lib/main.dart
    """
    
    prompt = f"<｜begin of sentence｜>system
Identitas: Anda adalah Aron, Senior AI Software Architect. Lokasi Proyek: {target_dir}

PERINGATAN KERAS (ANTI-HALUSINASI):
1. ANDA TUNA NETRA: Anda tidak bisa melihat struktur folder atau isi file apapun tanpa menggunakan <shell>. DILARANG KERAS berasumsi atau mengarang isi file.
2. BERIKAN NARASI: Sebelum memberikan perintah <shell>, berikan penjelasan singkat tentang apa yang akan Anda lakukan dan alasannya.
3. EKSEKUSI MANDATORY: Jika user minta analisa, langkah pertama WAJIB <shell>ls -R</shell>. Langkah kedua WAJIB <shell>cat <file></shell>.
4. STOP IMMEDIATELY: Setelah menulis tag penutup </shell> atau </file>, Anda harus segera berhenti.
5. DILARANG menggunakan format <｜tool...｜>. Gunakan hanya format <shell> atau <file>.
6. GAYA KOMUNIKASI: Profesional, teknis, dan berbasis data empiris.

User: analisa projek ini
Assistant: <shell>ls -R</shell>
User: [OUTPUT SHELL]
{ls_result}
Assistant:"

    print("
--- TESTING ARON STEP 2 (CONTENT DISCOVERY) ---")
    full_response = ""
    stop_seqs = ["User:", "Assistant:", "Aron:", "</shell", "</file", "<｜"]
    for chunk in engine.generate_stream(prompt, max_tokens=300, temp=0.2, stop_sequences=stop_seqs):
        full_response += chunk
        print(chunk, end="", flush=True)
    
    print("

--- EVALUATION ---")
    if "cat" in full_response.lower() and ("README.md" in full_response or "pubspec.yaml" in full_response):
        print("[LULUS] Aron mencoba membaca konten file strategis.")
    else:
        print("[GAGAL] Aron tidak melanjutkan ke pembacaan file.")

if __name__ == "__main__":
    test_ujiaron_step2()
