# 🤖 Codex Universal CLI

Asisten AI Coding & Terminal Multi-Platform cerdas untuk **Android Termux, Linux, Windows (PowerShell & CMD), dan macOS**.

## 🌟 Fitur Utama
1. **Multi-Platform Native:** Otomatis mendeteksi sistem operasi (Windows CMD/PowerShell, Linux, Termux, macOS) dan menyesuaikan sintaks perintah terminal yang dihasilkan.
2. **Auto-Read File:** Cukup sebutkan nama file (misal: `codex "periksa app.py dan perbaiki bug"`), Codex akan otomatis membaca isi file tersebut ke dalam konteks AI.
3. **Auto-Create File:** Minta Codex membuat file (misal: `codex "buat file hitung.py fungsi tambah"`), file akan langsung tersimpan secara fisik.
4. **Interactive Command Execution:** Rekomendasi perintah terminal dapat langsung dieksekusi dengan satu konfirmasi `[y/N]`.
5. **Dual Backend Engine:**
   - **Offline / Lokal:** Mendukung `llama.cpp` / `llama-server` (Termux & PC) dan `Ollama` (`ollama run qwen2.5-coder`).
   - **Online / Cloud:** Otomatis menggunakan `GITHUB_TOKEN` jika offline engine tidak aktif.

---

## 💻 Cara Install & Menggunakan di Laptop / Komputer

### 1. Di Windows (PowerShell / CMD)
Pastikan Python 3 sudah terpasang di Windows.

```powershell
# 1. Download file codex.py
curl -O https://raw.githubusercontent.com/ComitIdn/codex-cli/main/codex.py

# 2. (Opsional) Jika ingin menggunakan AI lokal di Windows, pasang Ollama:
# Download dari https://ollama.com lalu jalankan:
# ollama run qwen2.5-coder

# 3. Jalankan Codex di Windows:
python codex.py "buatkan script powershell untuk monitor cpu"

# Atau masuk ke mode interaktif chat:
python codex.py
```

### 2. Di Linux / macOS
```bash
# 1. Download & beri izin eksekusi
curl -sLO https://raw.githubusercontent.com/ComitIdn/codex-cli/main/codex.py
chmod +x codex.py
sudo mv codex.py /usr/local/bin/codex

# 2. Jalankan kapan saja:
codex "buatkan script bash backup"
codex
```

### 3. Di Android Termux
Sudah terpasang secara otomatis! Cukup ketik:
```bash
codex "pertanyaan atau kode"
# atau
codex
```
