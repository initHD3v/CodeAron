<div align="center">

# 🤖 CodeAron
### **Partner Ngoding Paling "Sat-Set" & 100% Lokal di Apple Silicon**

<p align="center">
  <img src="https://img.shields.io/badge/PLATFORM-macOS%20SILICON-000000?style=for-the-badge&logo=apple&logoColor=white" />
  <img src="https://img.shields.io/badge/ENGINE-MLX%20LM-FF4B11?style=for-the-badge" />
  <img src="https://img.shields.io/badge/VERSION-0.4.0-00FF00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MODEL-QWEN%2FDEEPSEEK-0052FF?style=for-the-badge&logo=deepseek&logoColor=white" />
</p>

---

**CodeAron** adalah asisten pengembang berbasis AI yang berjalan 100% secara lokal. Aron dirancang untuk menjadi **Senior Architect** mandiri yang memiliki integritas data tinggi, tidak pernah berhalusinasi, dan proaktif dalam menganalisis serta memodifikasi kode langsung di mesin Anda.

[Fitur Utama](#-fitur-utama) • [Command](#-command) • [Skill System](#-skill-system) • [Konfigurasi](#-konfigurasi) • [Instalasi](#-instalasi) • [Arsitektur](#-arsitektur)

</div>

## 🎯 Apa yang Baru di v0.4.0?

### ✨ Fitur Baru
- **🧠 ChatML Prompt Template** — Format Qwen2.5 yang benar (bukan LLaMA [INST])
- **🎯 Auto Task Detection** — Otomatis atur temperature (coding/analysis/chat/planning)
- **🧪 Benchmark Tool** — Test 7 metrik: speed, correctness, RAM, context, multilingual
- **🔧 Skill System** — Auto-trigger skill: review, explain, test, refactor
- **📋 Few-Shot Examples** — System prompt dengan contoh format response yang benar
- **🛡️ Output Validation** — Auto-fix: repetition, hallucination, broken tokens
- **📚 Context Management** — Token-aware compression, chat panjang tetap stabil

### 🐛 Bug Fixes
- Fixed tree-sitter parser compatibility (downgrade ke 0.21.3)
- Fixed skill auto-trigger (tidak trigger untuk general knowledge)
- Fixed prompt template inconsistency — sekarang pakai ChatML format
- Fixed output yang mengandung ChatML artifacts
- Improved error handling dan self-correction

---

## 🚀 Fitur Utama

### 🧠 **Senior Architect Persona**
Aron bukan sekadar chatbot. Ia memiliki kepribadian profesional yang menggunakan prinsip **"Check Before Speak"**. Ia akan melakukan observasi struktur proyek (`ls`) dan membaca konten file (`cat`) secara otomatis sebelum memberikan opini teknis.

### 🛡️ **Anti-Hallucination Protocol**
- **Blind Observation:** Aron menyadari ia "tuna netra" tanpa perintah shell. Wajib validasi empiris.
- **Deterministic Inference:** Temperatur otomatis sesuai task (0.1-0.7) untuk akurasi optimal.
- **Output Validation:** Auto-detect repetition, broken tokens, dan hallucinated paths.
- **Strict Stop Sequences:** Berhenti seketika setelah prediksi selesai.

### 🎯 **Auto Task Detection** (BARU!)
Aron otomatis detect jenis pertanyaan dan atur temperature:

| Task Type | Temperature | Contoh |
|-----------|-------------|--------|
| Coding | 0.2 | "buatkan fungsi sorting" |
| Analysis | 0.3 | "jelaskan tentang Python" |
| Planning | 0.4 | "desain arsitektur project" |
| Chat | 0.7 | "hai", "apa kabar" |
| Shell | 0.1 | "command untuk install" |

### 📋 **Skill System** (BARU!)
Aron punya skill yang bisa auto-trigger dari intent:

| Skill | Trigger | Fungsi |
|-------|---------|--------|
| `/skill review` | "review", "audit", "cek bug" | Code review mendalam |
| `/skill explain` | "jelaskan", "apa itu", "how does" | Penjelasan detail |
| `/skill test` | "test", "unit test", "buatkan test" | Generate test files |
| `/skill refactor` | "refactor", "optimize", "bersihkan" | Refactor kode |

### 🧪 **Benchmark Tool** (BARU!)
Test performa Aron dengan command `/benchmark`:

```
🧪 Starting CodeAron Benchmark...

  CodeAron Benchmark Report
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Speed (Code)    30.9 t/s     100%
  ✅ Speed (Analysis) 41.8 t/s    100%
  ✅ Correctness     3/3 checks   100%
  ✅ Context         Yes          90%
  ✅ RAM             0.6GB        100%
  ⚠️ Multilingual    20.1 t/s     60%
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Overall Score: 88/100  [Grade: A]
  Total Time:  34.6s
```

### 🔒 **Circuit Breaker & Rate Limiting**
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
| `/benchmark` | Jalankan benchmark performa AI (NEW!) |
| `/hub` | Kelola model AI (Download/List) |
| `/update` | Update CodeAron ke versi terbaru |
| `/undo` | Rollback perubahan terakhir |
| `/checkpoint` | Git commit dengan pesan custom |
| `/skill [name]` | List atau jalankan skill (NEW!) |
| `/vision [path]` | Analisis gambar |
| `/quit` | Keluar dari sesi |

### Contoh Skill Usage
```bash
# List semua skill
/skill

# Execute skill dengan target
/skill review src/orchestrator.py
/skill explain utils.py
/skill test src/main.py

# Auto-trigger dari chat biasa
"review file ini"          → auto trigger review skill
"jelaskan fungsi ini"       → auto trigger explain skill
"buatkan unit test"         → auto trigger test skill
```

### Contoh Benchmark
```bash
# Di dalam sesi Aron
/benchmark
# Akan menjalankan 7 test dan menampilkan report
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
├── 🧠 src/core/           # Orchestrator, Config, Benchmark
│   ├── orchestrator.py    # Main controller dengan circuit breaker
│   ├── benchmark.py       # Benchmark suite (7 tests)
│   ├── skill_manager.py   # Skill definitions
│   ├── skill_executor.py  # Skill execution engine
│   ├── config_manager.py  # Project config manager
│   ├── exceptions.py      # Custom exceptions
│   └── prompt_templates.py # ChatML templates (NEW!)
├── 🤖 src/llm/            # MLX Inference Engine
├── 💾 src/memory/         # Vector Store & RAG
├── 🛠️ src/tools/          # Tools & Bridges
│   ├── vision_engine.py   # Vision AI untuk gambar
│   └── ...
├── 📋 src/skills/         # Skill Definitions (NEW!)
│   ├── review.md
│   ├── explain.md
│   ├── test.md
│   └── refactor.md
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

# Restart Aron
aron
```

---

## 🧪 Benchmark

CodeAron punya built-in benchmark untuk mengukur performa. Jalankan dengan `/benchmark` di sesi interaktif.

### Test yang Dijalankan

| Test | Metrik | Target |
|------|--------|--------|
| **Speed (Coding)** | Tokens/sec | ≥ 15 t/s |
| **Speed (Analysis)** | Tokens/sec | ≥ 15 t/s |
| **Speed (Chat)** | Tokens/sec | ≥ 15 t/s |
| **Code Correctness** | 3 checks (def, base, logic) | 3/3 |
| **Context Memory** | Multi-turn recall | Yes |
| **RAM Usage** | Model memory footprint | ≤ 4GB |
| **Multilingual (ID)** | Bahasa Indonesia | ID words ≥ 3 |

### Contoh Output
```
  Overall Score: 88/100  [Grade: A]
  Total Time:  34.6s
```

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

### Tree-Sitter Parser Error
```
✗ dart (skip)
✗ python (skip)
...
```
**Solusi:** Pastikan versi tree-sitter kompatibel:
```bash
pip install tree-sitter==0.21.3 tree-sitter-languages==1.10.2
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
- [Skill System](https://github.com/initHD3v/CodeAron/wiki/Skills)
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
  <sub><b>v0.4.0</b> | Dibuat dengan ❤️ untuk komunitas Developer Indonesia oleh <b>initHD3v</b></sub>
</div>
