#!/bin/bash
# Hook Stop: convertir la sesión Claude Code más reciente a markdown en el vault.
# Llamado desde ~/.claude/settings.json hooks Stop array.
# Idempotente: si el JSONL ya está convertido, se sobrescribe con la versión final.
# Async-safe: errores van a stderr sin bloquear el cierre de sesión.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="$HOME/.claude/projects"
VAULT_OUTPUT="$HOME/iamasters-os/_wiki/raw/chat-history"

mkdir -p "$VAULT_OUTPUT"

# Most recent JSONL across all projects (modified within last 10 minutes).
latest=$(find "$PROJECTS_DIR" -type f -name '*.jsonl' -mmin -10 -printf '%T@ %p\n' 2>/dev/null \
    | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "$latest" ]; then
    echo "[chat-hook-on-stop] No recent JSONL session found within 10min." >&2
    exit 0
fi

python3 "$SCRIPT_DIR/chat-to-md.py" "$latest" "$VAULT_OUTPUT" >/dev/null 2>&1 || {
    echo "[chat-hook-on-stop] Conversion failed for $latest" >&2
    exit 0
}

exit 0
