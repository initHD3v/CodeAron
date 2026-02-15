# CodeAron 🤖

**CodeAron** adalah asisten coding berbasis AI yang berjalan 100% secara lokal di mesin Apple Silicon (M1-M4). Dirancang untuk menjadi partner diskusi yang cerdas, responsif, dan adaptif bagi para developer.

---

## ✨ Fitur Unggulan

- **🚀 Smart Intent Detection**: Aron merespon seketika untuk obrolan santai dan hanya menganalisis proyek saat mendeteksi niat coding (sangat cepat & efisien).
- **🌊 Real-time Streaming**: Jawaban muncul kata demi kata secara instan, memberikan pengalaman interaksi yang hidup seperti `gemini-cli`.
- **🧠 Conversational Memory**: Aron memiliki ingatan sesi, sehingga Anda bisa berdiskusi secara natural tanpa perlu mengulang konteks.
- **📂 Adaptive Project Context**: Secara otomatis mendeteksi tipe proyek (Flutter, Python, Node.js) dan menganalisis file yang relevan secara cerdas.
- **💾 Auto-Writing & Patching**: Aron tidak hanya memberi saran, tapi bisa membuat atau merubah file secara otomatis melalui instruksi chat.
- **🔍 Typo-Tolerant Commands**: Mengenali dan menyarankan perintah yang benar jika Anda salah mengetik (misal: `/modle` -> `/model`).
- **🔄 In-App Updater**: Perbarui CodeAron ke versi terbaru langsung dari terminal dengan perintah `/update`.

---

## 🛠️ Instalasi & Persiapan

### Prasyarat
- macOS dengan Apple Silicon (M1, M2, M3, M4).
- Python 3.11+.
- [MLX](https://github.com/ml-explore/mlx) installed.

### Cara Menjalankan
1. Clone repositori ini:
   ```bash
   git clone https://github.com/initHD3v/CodeAron.git
   cd CodeAron
   ```
2. Setup Virtual Environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```
3. Jalankan CodeAron:
   ```bash
   python src/main.py
   ```

---

## ⌨️ Perintah Tersedia

| Perintah | Deskripsi |
| :--- | :--- |
| `/model` | Kelola dan pilih model AI lokal. |
| `/update` | Cek dan instal pembaruan dari GitHub secara otomatis. |
| `/clear` | Bersihkan memori percakapan sesi saat ini. |
| `/reload` | Muat ulang aplikasi dari kode lokal tanpa keluar. |
| `/quit` | Keluar dari aplikasi. |

---

## 🎯 Visi Pengembangan
CodeAron dikembangkan untuk membuktikan bahwa asisten coding yang kuat tidak harus bergantung pada cloud. Dengan memanfaatkan kekuatan chip Apple Silicon dan framework MLX, CodeAron menghadirkan privasi total dan kecepatan maksimal bagi developer.

---
**v0.2.0** | Dibuat dengan ❤️ untuk komunitas Developer Indonesia.
