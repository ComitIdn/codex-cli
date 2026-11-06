#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Universal CLI v4.0 - Full-Stack AI Engineer with Web GUI & VS Code Integration
Mendukung: Android Termux, Windows (CMD & PowerShell), Linux, macOS
Akses: CLI Terminal, Web GUI (Browser HP & Laptop), dan VS Code Extension API
"""

import sys
import os
import json
import re
import platform
import subprocess
import pathlib
import urllib.request
import urllib.error
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==================== DETEKSI SISTEM ====================
OS_TYPE = platform.system()
IS_TERMUX = "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")
IS_WINDOWS = OS_TYPE == "Windows"

if IS_TERMUX:
    PLATFORM_NAME = "Android (Termux)"
    DEFAULT_PKG_MGR = "pkg / apt"
elif IS_WINDOWS:
    PLATFORM_NAME = "Windows (PowerShell / CMD)"
    DEFAULT_PKG_MGR = "winget / choco / pip"
elif OS_TYPE == "Darwin":
    PLATFORM_NAME = "macOS"
    DEFAULT_PKG_MGR = "brew"
else:
    PLATFORM_NAME = "Linux"
    DEFAULT_PKG_MGR = "apt / dnf / pacman"

if IS_WINDOWS and os.name == 'nt':
    os.system('')

C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_DIM = "\033[90m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

LOCAL_API_URL = os.environ.get("CODEX_LOCAL_URL", "http://127.0.0.1:8080/v1/chat/completions")
OLLAMA_API_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))

# ==================== BACKEND AI ====================
def detect_active_backend():
    try:
        req = urllib.request.Request("http://127.0.0.1:8080/health", headers={"User-Agent": "CodexCLI"})
        with urllib.request.urlopen(req, timeout=0.8) as r:
            if r.status == 200:
                return "local_llama", LOCAL_API_URL, None
    except Exception:
        pass

    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "CodexCLI"})
        with urllib.request.urlopen(req, timeout=0.8) as r:
            if r.status == 200:
                return "local_ollama", OLLAMA_API_URL, "qwen2.5-coder:latest"
    except Exception:
        pass

    if IS_TERMUX:
        model_path = pathlib.Path.home() / "model.gguf"
        if model_path.exists():
            import time
            subprocess.Popen(
                ["llama-server", "-m", str(model_path), "--port", "8080", "--host", "127.0.0.1", "-c", "2048", "-t", "4", "--poll", "0"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            for _ in range(12):
                time.sleep(0.8)
                try:
                    req = urllib.request.Request("http://127.0.0.1:8080/health", headers={"User-Agent": "CodexCLI"})
                    with urllib.request.urlopen(req, timeout=0.8) as r:
                        if r.status == 200:
                            return "local_llama", LOCAL_API_URL, None
                except Exception:
                    pass
            return "local_llama", LOCAL_API_URL, None

    if GITHUB_TOKEN:
        return "cloud_github", "https://models.github.ai/inference/chat/completions", "gpt-4o-mini"

    return "none", None, None

def query_ai(messages, backend_type, endpoint, model_name=None):
    payload = {
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.4,
        "repeat_penalty": 1.15,
        "stop": ["<|im_end|>", "<|endoftext|>", "User:", "Pengguna:"]
    }
    if model_name:
        payload["model"] = model_name

    headers = {"Content-Type": "application/json"}
    if backend_type == "cloud_github":
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()

def get_system_prompt():
    return {
        "role": "system",
        "content": (
            f"Kamu adalah Codex AI Full-Stack Software Engineer, Network Engineer & DevOps Master. "
            f"Platform: {PLATFORM_NAME}. Package Manager: {DEFAULT_PKG_MGR}. OS: {OS_TYPE}. "
            f"Keahlian penuh mencakup: HTML5, CSS3, JS/TS, Python, Java, PHP (XAMPP/Laragon/Laravel), SQL/MySQL, C/C++, Go, Rust, JSON. "
            f"Keahlian Khusus Jaringan & MikroTik: Sangat menguasai library PHP 'comitidn/routeros-api' untuk berkomunikasi dengan MikroTik RouterOS melalui port API 8728 (atau 8729 SSL). "
            f"Mampu membuat skrip monitoring trafik interface, manajemen Hotspot voucher/users, PPPoE Secrets, Simple Queues bandwidth, IP Address, dan resource router menggunakan class RouterOSAPI. "
            f"Untuk instalasi via Composer gunakan: composer require comitidn/routeros-api:dev-dev-main. "
            f"Mampu mengedit, merapikan, memilih arsitektur, mendebug error, membuild, dan menganalisa sistem. "
            f"Berikan jawaban profesional, kode siap pakai, dan perintah shell yang tepat."
        )
    }

# ==================== WEB GUI (HTML/CSS/JS) ====================
HTML_GUI = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codex AI Studio</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-dark: #1e293b;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --border: #334155;
            --code-bg: #090d16;
            --user-bubble: #1e3a8a;
            --bot-bubble: #1e293b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        #sidebar { width: 260px; background: #0b1120; border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        #main { flex: 1; display: flex; flex-direction: column; height: 100%; position: relative; }
        header { padding: 14px 20px; background: var(--panel-dark); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .brand { font-size: 1.15rem; font-weight: 700; color: var(--accent); display: flex; align-items: center; gap: 8px; }
        .status-badge { font-size: 0.75rem; background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 999px; }
        #chat-flow { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 18px; }
        .msg { max-width: 85%; padding: 14px 18px; border-radius: 12px; line-height: 1.6; font-size: 0.95rem; word-break: break-word; }
        .msg.user { align-self: flex-end; background: var(--user-bubble); color: #fff; border-bottom-right-radius: 2px; }
        .msg.bot { align-self: flex-start; background: var(--bot-bubble); border: 1px solid var(--border); border-bottom-left-radius: 2px; }
        pre { background: var(--code-bg); padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; border: 1px solid var(--border); font-family: monospace; font-size: 0.9rem; }
        code { color: #38bdf8; font-family: monospace; }
        #input-box { padding: 16px; background: var(--panel-dark); border-top: 1px solid var(--border); display: flex; gap: 12px; }
        textarea { flex: 1; background: var(--bg-dark); color: var(--text-main); border: 1px solid var(--border); border-radius: 8px; padding: 12px; font-size: 0.95rem; resize: none; height: 52px; outline: none; }
        textarea:focus { border-color: var(--accent); }
        button { background: var(--accent); color: #000; border: none; padding: 0 20px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { background: var(--accent-hover); }
        .presets { padding: 10px 20px; display: flex; gap: 8px; overflow-x: auto; background: #131d31; }
        .preset-btn { background: #1e293b; color: var(--text-dim); border: 1px solid var(--border); padding: 5px 12px; border-radius: 16px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; }
        .preset-btn:hover { color: #fff; border-color: var(--accent); }
        @media (max-width: 768px) {
            #sidebar { display: none; }
            .msg { max-width: 95%; }
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <div style="padding: 20px; border-bottom: 1px solid var(--border);">
            <h3 style="color: var(--accent);">🛠️ Codex Tools</h3>
            <p style="font-size: 0.8rem; color: var(--text-dim); margin-top: 4px;">Platform: __PLATFORM__</p>
        </div>
        <div style="padding: 16px; flex: 1; overflow-y: auto;">
            <p style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 8px;">Aksi Cepat</p>
            <button class="preset-btn" style="width: 100%; margin-bottom: 8px; text-align: left;" onclick="sendQuick('periksa struktur folder /tree')">📂 Lihat Struktur /tree</button>
            <button class="preset-btn" style="width: 100%; margin-bottom: 8px; text-align: left;" onclick="sendQuick('buat file db.php koneksi PDO MySQL XAMPP Laragon')">🗄️ Koneksi MySQL (PDO)</button>
            <button class="preset-btn" style="width: 100%; margin-bottom: 8px; text-align: left;" onclick="sendQuick('analisa dan rapikan file proyek ini')">🧹 Rapikan & Optimasi</button>
            <button class="preset-btn" style="width: 100%; margin-bottom: 8px; text-align: left;" onclick="sendQuick('buat file index.html dashboard modern responsif')">🌐 Scaffold HTML5/CSS</button>
        </div>
    </div>
    <div id="main">
        <header>
            <div class="brand">🤖 Codex AI Studio <span style="font-size: 0.75rem; color: var(--text-dim);">v4.0</span></div>
            <div class="status-badge">● Sistem Aktif (__BACKEND__)</div>
        </header>
        <div class="presets">
            <span class="preset-btn" onclick="sendQuick('buat file mikrotik.php koneksi ke routeros menggunakan comitidn/routeros-api untuk cek resource dan interface')">📡 MikroTik API (comitidn)</span>
            <span class="preset-btn" onclick="sendQuick('buatkan CRUD PHP MySQL lengkap')">⚡ CRUD PHP</span>
            <span class="preset-btn" onclick="sendQuick('buat script python scraper data json')">🐍 Python JSON</span>
            <span class="preset-btn" onclick="sendQuick('buatkan REST API Java Spring Boot')">☕ Java Spring</span>
            <span class="preset-btn" onclick="sendQuick('bagaimana debug error connection refused xampp port 3306')">🔧 Debug XAMPP 3306</span>
        </div>
        <div id="chat-flow">
            <div class="msg bot">
                Halo! Saya <b>Codex AI</b>. Saya siap membantu coding, debug, edit file, dan manajemen database langsung lewat tampilan visual ini atau terminal Anda. Silakan ketik perintah atau pertanyaan Anda!
            </div>
        </div>
        <div id="input-box">
            <textarea id="prompt" placeholder="Tulis instruksi koding, debug error, atau buat file... (Tekan Enter)"></textarea>
            <button id="send-btn" onclick="sendPrompt()">Kirim</button>
        </div>
    </div>
    <script>
        const promptInput = document.getElementById("prompt");
        const chatFlow = document.getElementById("chat-flow");

        promptInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendPrompt();
            }
        });

        function sendQuick(text) {
            promptInput.value = text;
            sendPrompt();
        }

        async function sendPrompt() {
            const text = promptInput.value.trim();
            if (!text) return;
            promptInput.value = "";

            appendMsg(text, "user");
            const loadingMsg = appendMsg("⏳ Sedang memproses & menganalisa...", "bot");

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: text })
                });
                const data = await res.json();
                loadingMsg.innerHTML = formatReply(data.reply);
            } catch (err) {
                loadingMsg.innerHTML = "❌ Gagal terhubung ke server: " + err.message;
            }
            chatFlow.scrollTop = chatFlow.scrollHeight;
        }

        function appendMsg(content, sender) {
            const div = document.createElement("div");
            div.className = "msg " + sender;
            div.textContent = content;
            chatFlow.appendChild(div);
            chatFlow.scrollTop = chatFlow.scrollHeight;
            return div;
        }

        function formatReply(raw) {
            let html = raw.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            html = html.replace(/```(?:([a-zA-Z0-9_-]+)\n)?([\\s\\S]*?)```/g, function(match, lang, code) {
                return `<pre><code>${code.trim()}</code></pre>`;
            });
            return html.replace(/\\n/g, "<br>");
        }
    </script>
</body>
</html>
"""

# ==================== HTTP SERVER UNTUK GUI & VS CODE ====================
class CodexHttpServer(BaseHTTPRequestHandler):
    b_type = "none"
    b_endpoint = ""
    b_model = None

    def log_message(self, format, *args):
        pass  # Heningkan log default agar terminal tetap rapi

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        # 1. Endpoint Web GUI
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            gui_html = HTML_GUI.replace("__PLATFORM__", PLATFORM_NAME).replace("__BACKEND__", self.b_type.upper())
            self.wfile.write(gui_html.encode("utf-8"))
            return

        # 2. Endpoint VS Code Extension (OpenAI-Compatible Models List)
        if self.path in ["/v1/models", "/api/v1/models"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            res = {
                "object": "list",
                "data": [
                    {"id": "codex-ai", "object": "model", "owned_by": "codex-universal"},
                    {"id": "qwen2.5-coder", "object": "model", "owned_by": "codex-universal"}
                ]
            }
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body) if body else {}

        # 1. API Obrolan Web GUI
        if self.path == "/api/chat":
            prompt = data.get("prompt", "")
            messages = [get_system_prompt(), {"role": "user", "content": prompt}]
            try:
                reply = query_ai(messages, self.b_type, self.b_endpoint, self.b_model)
            except Exception as e:
                reply = f"Error pemrosesan AI: {e}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))
            return

        # 2. Endpoint OpenAI-Compatible untuk VS Code (Continue / CodeGPT)
        if self.path in ["/v1/chat/completions", "/api/v1/chat/completions"]:
            incoming_messages = data.get("messages", [])
            messages = [get_system_prompt()] + incoming_messages
            try:
                reply = query_ai(messages, self.b_type, self.b_endpoint, self.b_model)
            except Exception as e:
                reply = f"Error: {e}"

            resp = {
                "id": "chatcmpl-codex",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": reply},
                    "finish_reason": "stop"
                }]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        # Support CORS untuk VS Code extension
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

def start_gui_server(b_type, b_endpoint, b_model, port=5000):
    CodexHttpServer.b_type = b_type
    CodexHttpServer.b_endpoint = b_endpoint
    CodexHttpServer.b_model = b_model

    server = HTTPServer(("0.0.0.0", port), CodexHttpServer)
    url = f"http://127.0.0.1:{port}"

    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║      🚀 CODEX STUDIO GUI & VS CODE SERVER AKTIF             ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚══════════════════════════════════════════════════════════════╝{C_RESET}")
    print(f"📱 Web GUI Browser   : {C_GREEN}{C_BOLD}{url}{C_RESET}")
    print(f"💻 VS Code API Base  : {C_BLUE}{C_BOLD}{url}/v1{C_RESET}")
    print(f"{C_DIM}Tekan Ctrl+C di terminal untuk menghentikan server.{C_RESET}\n")

    # Otomatis buka browser di HP / PC
    if IS_TERMUX:
        subprocess.run(f"termux-open-url {url} 2>/dev/null || am start -a android.intent.action.VIEW -d '{url}' >/dev/null 2>&1", shell=True)
    else:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}Server GUI dihentikan.{C_RESET}")
        server.server_close()

# ==================== MAIN ====================
def main():
    b_type, b_endpoint, b_model = detect_active_backend()
    if b_type == "none":
        print(f"{C_YELLOW}⚠️ Tidak ada engine AI aktif.{C_RESET}")
        sys.exit(1)

    # 1. Jalankan Mode GUI / Server jika ada flag --gui atau --web atau --server
    if any(arg in sys.argv for arg in ["--gui", "-g", "--web", "--server", "-s"]):
        port = 5000
        for i, a in enumerate(sys.argv):
            if a in ["--port", "-p"] and i + 1 < len(sys.argv):
                try: port = int(sys.argv[i+1])
                except ValueError: pass
        start_gui_server(b_type, b_endpoint, b_model, port)
        return

    # Periksa perintah khusus /mikrotik
    if len(sys.argv) > 1 and sys.argv[1] == "/mikrotik":
        print(f"\n{C_CYAN}{C_BOLD}📡 Menyiapkan Proyek MikroTik PHP (comitidn/routeros-api)...{C_RESET}")
        cmd = "composer require comitidn/routeros-api:dev-dev-main"
        print(f"{C_YELLOW}Perintah:{C_RESET} {cmd}")
        pilihan = input(f"{C_BOLD}Jalankan composer require sekarang? [Y/n]: {C_RESET}").strip().lower()
        if pilihan in ["", "y", "ya", "yes"]:
            subprocess.run(cmd, shell=True)
            print(f"\n{C_GREEN}✓ comitidn/routeros-api berhasil dipasang!{C_RESET}")
        return

    # 2. Mode One-shot CLI arguments
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        messages = [get_system_prompt(), {"role": "user", "content": user_prompt}]
        print(f"{C_DIM}⏳ Sedang memproses ({PLATFORM_NAME})...{C_RESET}")
        try:
            reply = query_ai(messages, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}")
        except Exception as e:
            print(f"{C_YELLOW}Error: {e}{C_RESET}")
        return

    # 3. Mode Interactive REPL Terminal
    print(f"{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║      🤖 CODEX FULL-STACK ENGINEERING CLI v4.0               ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚══════════════════════════════════════════════════════════════╝{C_RESET}")
    print(f"{C_GREEN}Platform :{C_RESET} {PLATFORM_NAME}")
    print(f"{C_BLUE}Tips GUI :{C_RESET} Ketik {C_YELLOW}codex --gui{C_RESET} untuk membuka tampilan grafis di Browser / VS Code.")
    print(f"{C_DIM}Ketik pertanyaan Anda, atau 'exit' untuk keluar.{C_RESET}\n")

    history = [get_system_prompt()]
    while True:
        try:
            prompt = input(f"{C_GREEN}{C_BOLD}Codex [{OS_TYPE}] > {C_RESET}").strip()
            if not prompt: continue
            if prompt.lower() in ["exit", "quit", "q"]: break
            if prompt.lower() in ["--gui", "gui", "web"]:
                start_gui_server(b_type, b_endpoint, b_model, 5000)
                break

            history.append({"role": "user", "content": prompt})
            print(f"{C_DIM}⏳ Berpikir & Menganalisa...{C_RESET}")
            reply = query_ai(history, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}\n")
            history.append({"role": "assistant", "content": reply})

            if len(history) > 11:
                history = [history[0]] + history[-10:]
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
