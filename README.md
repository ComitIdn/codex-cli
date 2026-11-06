# 🤖 Codex Universal CLI & Studio v4.0

Asisten AI Coding, Terminal & Engineering Full-Stack untuk **Android Termux, Windows (PowerShell & CMD), Linux, macOS, dan Visual Studio Code**.

---

## 🚀 3 Cara Menggunakan Codex

### 1. 📱 Mode GUI Visual (Android & Laptop Browser)
Codex dilengkapi Web GUI modern, responsif, dan bertema gelap (Dark Mode) yang dapat dibuka langsung di browser HP maupun Laptop:

```bash
# Jalankan GUI di Termux atau Windows/Linux:
codex --gui
```
* **Di HP (Android):** Browser Chrome akan otomatis terbuka mengarah ke `http://127.0.0.1:5000`.
* **Di Laptop (Windows/PC):** Browser default akan otomatis terbuka menampilkan antarmuka visual mirip ChatGPT / Claude Studio.

---

### 2. 💻 Mode Visual Studio Code (VS Code Integration)
Anda bisa menggunakan Codex langsung di dalam VS Code dengan **2 metode**:

#### Metode A: Tampilan Panel GUI Langsung di VS Code
1. Jalankan `codex --gui` di terminal terintegrasi VS Code (`Ctrl + ~`).
2. Di VS Code, tekan **`Ctrl + Shift + P`** (atau `Cmd + Shift + P` di Mac).
3. Ketik dan pilih: **`Simple Browser: Show`**.
4. Masukkan URL: `http://127.0.0.1:5000`.
5. Panel AI Codex akan langsung muncul di samping editor kode Anda!

#### Metode B: Menggunakan Ekstensi AI VS Code (Continue / CodeGPT)
Codex menyediakan server API yang kompatibel dengan format OpenAI (`/v1/chat/completions`).
1. Pasang ekstensi **[Continue](https://continue.dev)** atau **CodeGPT** dari VS Code Marketplace.
2. Di pengaturan ekstensi `config.json`, tambahkan Codex sebagai provider lokal:
```json
{
  "models": [
    {
      "title": "Codex AI Local",
      "provider": "openai",
      "model": "codex-ai",
      "apiBase": "http://127.0.0.1:5000/v1"
    }
  ]
}
```
Sekarang Anda bisa memakai fitur *autocomplete*, *inline edit*, dan *code explanation* asli VS Code langsung menggunakan otak Codex!

---

### 3. ⚡ Mode Terminal CLI Cepat
```bash
# Tanya langsung atau buat file:
codex "buat file hitung.py fungsi tambah"

# Buka mode obrolan interaktif:
codex

# Cek struktur folder proyek:
codex /tree

# Compile otomatis (Maven, Gradle, NPM, Composer, Make):
codex /build
```

---

## 📥 Instalasi di Laptop / Komputer Baru

### Di Windows (PowerShell / CMD)
```powershell
curl -O https://raw.githubusercontent.com/ComitIdn/codex-cli/main/codex.py
python codex.py --gui
```

### Di Linux / macOS
```bash
curl -sLO https://raw.githubusercontent.com/ComitIdn/codex-cli/main/codex.py
chmod +x codex.py
sudo mv codex.py /usr/local/bin/codex
codex --gui
```
