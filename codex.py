#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Universal CLI - Asisten AI Coding & Terminal Lintas Platform
Mendukung: Android Termux, Linux, Windows (PowerShell & CMD), macOS
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

# Deteksi Lingkungan Sistem
OS_TYPE = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
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

# Warna Terminal (ANSI)
if IS_WINDOWS and os.name == 'nt':
    os.system('')  # Aktifkan dukungan ANSI escape di Windows 10/11 CMD

C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_DIM = "\033[90m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

# Konfigurasi Backend
# 1. Local Engine (llama-server di Termux / PC, atau Ollama)
LOCAL_API_URL = os.environ.get("CODEX_LOCAL_URL", "http://127.0.0.1:8080/v1/chat/completions")
OLLAMA_API_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
# 2. Cloud Engine (GitHub Models atau OpenAI Compatible)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))

def detect_active_backend():
    # Cek local llama-server / llama.cpp
    try:
        req = urllib.request.Request("http://127.0.0.1:8080/health", headers={"User-Agent": "CodexCLI"})
        with urllib.request.urlopen(req, timeout=0.8) as r:
            if r.status == 200:
                return "local_llama", LOCAL_API_URL, None
    except Exception:
        pass

    # Cek local Ollama (umum di laptop/PC)
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "CodexCLI"})
        with urllib.request.urlopen(req, timeout=0.8) as r:
            if r.status == 200:
                return "local_ollama", OLLAMA_API_URL, "qwen2.5-coder:latest"
    except Exception:
        pass

    # Cek apakah di Termux dan ada ~/model.gguf
    if IS_TERMUX:
        model_path = pathlib.Path.home() / "model.gguf"
        if model_path.exists():
            import time
            subprocess.Popen(
                ["llama-server", "-m", str(model_path), "--port", "8080", "--host", "127.0.0.1", "-c", "1024", "-t", "4", "--poll", "0"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            for _ in range(10):
                time.sleep(0.5)
                try:
                    req = urllib.request.Request("http://127.0.0.1:8080/health", headers={"User-Agent": "CodexCLI"})
                    with urllib.request.urlopen(req, timeout=0.8) as r:
                        if r.status == 200:
                            return "local_llama", LOCAL_API_URL, None
                except Exception:
                    pass
            return "local_llama", LOCAL_API_URL, None

    # Fallback ke Cloud (jika ada token)
    if GITHUB_TOKEN:
        return "cloud_github", "https://models.github.ai/inference/chat/completions", "gpt-4o-mini"

    return "none", None, None

def query_ai(messages, backend_type, endpoint, model_name=None):
    payload = {
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.5,
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
    with urllib.request.urlopen(req, timeout=40) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"].strip()

def extract_commands(text):
    """Mengekstrak blok perintah shell dari respon AI"""
    patterns = [
        r"```(?:bash|sh|cmd|powershell|bat)\n(.*?)```",
        r"```\n(.*?)```"
    ]
    cmds = []
    for pat in patterns:
        matches = re.findall(pat, text, re.DOTALL)
        for m in matches:
            lines = [l.strip() for l in m.strip().split("\n") if l.strip() and not l.strip().startswith("#")]
            if lines:
                cmds.extend(lines)
    return cmds

def execute_command_interactive(cmd_str):
    """Menanyakan konfirmasi pengguna sebelum mengeksekusi perintah shell"""
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

def check_and_create_file(prompt: str, reply: str):
    """Mendeteksi apakah pengguna ingin menyimpan kode ke file"""
    low = prompt.lower()
    if any(k in low for k in ["buat file", "bikin file", "tulis file", "simpan ke", "create file", "save to"]):
        m = re.search(r'([A-Za-z0-9_\-./\\]+\.(?:py|html|js|sh|bat|ps1|txt|json|md|c|cpp|go|rs|css))', prompt)
        if m:
            fname = m.group(1)
            target_path = pathlib.Path(fname)
            code_match = re.search(r'```(?:\w+)?\n(.*?)```', reply, re.DOTALL)
            content = code_match.group(1) if code_match else reply
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content.strip() + "\n", encoding="utf-8")
            print(f"\n{C_GREEN}💾 File berhasil dibuat:{C_RESET} {target_path.resolve()}")

def read_target_file(prompt: str):
    """Otomatis membaca isi file jika disebutkan di pertanyaan (misal: periksa app.py)"""
    m = re.search(r'(?:periksa|cek|baca|review|edit|ubah|lihat|read|check)\s+([A-Za-z0-9_\-./\\]+\.[a-zA-Z0-9]+)', prompt, re.IGNORECASE)
    if m:
        fname = m.group(1)
        p = pathlib.Path(fname)
        if p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                print(f"{C_DIM}📖 Otomatis membaca konteks file: {p.name} ({len(content)} karakter){C_RESET}")
                return f"\n\n[Isi file {p.name} saat ini]:\n```\n{content}\n```\n"
            except Exception:
                pass
    return ""

def main():
    b_type, b_endpoint, b_model = detect_active_backend()
    if b_type == "none":
        print(f"{C_YELLOW}⚠️ Tidak ada engine AI aktif.{C_RESET}")
        print(f"• Di HP: Pastikan model.gguf ada di ~/model.gguf")
        print(f"• Di Laptop: Jalankan Ollama ('ollama run qwen2.5-coder') atau set GITHUB_TOKEN")
        sys.exit(1)

    system_prompt = {
        "role": "system",
        "content": (
            f"Kamu adalah Codex CLI, asisten AI pemrograman dan terminal cerdas serbaguna. "
            f"Lingkungan saat ini: {PLATFORM_NAME}. "
            f"Package manager: {DEFAULT_PKG_MGR}. "
            f"Gunakan sintaks perintah yang SESUAI untuk OS saat ini ({OS_TYPE}). "
            f"Beri jawaban ringkas, jelas, langsung ke solusi, dan berikan blok kode/perintah yang siap dijalankan."
        )
    }

    # Mode 1: One-shot CLI arguments (e.g. codex "buat fungsi kalkulator")
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        file_context = read_target_file(user_prompt)
        full_user_prompt = user_prompt + file_context
        messages = [system_prompt, {"role": "user", "content": full_user_prompt}]
        print(f"{C_DIM}⏳ Sedang memproses ({PLATFORM_NAME})...{C_RESET}")
        try:
            reply = query_ai(messages, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}")
            check_and_create_file(user_prompt, reply)
            
            # Cek apakah ada perintah shell yang bisa dieksekusi
            commands = extract_commands(reply)
            for cmd in commands:
                if any(cmd.startswith(pfx) for pfx in ["pkg ", "apt ", "git ", "pip ", "python ", "npm ", "mkdir ", "cd ", "curl ", "wget ", "winget ", "dir ", "ls "]):
                    execute_command_interactive(cmd)
        except Exception as e:
            print(f"{C_YELLOW}Error: {e}{C_RESET}")
        return

    # Mode 2: Interactive REPL Chat
    print(f"{C_CYAN}{C_BOLD}╔═══════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║          🤖 CODEX UNIVERSAL CLI v2.0                  ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚═══════════════════════════════════════════════════════╝{C_RESET}")
    print(f"{C_GREEN}Platform Aktif :{C_RESET} {PLATFORM_NAME}")
    print(f"{C_BLUE}Backend Engine :{C_RESET} {b_type.upper()} ({b_endpoint})")
    print(f"{C_DIM}Ketik pertanyaan Anda, 'clear' untuk reset percakapan, atau 'exit'/'q' untuk keluar.{C_RESET}\n")

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

            file_context = read_target_file(prompt)
            full_prompt = prompt + file_context
            history.append({"role": "user", "content": full_prompt})
            
            print(f"{C_DIM}⏳ Berpikir...{C_RESET}")
            reply = query_ai(history, b_type, b_endpoint, b_model)
            print(f"\n{C_CYAN}{C_BOLD}🤖 Codex:{C_RESET}\n{reply}\n")
            history.append({"role": "assistant", "content": reply})
            
            check_and_create_file(prompt, reply)
            
            commands = extract_commands(reply)
            for cmd in commands:
                if any(cmd.startswith(pfx) for pfx in ["pkg ", "apt ", "git ", "pip ", "python ", "npm ", "mkdir ", "cd ", "curl ", "wget ", "winget ", "dir ", "ls "]):
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
