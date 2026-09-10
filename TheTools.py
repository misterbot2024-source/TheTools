#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Tools — Instalador para Termux
------------------------------------
Ferramenta em Python para Termux que exibe um banner elegante ("THE TOOLS")
e instala um conjunto de 50 ferramentas úteis, organizadas por categoria,
via pkg, com barra de progresso e log de instalação.

Uso:
    python termux_installer.py
"""

import os
import sys
import time
import shutil
import subprocess
import textwrap

# ----------------------------------------------------------------------
# CORES (ANSI) - funcionam nativamente no Termux
# ----------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[38;5;196m"
    GREEN = "\033[38;5;46m"
    YELLOW = "\033[38;5;226m"
    BLUE = "\033[38;5;39m"
    CYAN = "\033[38;5;51m"
    MAGENTA = "\033[38;5;201m"
    ORANGE = "\033[38;5;208m"
    GRAY = "\033[38;5;244m"
    WHITE = "\033[38;5;255m"

    # gradiente para o banner
    GRAD = [21, 27, 33, 39, 45, 51, 87, 123, 159, 195]


def grad_text(text, palette=None):
    """Aplica um gradiente de cor caractere a caractere."""
    palette = palette or C.GRAD
    out = []
    n = max(len(text) - 1, 1)
    for i, ch in enumerate(text):
        idx = palette[int(i / n * (len(palette) - 1))]
        out.append(f"\033[38;5;{idx}m{ch}")
    out.append(C.RESET)
    return "".join(out)


def term_width(default=70):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def hr(char="─", color=C.GRAY):
    w = min(term_width(), 70)
    print(f"{color}{char * w}{C.RESET}")


def center(text, width=None):
    width = width or min(term_width(), 70)
    return text.center(width)


# ----------------------------------------------------------------------
# BANNER
# ----------------------------------------------------------------------
LOGO = r"""
▀█▀ █░█ █▀▀   ▀█▀ █▀█ █▀█ █░░ █▀
░█░ █▀█ ██▄   ░█░ █▄█ █▄█ █▄▄ ▄█
"""

def print_banner():
    os.system("clear" if os.name != "nt" else "cls")
    w = min(term_width(), 70)
    print()
    for line in LOGO.strip("\n").split("\n"):
        pad = max((w - len(line)) // 2, 0)
        print(" " * pad + grad_text(line))
    print()
    hr("═", C.CYAN)
    print(center(f"{C.BOLD}{C.WHITE}THE TOOLS — INSTALADOR{C.RESET}", w))
    print(center(f"{C.DIM}{C.GRAY}50 utilitários essenciais para o Termux{C.RESET}", w))
    hr("═", C.CYAN)
    print(center(f"{C.YELLOW}Python {sys.version.split()[0]}{C.RESET}  {C.GRAY}|{C.RESET}  "
                 f"{C.YELLOW}{time.strftime('%d/%m/%Y %H:%M')}{C.RESET}", w))
    hr("─", C.GRAY)
    print()


def print_section_banner(title, icon="◆"):
    w = min(term_width(), 70)
    print()
    print(f"{C.MAGENTA}{icon}{C.RESET} {C.BOLD}{C.WHITE}{title}{C.RESET}")
    print(f"{C.GRAY}{'·' * w}{C.RESET}")


# ----------------------------------------------------------------------
# CATÁLOGO DE FERRAMENTAS (50 no total)
# cada item: (nome do pacote pkg, descrição curta)
# ----------------------------------------------------------------------
CATEGORIES = {
    "Desenvolvimento": [
        ("git", "Controle de versão"),
        ("python", "Linguagem Python"),
        ("nodejs", "Runtime JavaScript"),
        ("golang", "Linguagem Go"),
        ("rust", "Linguagem Rust"),
        ("clang", "Compilador C/C++"),
        ("openjdk-17", "JDK Java 17"),
        ("php", "Linguagem PHP"),
        ("make", "Automação de build"),
    ],
    "Editores & Terminal": [
        ("vim", "Editor de texto"),
        ("neovim", "Editor de texto moderno"),
        ("nano", "Editor simples"),
        ("tmux", "Multiplexador de terminal"),
        ("zsh", "Shell alternativo"),
        ("fish", "Shell amigável"),
        ("micro", "Editor moderno de terminal"),
    ],
    "Rede & Conectividade": [
        ("curl", "Requisições HTTP"),
        ("wget", "Download de arquivos"),
        ("openssh", "Cliente/servidor SSH"),
        ("nmap", "Scanner de rede"),
        ("net-tools", "Utilitários de rede"),
        ("rsync", "Sincronização de arquivos"),
        ("proot", "Ambiente chroot sem root"),
        ("termux-api", "Integração com o Android"),
    ],
    "Utilitários de Sistema": [
        ("htop", "Monitor de processos"),
        ("neofetch", "Info do sistema"),
        ("tree", "Árvore de diretórios"),
        ("zip", "Compactação zip"),
        ("unzip", "Descompactação zip"),
        ("tar", "Compactação tar"),
        ("which", "Localizar binários"),
        ("ncdu", "Análise de uso de disco"),
        ("man", "Páginas de manual"),
        ("termux-tools", "Ferramentas extras Termux"),
    ],
    "Dados & Texto": [
        ("jq", "Processador JSON"),
        ("grep", "Busca em texto"),
        ("sed", "Editor de fluxo"),
        ("gawk", "Processamento de texto"),
        ("ripgrep", "Busca rápida em arquivos"),
        ("fzf", "Busca fuzzy interativa"),
        ("bat", "cat com realce de sintaxe"),
    ],
    "Bancos de Dados": [
        ("sqlite", "Banco de dados leve"),
        ("mariadb", "Servidor MySQL/MariaDB"),
        ("postgresql", "Banco de dados PostgreSQL"),
        ("redis", "Banco chave-valor"),
    ],
    "Multimídia": [
        ("ffmpeg", "Conversão de áudio/vídeo"),
        ("imagemagick", "Manipulação de imagens"),
        ("youtube-dl", "Download de vídeos"),
    ],
    "Segurança": [
        ("gnupg", "Criptografia GPG"),
        ("openssl-tool", "Ferramentas OpenSSL"),
    ],
}


def flat_tools():
    flat = []
    for cat, items in CATEGORIES.items():
        for pkg, desc in items:
            flat.append((cat, pkg, desc))
    return flat


TOTAL_TOOLS = len(flat_tools())


# ----------------------------------------------------------------------
# BARRA DE PROGRESSO
# ----------------------------------------------------------------------
def progress_bar(current, total, label="", width=32):
    frac = current / total if total else 1
    filled = int(width * frac)
    bar = f"{C.GREEN}{'█' * filled}{C.GRAY}{'░' * (width - filled)}{C.RESET}"
    pct = f"{frac * 100:5.1f}%"
    line = f"\r{bar} {C.CYAN}{pct}{C.RESET}  {C.WHITE}{label:<28}{C.RESET}"
    sys.stdout.write(line[: term_width() - 1] if term_width() < len(line) else line)
    sys.stdout.flush()


# ----------------------------------------------------------------------
# INSTALAÇÃO
# ----------------------------------------------------------------------
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")


def run_cmd(cmd, timeout=600):
    try:
        result = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def update_repos():
    print(f"{C.YELLOW}» Atualizando repositórios (pkg update)...{C.RESET}")
    ok, out = run_cmd("pkg update -y && pkg upgrade -y")
    if ok:
        print(f"{C.GREEN}✔ Repositórios atualizados.{C.RESET}\n")
    else:
        print(f"{C.RED}✘ Falha ao atualizar repositórios. Prosseguindo mesmo assim.{C.RESET}\n")
    return ok


def install_tool(pkg):
    ok, out = run_cmd(f"pkg install -y {pkg}")
    return ok, out


def install_all(selected_categories=None, log_path="the_tools_install_log.txt"):
    tools = flat_tools()
    if selected_categories:
        tools = [t for t in tools if t[0] in selected_categories]

    total = len(tools)
    success, failed = [], []

    print_section_banner("Instalação em andamento", "▶")
    print()

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n=== Instalação iniciada em {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

        for i, (cat, pkg, desc) in enumerate(tools, start=1):
            progress_bar(i - 1, total, label=f"{pkg}")
            ok, out = install_tool(pkg)
            progress_bar(i, total, label=f"{pkg}")

            status = f"{C.GREEN}OK{C.RESET}" if ok else f"{C.RED}FALHOU{C.RESET}"
            print(f"  [{status}] {C.CYAN}{pkg:<16}{C.RESET} {C.GRAY}{desc}{C.RESET}")

            log.write(f"{pkg}: {'OK' if ok else 'FALHOU'}\n")
            if ok:
                success.append(pkg)
            else:
                failed.append(pkg)

    print()
    hr("─", C.GRAY)
    print(f"{C.GREEN}✔ Instaladas: {len(success)}{C.RESET}   "
          f"{C.RED}✘ Falharam: {len(failed)}{C.RESET}   "
          f"{C.GRAY}Total: {total}{C.RESET}")
    if failed:
        print(f"{C.YELLOW}Ferramentas com falha:{C.RESET} {', '.join(failed)}")
    print(f"{C.DIM}Log salvo em: {log_path}{C.RESET}\n")


# ----------------------------------------------------------------------
# MENU
# ----------------------------------------------------------------------
def print_catalog():
    idx = 1
    for cat, items in CATEGORIES.items():
        print_section_banner(cat, "◆")
        for pkg, desc in items:
            print(f"  {C.GRAY}{idx:>2}.{C.RESET} {C.CYAN}{pkg:<16}{C.RESET} {C.GRAY}- {desc}{C.RESET}")
            idx += 1
    print()


def main_menu():
    while True:
        print_banner()
        print(f"  {C.WHITE}[1]{C.RESET} Ver catálogo completo ({TOTAL_TOOLS} ferramentas)")
        print(f"  {C.WHITE}[2]{C.RESET} Instalar TODAS as ferramentas")
        print(f"  {C.WHITE}[3]{C.RESET} Instalar por categoria")
        print(f"  {C.WHITE}[4]{C.RESET} Atualizar repositórios (pkg update/upgrade)")
        print(f"  {C.WHITE}[0]{C.RESET} Sair")
        hr("─", C.GRAY)
        choice = input(f"{C.BOLD}Escolha uma opção: {C.RESET}").strip()

        if choice == "1":
            print_banner()
            print_catalog()
            input(f"{C.GRAY}Pressione ENTER para voltar...{C.RESET}")

        elif choice == "2":
            if not is_termux():
                print(f"{C.RED}Aviso: ambiente Termux não detectado (PREFIX ausente).{C.RESET}")
                if input("Continuar mesmo assim? (s/N): ").strip().lower() != "s":
                    continue
            update_repos()
            install_all()
            input(f"{C.GRAY}Pressione ENTER para voltar ao menu...{C.RESET}")

        elif choice == "3":
            print_banner()
            cats = list(CATEGORIES.keys())
            for i, c in enumerate(cats, start=1):
                print(f"  {C.WHITE}[{i}]{C.RESET} {c} {C.GRAY}({len(CATEGORIES[c])} itens){C.RESET}")
            sel = input(f"\n{C.BOLD}Digite os números separados por vírgula: {C.RESET}").strip()
            try:
                picked = [cats[int(x) - 1] for x in sel.split(",") if x.strip()]
            except (ValueError, IndexError):
                print(f"{C.RED}Seleção inválida.{C.RESET}")
                time.sleep(1.5)
                continue
            update_repos()
            install_all(selected_categories=picked)
            input(f"{C.GRAY}Pressione ENTER para voltar ao menu...{C.RESET}")

        elif choice == "4":
            update_repos()
            input(f"{C.GRAY}Pressione ENTER para voltar ao menu...{C.RESET}")

        elif choice == "0":
            print_banner()
            print(center(f"{C.CYAN}The Tools — até logo! 👋{C.RESET}"))
            print()
            break

        else:
            print(f"{C.RED}Opção inválida.{C.RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Interrompido pelo usuário.{C.RESET}")
        sys.exit(0)
