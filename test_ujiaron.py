import sys
import os
sys.path.append(os.getcwd())
from src.llm.inference import InferenceEngine

def test_ujiaron_analysis():
    engine = InferenceEngine()
    engine.load_model()
    target_dir = os.path.join(os.getcwd(), "projects", "ujiaron")
    prompt = f"<｜begin of sentence｜>system\nIdentitas: Anda adalah Aron, Senior AI Software Architect. Lokasi Proyek: {target_dir}\n\nPERINGATAN KERAS (ANTI-HALUSINASI):\n1. ANDA TUNA NETRA: Anda tidak bisa melihat struktur folder atau isi file apapun tanpa menggunakan <shell>. DILARANG KERAS berasumsi atau mengarang isi file.\n2. BERIKAN NARASI: Sebelum memberikan perintah <shell>, berikan penjelasan singkat (1-2 kalimat) tentang apa yang akan Anda lakukan dan alasannya.\n3. EKSEKUSI MANDATORY: Jika user minta analisa, langkah pertama WAJIB <shell>ls -R</shell>. Langkah kedua WAJIB <shell>cat <file></shell>.\n4. STOP IMMEDIATELY: Setelah menulis tag penutup </shell> atau </file>, Anda harus segera berhenti.\n5. DILARANG menggunakan format <｜tool...｜>. Gunakan hanya format <shell> atau <file>.\n6. GAYA KOMUNIKASI: Profesional, teknis, dan berbasis data empiris.\n\nSTRUKTUR RESPONS:\n   - Narasi Strategi\n   - Perintah Teknis (<shell> atau <file>)\n\nUser: analisa projek ini\nAssistant:"

    print("\n--- TESTING ARON ON DIRECTORY ---")
    full_response = ""
    stop_seqs = ["User:", "Assistant:", "Aron:", "</shell", "</file", "<｜"]
    for chunk in engine.generate_stream(prompt, max_tokens=300, temp=0.2, stop_sequences=stop_seqs):
        full_response += chunk
        print(chunk, end="", flush=True)
    
    print("\n\n--- OBSERVATION ---")
    if "<shell>ls -R</shell>" in full_response or "ls -R" in full_response:
        print("[LULUS] Aron mematuhi SOP.")
    else:
        print("[GAGAL] Aron tidak mematuhi SOP.")

if __name__ == "__main__":
    test_ujiaron_analysis()
