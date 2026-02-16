# 🤖 CodeAron: Senior AI Architect 🚀

[![Platform](https://img.shields.io/badge/Platform-macOS%20(Apple%20Silicon)-black?style=for-the-badge&logo=apple)](https://developer.apple.com/apple-silicon/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![MLX](https://img.shields.io/badge/Engine-MLX-orange?style=for-the-badge)](https://github.com/ml-explore/mlx)

**CodeAron** adalah asisten pengembang berbasis AI yang berjalan 100% secara lokal, dirancang khusus untuk ekosistem Apple Silicon. Berfungsi sebagai **Senior AI Architect** yang proaktif, Aron tidak hanya menjawab pertanyaan, tetapi mampu menganalisis arsitektur, membaca kode, dan melakukan perubahan file secara cerdas dan mandiri.

---

## 🛠️ Technology Stack

CodeAron memanfaatkan teknologi mutakhir untuk performa maksimal di mesin lokal:

- **Core Engine:** [MLX Framework](https://github.com/ml-explore/mlx) - Optimasi inferensi untuk Apple Unified Memory.
- **LLM Model:** [DeepSeek-Coder-V2-Lite](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) - Model coding state-of-the-art dengan efisiensi tinggi.
- **Vector Database:** [Qdrant](https://qdrant.tech/) - Untuk Semantic Memory dan RAG (Retrieval-Augmented Generation).
- **Terminal UI:** [Rich](https://github.com/Textualize/rich) & [Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) - Antarmuka terminal yang modern dan interaktif.
- **Static Analysis:** [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - Untuk pemahaman struktur kode yang mendalam.

---

## ✨ Fitur Utama (v0.2.1)

### 🧠 Senior AI Persona
Aron kini berbicara seperti Senior Developer profesional. Ia menggunakan prinsip **"Check Before Speak"**, memastikan setiap analisis didasarkan pada data asli dari direktori proyek Anda.

### 🛡️ Anti-Hallucination Protocol
Dengan suhu inferensi yang dioptimasi (0.2) dan SOP observasi wajib, Aron dilarang keras mengarang struktur folder atau isi file. Ia akan selalu mulai dengan `ls` dan `cat` sebelum memberikan kesimpulan.

### 🌊 Modern Terminal UI
- **Professional Chat Bubbles:** Pemisahan visual yang jelas antara User dan AI.
- **Live Performance Monitoring:** Pantau penggunaan RAM dan CPU secara real-time di bilah status bawah.
- **IDE-Like Code Rendering:** Penampilan kode dengan syntax highlighting profesional bertema Monokai.

---

## 🚀 Instalasi & Persiapan

### Prasyarat
- macOS dengan Apple Silicon (M1, M2, M3, M4).
- Python 3.11+.

### Cara Menjalankan
1. **Clone & Setup:**
   ```bash
   git clone https://github.com/initHD3v/CodeAron.git
   cd CodeAron
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```
2. **Launch:**
   ```bash
   aron
   ```

---

## 📈 Status Pengembangan

- [x] Migrasi ke MLX-LM v0.30+
- [x] Redesain UI Profesional
- [x] Implementasi Proactive Analysis SOP
- [x] Perbaikan Bug Halusinasi & Stop Sequences
- [ ] Integrasi Vision Engine (Upcoming)
- [ ] Fitur Multi-Project Indexing (Upcoming)

---
**v0.2.1** | Dibuat dengan ❤️ oleh [initHD3v](https://github.com/initHD3v) untuk komunitas Developer Indonesia.
