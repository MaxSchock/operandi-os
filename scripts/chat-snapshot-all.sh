#!/bin/bash
# Snapshot inicial: convertir TODAS las sesiones JSONL de Claude Code a markdown en el vault.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="$HOME/.claude/projects"
VAULT_OUTPUT="$HOME/iamasters-os/_wiki/raw/chat-history"

mkdir -p "$VAULT_OUTPUT"

count=0
skipped=0
errored=0

echo "Scanning $PROJECTS_DIR for .jsonl sessions..."
while IFS= read -r -d '' jsonl; do
    if python3 "$SCRIPT_DIR/chat-to-md.py" "$jsonl" "$VAULT_OUTPUT" >/dev/null 2>&1; then
        count=$((count + 1))
    else
        rc=$?
        if [ $rc -eq 0 ]; then
            skipped=$((skipped + 1))
        else
            errored=$((errored + 1))
            echo "ERROR on: $jsonl" >&2
        fi
    fi
done < <(find "$PROJECTS_DIR" -type f -name '*.jsonl' -print0)

echo ""
echo "Done. Converted: $count · Skipped: $skipped · Errored: $errored"
echo "Output: $VAULT_OUTPUT"
ls -1 "$VAULT_OUTPUT" | wc -l | xargs -I {} echo "Files in vault: {}"
