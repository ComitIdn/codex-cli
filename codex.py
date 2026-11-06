#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Universal CLI v3.0 - Full-Stack Programming & Engineering Assistant
Mendukung: Termux Android, Windows (CMD & PowerShell), Linux, macOS
Bahasa & Ekosistem: Python, Java, PHP (XAMPP/Laragon/Native), HTML/CSS/JS/TS, 
SQL/MySQL/Postgres/SQLite, C/C++, Go, Rust, JSON/YAML, Docker, dll.
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

# ==================== DETEKSI SISTEM ====================
OS_TYPE = platform.system()
IS_TERMUX = "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")
IS_WINDOWS = OS_TYPE == "Windows"

if IS_TERMUX:
    PLATFORM_NAME = "Android (Termux CLI)"
    DEFAULT_PKG_MGR = "pkg / apt"
elif IS_WINDOWS:
    PLATFORM_NAME = "Windows (PowerShell / CMD)"
    DEFAULT_PKG_MGR = "winget / choco / pip"
elif OS_TYPE == "Darwin":
    PLATFORM_NAME = "macOS (Terminal)"
    DEFAULT_PKG_MGR = "brew"
else:
    PLATFORM_NAME = "Linux (Bash / Zsh)"
    DEFAULT_PKG_MGR = "apt / dnf / pacman"

if IS_WINDOWS and os.name == 'nt':
    os.system('')  # Aktifkan ANSI escape di Windows

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

# ==================== KEMAMPUAN PROJECT & FILE ====================
def get_directory_tree(path=".", max_depth=2):
    """Melihat struktur file & direktori proyek"""
    tree_lines = []
    root_p = pathlib.Path(path)
    ignore = {".git", "node_modules", "vendor", "__pycache__", ".idea", ".vscode", "build", "dist", "target", ".gradle"}
    
    def walk(curr_dir, depth):
        if depth > max_depth:
            return
        try:
            for item in sorted(curr_dir.iterdir()):
                if item.name in ignore:
                    continue
                indent = "  " * depth
                if item.is_dir():
                    tree_lines.append(f"{indent}📁 {item.name}/")
                    walk(item, depth + 1)
                else:
                    tree_lines.append(f"{indent}📄 {item.name}")
        except PermissionError:
            pass

    tree_lines.append(f"📁 {root_p.resolve().name}/")
    walk(root_p, 1)
    return "\n".join(tree_lines[:40])

def detect_project_and_build():
    """Mendeteksi jenis proyek dan perintah build/compile otomatis"""
    cwd = pathlib.Path(".")
    if (cwd / "pom.xml").exists():
        return "Java (Maven)", "mvn clean package"
    if (cwd / "build.gradle").exists() or (cwd / "build.gradle.kts").exists():
        return "Java (Gradle)", "gradle build" if not IS_WINDOWS else ".\\gradlew.bat build"
    if (cwd / "package.json").exists():
        return "Node.js / Web Frontend", "npm install && npm run build"
    if (cwd / "composer.json").exists():
        return "PHP (Composer / Laravel)", "composer install"
    if (cwd / "requirements.txt").exists():
        return "Python", "pip install -r requirements.txt"
    if (cwd / "Makefile").exists():
        return "C/C++ (Make)", "make"
    if (cwd / "CMakeLists.txt").exists():
        return "C/C++ (CMake)", "cmake -B build && cmake --build build"
    if (cwd / "Cargo.toml").exists():
        return "Rust (Cargo)", "cargo build"
    if (cwd / "go.mod").exists():
        return "Go", "go build ."
    return None, None

def read_target_file(prompt: str):
    """Membaca isi file yang disebutkan pengguna"""
    m = re.search(r'(?:periksa|cek|baca|review|edit|ubah|lihat|read|check|debug|analisa|upgrade|rapikan)\s+([A-Za-z0-9_\-./\\]+\.[a-zA-Z0-9]+)', prompt, re.IGNORECASE)
    if m:
        fname = m.group(1)
        p = pathlib.Path(fname)
        if p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                print(f"{C_DIM}📖 Otomatis membaca konteks file: {p.name} ({len(content)} karakter){C_RESET}")
                return f"\n\n[Isi file {p.name}]:\n```{p.suffix.lstrip('.')}\n{content}\n```\n", p
            except Exception as e:
                print(f"{C_YELLOW}Gagal membaca file: {e}{C_RESET}")
    return "", None

def smart_file_manager(prompt: str, reply: str, active_file=None):
    """Menyimpan file baru atau memperbarui (edit) file yang sudah ada"""
    # 1. Mode Edit File yang ada
    if active_file and any(k in prompt.lower() for k in ["edit", "ubah", "ganti", "perbaiki", "update", "rapikan", "upgrade"]):
        code_match = re.search(r'```(?:\w+)?\n(.*?)```', reply, re.DOTALL)
        if code_match:
            new_code = code_match.group(1).strip()
            print(f"\n{C_YELLOW}{C_BOLD}📝 Perubahan terdeteksi untuk file:{C_RESET} {active_file}")
            tanya = input(f"{C_BOLD}Terapkan pembaruan ini ke {active_file.name}? [Y/n]: {C_RESET}").strip().lower()
            if tanya in ["", "y", "ya", "yes"]:
                active_file.write_text(new_code + "\n", encoding="utf-8")
                print(f"{C_GREEN}✓ File {active_file.name} berhasil diperbarui.{C_RESET}")
            return

    # 2. Mode Buat File Baru
    if any(k in prompt.lower() for k in ["buat file", "bikin file", "tulis file", "simpan ke", "create file", "save to"]):
        m = re.search(r'([A-Za-z0-9_\-./\\]+\.(?:py|html|php|java|sql|js|ts|css|json|sh|bat|ps1|md|c|cpp|go|rs|xml|yml|yaml))', prompt)
        if m:
            fname = m.group(1)
            target = pathlib.Path(fname)
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', reply, re.DOTALL)
            content = code_match.group(1) if code_match else reply
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content.strip() + "\n", encoding="utf-8")
            print(f"\n{C_GREEN}💾 File berhasil dibuat:{C_RESET} {target.resolve()}")

def extract_commands(text):
    patterns = [r"```(?:bash|sh|cmd|powershell|bat)\n(.*?)```", r"```\n(.*?)```"]
    cmds = []
    for pat in patterns:
        matches = re.findall(pat, text, re.DOTALL)
        for m in matches:
            lines = [l.strip() for l in m.strip().split("\n") if l.strip() and not l.strip().startswith("#")]
            if lines:
                cmds.extend(lines)
    return cmds

def execute_command_interactive(cmd_str):
    print(f"\n{C_MAGENTA}{C_BOLD}⚡ Rekomendasi Perintah:{C_RESET} {C_YELLOW}{cmd_str}{C_RESET}")
    try:
        pilihan = input(f"{C_BOLD}Eksekusi perintah ini di {PLATFORM_NAME}? [y/N]: {C_RESET}").strip().lower()
        if pilihan in ["y", "ya", "yes"]:
            print(f"{C_DIM}Menjalankan...{C_RESET}\n")
            if IS_WINDOWS:
                subprocess.run(cmd_str, shell=True)
            else:
                subprocess.run(cmd_str, shell=True, executable="/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh")
            print(f"\n{C_GREEN}✓ Selesai.{C_RESET}")
        else:
            print(f"{C_DIM}Dilewati.{C_RESET}")
    except KeyboardInterrupt:
        print(f"\n{C_DIM}Dibatalkan.{C_RESET}")

def get_system_prompt():
    return {
        "role": "system",
        "content": (
            f"Kamu adalah Codex CLI Full-Stack Software Engineer & DevOps Master. "
            f"Lingkungan saat ini: {PLATFORM_NAME}. Package Manager: {DEFAULT_PKG_MGR}. OS: {OS_TYPE}. "
            f"Kemampuan ahli mencakup: "
            f"1. Semua Bahasa: Python, Java (Spring/Maven/Gradle), PHP (Laravel/CodeIgniter/Native), HTML5, CSS3, JS/TS (React/Vue/Node), C/C++, Go, Rust, SQL, JSON, YAML. "
            f"2. Database & Server: XAMPP, Laragon, MySQL, MariaDB, SQLite, PostgreSQL, Apache, Nginx. (Paham letak htdocs, www, apache vhost, dan port standar 3306/80/8080). "
            f"3. Tugas Rekayasa: Debugging error/traceback, merapikan/refactoring kode, memilih arsitektur/design pattern terbaik, membuild/compile proyek, dan menganalisa keamanan/performa. "
            f"Berikan jawaban profesional, kode bersih siap pakai, dan perintah shell yang tepat untuk OS ini."
        )
    }

# ==================== MAIN CLI ====================
def main():
    b_type, b_endpoint, b_model = detect_active_backend()
    if b_type == "none":
        print(f"{C_YELLOW}⚠️ Tidak ada engine AI aktif.{C_RESET}")
        sys.exit(1)

    system_prompt = get_system_prompt()

    # Mode 1: One-shot CLI arguments
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])

        # Periksa slash commands cepat
        if user_prompt.startswith("/tree") or user_prompt.startswith("/ls"):
            print(f"\n{C_CYAN}{C_BOLD}📂 Struktur Proyek Saat Ini:{C_RESET}\n{get_directory_tree()}")
            return
        if user_prompt.startswith("/build"):
            p_type, p_cmd = detect_project_and_build()
            if p_type:
                print(f"{C_GREEN}Deteksi Proyek:{C_RESET} {p_type}")
                execute_command_interactive(p_cmd)
            else:
                print(f"{C_YELLOW}Tidak ditemukan file build otomatis (pom.xml, package.json, Makefile, dll).{C_RESET}")
            return

        file_context, active_file = read_target_file(user_prompt)
        full_user_prompt = user_prompt + file_context
        messages = [system_prompt, {"role": "user", "content": full_user_prompt}]
        print(f"{C_DIM}⏳ Sedang memproses ({PLATFORM_NAME})...{C_RESET}")
        try:
            reply = query_ai(messages, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}")
            
            smart_file_manager(user_prompt, reply, active_file)

            commands = extract_commands(reply)
            for cmd in commands:
                if any(cmd.startswith(pfx) for pfx in ["pkg ", "apt ", "git ", "pip ", "python ", "npm ", "php ", "javac ", "mvn ", "gradle ", "composer ", "mysql ", "curl ", "wget ", "winget ", "dir ", "ls "]):
                    execute_command_interactive(cmd)
        except Exception as e:
            print(f"{C_YELLOW}Error: {e}{C_RESET}")
        return

    # Mode 2: Interactive REPL Chat
    print(f"{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║      🤖 CODEX FULL-STACK ENGINEERING CLI v3.0               ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚══════════════════════════════════════════════════════════════╝{C_RESET}")
    print(f"{C_GREEN}Platform  :{C_RESET} {PLATFORM_NAME} (OS: {OS_TYPE})")
    print(f"{C_BLUE}AI Engine :{C_RESET} {b_type.upper()}")
    print(f"{C_DIM}Perintah khusus: /tree (lihat file), /build (compile otomatis), clear, exit{C_RESET}\n")

    history = [system_prompt]
    while True:
        try:
            prompt = input(f"{C_GREEN}{C_BOLD}Codex [{OS_TYPE}] > {C_RESET}").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit", "q"]:
                print(f"{C_DIM}Sampai jumpa!{C_RESET}")
                break
            if prompt.lower() == "clear":
                history = [system_prompt]
                print(f"{C_DIM}Riwayat percakapan dibersihkan.{C_RESET}")
                continue
            if prompt.lower() in ["/tree", "/ls"]:
                print(f"\n{C_CYAN}{C_BOLD}📂 Struktur Proyek:{C_RESET}\n{get_directory_tree()}\n")
                continue
            if prompt.lower() == "/build":
                p_type, p_cmd = detect_project_and_build()
                if p_type:
                    print(f"{C_GREEN}Deteksi Proyek:{C_RESET} {p_type}")
                    execute_command_interactive(p_cmd)
                else:
                    print(f"{C_YELLOW}Tidak ditemukan file build otomatis.{C_RESET}")
                continue

            file_context, active_file = read_target_file(prompt)
            full_prompt = prompt + file_context
            history.append({"role": "user", "content": full_prompt})

            print(f"{C_DIM}⏳ Berpikir & Menganalisa...{C_RESET}")
            reply = query_ai(history, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}\n")
            history.append({"role": "assistant", "content": reply})

            smart_file_manager(prompt, reply, active_file)

            commands = extract_commands(reply)
            for cmd in commands:
                if any(cmd.startswith(pfx) for pfx in ["pkg ", "apt ", "git ", "pip ", "python ", "npm ", "php ", "javac ", "mvn ", "gradle ", "composer ", "mysql ", "curl ", "wget ", "winget ", "dir ", "ls "]):
                    execute_command_interactive(cmd)

            if len(history) > 11:
                history = [history[0]] + history[-10:]

        except KeyboardInterrupt:
            print(f"\n{C_DIM}Sesi dihentikan.{C_RESET}")
            break
        except Exception as e:
            print(f"{C_YELLOW}Error: {e}{C_RESET}")

if __name__ == "__main__":
    main()
