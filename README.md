# CodeAron 🤖

**CodeAron** adalah AI Coding Assistant berbasis CLI yang berjalan sepenuhnya secara lokal (offline) dan dioptimalkan khusus untuk **MacBook Pro Apple Silicon (M1-M4)**. Didesain dengan fokus utama pada pengembangan **Flutter** menggunakan pendekatan *Clean Architecture*.

---

## ✨ Fitur Unggulan

- 🏠 **100% Lokal & Privat:** Tidak ada kode yang dikirim ke cloud. Privasi data Anda terjamin sepenuhnya.
- ⚡ **Optimasi Apple Silicon:** Menggunakan framework **MLX** dari Apple Research untuk performa maksimal pada Unified Memory M1/M2/M3/M4.
- 🛠️ **Flutter & Clean Architecture Expert:** Memahami struktur layer (Domain, Data, Presentation) dan pola desain Flutter (BLoC, Provider, dsb).
- 🛡️ **Safe-Transaction Engine:** Integrasi Git otomatis (GitGuard) yang membuat checkpoint sebelum melakukan perubahan kode, serta validasi otomatis menggunakan `dart analyze`.
- 👁️ **Aron Vision:** Mampu menganalisis desain UI (JPG/PNG) dan memberikan saran implementasi kode (Fase pengembangan).
- 🔄 **Smart Update & Reload:** Mendeteksi pembaruan dari GitHub dan mampu melakukan hot-restart aplikasi secara instan.
- 🇮🇩 **Linguistic Engine:** Interaksi natural dalam Bahasa Indonesia yang profesional namun santai.

---

## 🚀 Instalasi Cepat

### Prasyarat
- macOS (Apple Silicon M1/M2/M3/M4)
- Python 3.11+
- Flutter SDK & Git

### Langkah Instalasi
1. **Clone Repositori:**
   ```bash
   git clone https://github.com/initHD3v/CodeAron.git
   cd CodeAron
   ```

2. **Setup Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Global Access (Opsional):**
   Tambahkan fungsi berikut ke `.zshrc` Anda:
   ```bash
   aron() { PYTHONPATH=/path/to/CodeAron /path/to/CodeAron/.venv/bin/python /path/to/CodeAron/src/main.py "$@"; }
   ```

---

## 🎮 Cara Penggunaan

Cukup ketik `aron` di terminal Anda di dalam direktori proyek Flutter mana pun.

### Perintah Utama (Inside Chat):
- `/model` : Mengelola model AI (Download/Switch).
- `/update`: Menarik pembaruan terbaru dari GitHub.
- `/reload`: Memuat ulang aplikasi menggunakan kode lokal terbaru.
- `/quit`  : Keluar dari aplikasi.

---

## 🏗️ Arsitektur Sistem

CodeAron dibangun dengan modularitas tinggi:
- **Core Orchestrator:** Mengelola transisi state mesin (DFA).
- **Inference Engine:** Abstraksi pemrosesan LLM lokal berbasis MLX.
- **Context Manager:** Mengambil data nyata proyek (File Tree & Pubspec) untuk analisis akurat.
- **GitGuard:** Menjamin keamanan integritas kode proyek user.

---

## 🛠️ Roadmap Pengembangan
- [x] **Fase 0-2:** Dasar Infrastruktur & Integrasi Intelligence (DeepSeek-Coder).
- [x] **Fase 3:** Context & Memory dasar (Real Project Analysis).
- [ ] **Fase 4:** Real Coding & Patching (Auto-writing files).
- [ ] **Fase 5:** Vision Engine (Analisis Gambar).
- [ ] **Fase 6:** Final Polishing & Localization.

---

## 📄 Lisensi
[TBD] - Dikembangkan oleh initHD3v & Aron.
