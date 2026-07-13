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

# Auto-commit + push del vault: el backup no depende de tener Obsidian abierto.
# obsidian-git sigue activo para cuando la app corre; aquí cubrimos el resto.
VAULT="$HOME/iamasters-os/_wiki"
if [ -d "$VAULT/.git" ]; then
    (
        cd "$VAULT"
        git add -A >/dev/null 2>&1
        if ! git diff --cached --quiet; then
            git commit -m "vault backup: session close $(date +%Y-%m-%d_%H%M)" >/dev/null 2>&1
        fi
        git push origin main >/dev/null 2>&1 \
            || echo "[chat-hook-on-stop] Vault push failed (offline?); queda commiteado en local." >&2
    )
fi

exit 0
