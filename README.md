<div align="center">

# 🤖 CodeAron
### **The Proactive Senior AI Architect for Apple Silicon**

<p align="center">
  <img src="https://img.shields.io/badge/PLATFORM-macOS%20SILICON-000000?style=for-the-badge&logo=apple&logoColor=white" />
  <img src="https://img.shields.io/badge/ENGINE-MLX%20LM-FF4B11?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MODEL-DEEPSEEK--V2-0052FF?style=for-the-badge&logo=deepseek&logoColor=white" />
</p>

---

**CodeAron** adalah asisten pengembang berbasis AI yang berjalan 100% secara lokal. Aron dirancang untuk menjadi **Senior Architect** mandiri yang memiliki integritas data tinggi, tidak pernah berhalusinasi, dan proaktif dalam menganalisis serta memodifikasi kode langsung di mesin Anda.

[Fitur Utama](#-fitur-utama) • [Tech Stack](#-technology-stack) • [Instalasi](#-instalasi--persiapan) • [Arsitektur](#-arsitektur-sistem)

</div>

## 🚀 Fitur Utama (v0.2.1)

### 🧠 **Senior Architect Persona**
Aron bukan sekadar chatbot. Ia memiliki kepribadian profesional yang menggunakan prinsip **"Check Before Speak"**. Ia akan melakukan observasi struktur proyek (`ls`) dan membaca konten file (`cat`) secara otomatis sebelum memberikan opini teknis atau rekomendasi arsitektur.

### 🛡️ **Anti-Hallucination Protocol**
- **Blind Observation:** Aron menyadari ia "tuna netra" tanpa perintah shell. Ia diwajibkan melakukan validasi empiris pada setiap langkah.
- **Deterministic Inference:** Menggunakan temperatur rendah (0.2) untuk akurasi teknis maksimal.
- **Strict Stop Sequences:** Model akan berhenti seketika setelah memberikan perintah teknis untuk mencegah prediksi output yang salah.

### 🌊 **Modern Terminal UX**
- **IDE-Style Code Rendering:** Blok kode dengan *syntax highlighting* Monokai yang bersih.
- **Live Performance Monitor:** Pantau penggunaan RAM dan CPU Apple Silicon Anda secara real-time di bilah status bawah yang elegan.
- **Professional Layout:** Interface berbasis panel yang memisahkan konteks user dan asisten secara visual.

---

## 🛠️ Technology Stack

| Komponen | Teknologi | Deskripsi |
| :--- | :--- | :--- |
| **Inference Engine** | **MLX Framework** | Optimasi Unified Memory untuk kecepatan maksimal di Mac M1-M4. |
| **Model** | **DeepSeek-Coder-V2** | Model coding paling efisien untuk tugas arsitektural lokal. |
| **Memory** | **Qdrant & FastEmbed** | Semantic memory (RAG) untuk pemahaman konteks proyek jangka panjang. |
| **Interface** | **Rich & Prompt Toolkit** | UI terminal modern dengan auto-completion dan real-time status. |
| **Analysis** | **Tree-sitter** | Parsing kode untuk pemahaman struktur AST yang akurat. |

---

## 📂 Arsitektur Sistem

```text
CodeAron/
├── 🧠 src/core/        # Orchestrator & Logic Center
├── 🤖 src/llm/         # MLX Inference Engine
├── 💾 src/memory/      # Vector Store & RAG Logic
├── 🛠️ src/tools/       # File Patcher & Project Validator
└── 🎨 src/ui/          # Modern UI Renderer
```

---

## ⚡ Instalasi & Persiapan

### Prasyarat
- macOS dengan Apple Silicon (M-Series).
- Python 3.11+.

### Quick Start
```bash
# Clone repository
git clone https://github.com/initHD3v/CodeAron.git
cd CodeAron

# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run CodeAron
aron
```

---

<details>
<summary><b>🏮 Filosofi Nama: Mengapa "Aron"?</b></summary>
<br>

Diambil dari kearifan lokal **Suku Karo**, ***Aron*** merujuk pada kelompok kerja tradisional yang berlandaskan semangat **Gotong Royong**. 

Filosofi ini menjadi identitas inti CodeAron:
- **Persatuan:** Kolaborasi harmonis antara pengembang dan AI dalam satu kelompok kerja.
- **Kebersamaan:** Aron hadir bukan sebagai alat, melainkan rekan yang turun ke "ladang kode" untuk menanam logika dan memanen solusi secara bersama-sama.
- **Solidaritas:** Mengedepankan prinsip timbal balik (*reciprocity*)—di mana ketajaman analitis AI mendukung visi kreatif manusia.

**CodeAron** adalah jembatan antara nilai luhur tradisi dan kemajuan teknologi; membuktikan bahwa inovasi terbaik lahir dari semangat kebersamaan.

</details>

<div align="center">
  <p><i>"Privasi Total, Performa Tanpa Batas."</i></p>
  <sub><b>v0.2.1</b> | Dibuat dengan ❤️ untuk komunitas Developer Indonesia oleh <b>initHD3v</b></sub>
</div>
