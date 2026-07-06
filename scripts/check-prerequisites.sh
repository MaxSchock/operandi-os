#!/bin/bash
# Project Hivemind — preflight check. Run BEFORE bash scripts/install.sh.
# Human-readable: tells a non-technical user exactly what to fix.
# Exit 0 = ready; exit 1 = something blocking is missing.

set -u

green=$'\033[32m'; red=$'\033[31m'; yellow=$'\033[33m'; bold=$'\033[1m'; reset=$'\033[0m'
ok()   { echo "  ${green}✓${reset} $*"; }
bad()  { echo "  ${red}✗${reset} $*"; }
note() { echo "  ${yellow}!${reset} $*"; }

blocking=0

echo ""
echo "${bold}Project Hivemind — comprobación de requisitos${reset}"
echo "──────────────────────────────────────────────"

# --- OS / terminal ---------------------------------------------------------
uname_s="$(uname -s 2>/dev/null || echo unknown)"
case "$uname_s" in
    Linux)  if grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then ok "Terminal: WSL (Linux sobre Windows) — correcto"; else ok "Terminal: Linux"; fi ;;
    Darwin) ok "Terminal: macOS" ;;
    MINGW*|MSYS*|CYGWIN*) note "Estás en Git-Bash de Windows. Recomendado: usar WSL. Si no tienes WSL, instálalo con 'wsl --install' en PowerShell." ;;
    *) note "Sistema no reconocido ($uname_s). Continúa, pero avisa si algo falla." ;;
esac

# --- git -------------------------------------------------------------------
if command -v git >/dev/null 2>&1; then
    ok "git instalado ($(git --version | awk '{print $3}'))"
else
    bad "git NO está instalado. Instálalo: Linux/WSL 'sudo apt install git'; macOS 'xcode-select --install'."
    blocking=1
fi

# --- Node >= 18 ------------------------------------------------------------
if command -v node >/dev/null 2>&1; then
    nv="$(node -v 2>/dev/null | sed 's/^v//')"; nmaj="${nv%%.*}"
    if [ "${nmaj:-0}" -ge 18 ] 2>/dev/null; then
        ok "Node.js $nv (>= 18)"
    else
        bad "Node.js $nv es demasiado viejo (hace falta >= 18). Actualiza desde https://nodejs.org o con nvm."
        blocking=1
    fi
else
    bad "Node.js NO está instalado. Descárgalo de https://nodejs.org (versión LTS)."
    blocking=1
fi

# --- python3 ---------------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
    ok "python3 instalado ($(python3 --version 2>&1 | awk '{print $2}'))"
    if python3 -m pip --version >/dev/null 2>&1; then
        ok "pip disponible"
    else
        bad "pip NO está disponible (lo usa el instalador para las librerías del equipo). Linux/WSL: 'sudo apt install python3-pip'."
        blocking=1
    fi
    # Módulos del equipo: el instalador los instala solo; esto solo informa.
    missing="$(python3 -c '
import importlib.util as u
mods = {"mcp":"mcp","psycopg":"psycopg","openai":"openai","anthropic":"anthropic"}
print(" ".join(name for name, mod in mods.items() if u.find_spec(mod) is None))' 2>/dev/null)"
    if [ -n "$missing" ]; then
        note "Librerías Python pendientes ($missing): el instalador las instalará automáticamente."
    else
        ok "Librerías Python del equipo ya instaladas"
    fi
else
    bad "python3 NO está instalado (lo usa el resumen EOD). Linux/WSL: 'sudo apt install python3'."
    blocking=1
fi

# --- ssh + key -------------------------------------------------------------
if command -v ssh >/dev/null 2>&1; then
    ok "ssh disponible"
    if ls "$HOME"/.ssh/*.pub >/dev/null 2>&1; then
        ok "Tienes al menos una clave SSH en ~/.ssh/"
    else
        note "No tienes clave SSH todavía. El instalador de Hivemind te ayudará a crear una para el servidor."
    fi
else
    bad "ssh NO está disponible. Linux/WSL: 'sudo apt install openssh-client'."
    blocking=1
fi

# --- Claude Code -----------------------------------------------------------
if command -v claude >/dev/null 2>&1; then
    ok "Claude Code (CLI) en PATH"
else
    note "No encuentro 'claude' en PATH. Si usas Claude Desktop con terminal integrada, es normal; continúa."
fi

echo "──────────────────────────────────────────────"
if [ "$blocking" -ne 0 ]; then
    echo "${red}${bold}Faltan requisitos.${reset} Arregla lo marcado con ✗ y vuelve a ejecutar este script."
    exit 1
fi
echo "${green}${bold}Todo listo.${reset} Siguiente paso:  ${bold}bash scripts/install.sh${reset}"
exit 0
