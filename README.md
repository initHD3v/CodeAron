<div align="center">

# 🤖 CodeAron
### **Partner Ngoding Paling "Sat-Set" & 100% Lokal di Apple Silicon**

<p align="center">
  <img src="https://img.shields.io/badge/PLATFORM-macOS%20SILICON-000000?style=for-the-badge&logo=apple&logoColor=white" />
  <img src="https://img.shields.io/badge/ENGINE-MLX%20LM-FF4B11?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VERSION-0.3.0-00FF00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MODEL-QWEN%2FDEEPSEEK-0052FF?style=for-the-badge&logo=deepseek&logoColor=white" />
</p>

---

**CodeAron** adalah asisten pengembang berbasis AI yang berjalan 100% secara lokal. Aron dirancang untuk menjadi **Senior Architect** mandiri yang memiliki integritas data tinggi, tidak pernah berhalusinasi, dan proaktif dalam menganalisis serta memodifikasi kode langsung di mesin Anda.

[Fitur Utama](#-fitur-utama) • [Command](#-command) • [Konfigurasi](#-konfigurasi) • [Instalasi](#-instalasi) • [Arsitektur](#-arsitektur)

</div>

## 🎯 Apa yang Baru di v0.3.0?

### ✨ Fitur Baru
- **🖼️ Vision Engine** - Analisis gambar dengan command `/vision`
- **⚙️ Project Config** - Konfigurasi per-project via `.codearon/config.yaml`
- **🛡️ Circuit Breaker** - Auto-stop jika terlalu banyak failure
- **⏱️ Rate Limiting** - Cooldown antar command untuk stabilitas
- **🧪 Test Suite** - 22+ unit tests untuk memastikan kualitas

### 🐛 Bug Fixes
- Fixed Qdrant lock file issue yang menyebabkan crash
- Fixed memory leak di orchestrator
- Fixed prompt template inconsistency untuk multi-model support
- Improved error handling dengan custom exceptions

---

## 🚀 Fitur Utama

### 🧠 **Senior Architect Persona**
Aron bukan sekadar chatbot. Ia memiliki kepribadian profesional yang menggunakan prinsip **"Check Before Speak"**. Ia akan melakukan observasi struktur proyek (`ls`) dan membaca konten file (`cat`) secara otomatis sebelum memberikan opini teknis.

### 🛡️ **Anti-Hallucination Protocol**
- **Blind Observation:** Aron menyadari ia "tuna netra" tanpa perintah shell. Wajib validasi empiris.
- **Deterministic Inference:** Temperatur rendah (0.2) untuk akurasi teknis maksimal.
- **Strict Stop Sequences:** Berhenti seketika setelah perintah untuk mencegah prediksi salah.

### 🔒 **Circuit Breaker & Rate Limiting** (BARU!)
- **Auto-protect:** Jika 5 command gagal berturut-turut, sistem stop otomatis.
- **Cooldown:** 2 detik antar command untuk mencegah overload.
- **Smart Recovery:** Counter reset otomatis setelah command berhasil.

### 🌊 **Modern Terminal UX**
- **IDE-Style Code Rendering:** Syntax highlighting Monokai yang bersih.
- **Live Performance Monitor:** RAM & CPU usage real-time di status bar.
- **Professional Layout:** Interface berbasis panel yang terpisah visual.

---

## 💬 Command

### Command Chat
```bash
# Mulai sesi interaktif
aron

# Chat langsung dengan prompt
aron chat "Analisa struktur project ini"
```

### Command Sistem
| Command | Deskripsi |
|---------|-----------|
| `/help` | Tampilkan bantuan |
| `/clear` | Bersihkan layar & history |
| `/hub` | Kelola model AI (Download/List) |
| `/update` | Update CodeAron ke versi terbaru |
| `/undo` | Rollback perubahan terakhir |
| `/checkpoint` | Git commit dengan pesan custom |
| `/vision [path]` | Analisis gambar (NEW!) |
| `/quit` | Keluar dari sesi |

### Contoh Penggunaan Vision
```bash
# Mode interaktif
/vision
# > Path ke gambar: /Users/saya/screenshot.png
# > Pertanyaan: Deskripsikan UI ini

# Mode inline
/vision /path/to/screenshot.png
```

---

## ⚙️ Konfigurasi

### Default Configuration
CodeAron bekerja out-of-the-box tanpa konfigurasi. Untuk custom settings:

```bash
# Buat folder config
mkdir -p .codearon

# Copy template
cp .codearon.config.example .codearon/config.yaml

# Edit sesuai kebutuhan
nano .codearon/config.yaml
```

### Contoh Config
```yaml
# .codearon/config.yaml
version: "1.0"

model:
  default: "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
  fallback: "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"

tools:
  shell:
    auto_confirm: ["ls", "pwd", "head", "tail", "echo"]
    blocked: ["rm -rf /", "sudo", "mkfs"]
    cooldown_seconds: 2.0
    max_consecutive_failures: 5

ignored_dirs:
  - .git
  - node_modules
  - .venv
  - __pycache__
```

### Config Options
| Key | Default | Deskripsi |
|-----|---------|-----------|
| `model.default` | Qwen2.5-Coder-7B | Model utama untuk inference |
| `tools.shell.cooldown_seconds` | 2.0 | Delay antar command shell |
| `tools.shell.max_consecutive_failures` | 5 | Max failure sebelum circuit breaker |
| `ignored_dirs` | [...] | Folder yang diabaikan saat indexing |

---

## 🛠️ Technology Stack

| Komponen | Teknologi | Deskripsi |
| :--- | :--- | :--- |
| **Inference Engine** | **MLX Framework** | Optimasi Unified Memory untuk M1-M4 |
| **Model** | **Qwen2.5/DeepSeek** | Model coding terbaik untuk lokal |
| **Memory** | **Qdrant + FastEmbed** | Semantic memory (RAG) untuk konteks |
| **Interface** | **Rich + Prompt Toolkit** | UI terminal modern |
| **Analysis** | **Tree-sitter** | AST parsing untuk struktur kode |
| **Config** | **PyYAML** | Project-specific configuration |

---

## 📂 Arsitektur Sistem

```text
CodeAron/
├── 🧠 src/core/           # Orchestrator, Config, Exceptions
│   ├── orchestrator.py    # Main controller dengan circuit breaker
│   ├── config_manager.py  # Project config manager (NEW!)
│   ├── exceptions.py      # Custom exceptions (NEW!)
│   └── prompt_templates.py # Unified templates (NEW!)
├── 🤖 src/llm/            # MLX Inference Engine
├── 💾 src/memory/         # Vector Store & RAG
├── 🛠️ src/tools/          # Tools & Bridges
│   ├── vision_engine.py   # Vision AI untuk gambar (NEW!)
│   └── ...
└── 🎨 src/ui/             # Modern UI Renderer
```

---

## ⚡ Instalasi

### Prasyarat
- macOS dengan Apple Silicon (M1, M2, M3, M4)
- Python 3.11+
- Git

### Quick Start
```bash
# Clone repository
git clone https://github.com/initHD3v/CodeAron.git
cd CodeAron

# Setup environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Jalankan CodeAron
aron
```

### Update dari Versi Lama
```bash
# Pull kode terbaru
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt
pip install -e .

# Migrasi config (opsional)
python scripts/migrate_config.py
```

---

## 🧪 Testing

```bash
# Run semua tests
python -m unittest discover tests/

# Run specific test
python -m unittest tests.test_exceptions -v

# Run dengan coverage (jika coverage terinstall)
coverage run -m unittest discover
coverage report
```

### Test Coverage
- ✅ Exception handling (11 tests)
- ✅ Configuration management (7 tests)
- ✅ Inference engine (2 tests)
- ✅ Memory system (2 tests)

**Total: 22 tests | Status: All Passed ✅**

---

## 🔧 Troubleshooting

### Qdrant Lock File Error
```
RuntimeError: Storage folder is already accessed by another instance
```
**Solusi:** System akan auto-cleanup. Jika masih error:
```bash
rm -rf qdrant_db/.lock
```

### Model Download Gagal
```bash
# Download manual ke folder models
mkdir -p models
# Gunakan Aron Hub
aron hub
# Pilih model dan download
```

### Circuit Breaker Aktif
Jika muncul "Circuit Breaker: Terlalu banyak kegagalan":
- Periksa command yang dijalankan
- Pastikan permissions cukup
- Restart sesi dengan `/quit` lalu `aron`

---

## 📖 Dokumentasi Lengkap

- [Wiki](https://github.com/initHD3v/CodeAron/wiki)
- [Configuration Guide](https://github.com/initHD3v/CodeAron/wiki/Configuration)
- [Vision Engine Usage](https://github.com/initHD3v/CodeAron/wiki/Vision)
- [Troubleshooting](https://github.com/initHD3v/CodeAron/wiki/Troubleshooting)

---

<details>
<summary><b>🏮 Filosofi Nama: Mengapa "Aron"?</b></summary>
<br>

Diambil dari kearifan lokal **Suku Karo**, ***Aron*** merujuk pada kelompok kerja tradisional yang berlandaskan semangat kolaborasi dan kebersamaan.

Filosofi ini menjadi identitas inti CodeAron:
- **Solidaritas Digital:** Kolaborasi harmonis antara pengembang dan AI dalam satu visi.
- **Efisiensi Kolektif:** Aron hadir sebagai rekan yang membantu "menanam" logika dan "memanen" solusi secara cepat dan tepat (Sat-Set).
- **Kemandirian:** Mengedepankan prinsip kerja lokal yang tangguh—ketajaman analitis AI yang sepenuhnya berada di bawah kendali Anda.

**CodeAron** adalah jembatan antara nilai luhur tradisi dan kemajuan teknologi; membuktikan bahwa inovasi terbaik lahir dari semangat kebersamaan.

</details>

---

<div align="center">
  <p><i>"Privasi Total, Performa Tanpa Batas."</i></p>
  <sub><b>v0.3.0</b> | Dibuat dengan ❤️ untuk komunitas Developer Indonesia oleh <b>initHD3v</b></sub>
</div>
