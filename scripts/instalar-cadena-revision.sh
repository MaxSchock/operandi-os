#!/usr/bin/env bash
# Copy the review chain (skills adapted from mattpocock/skills, first installed in
# Linus on 2026-10-08) into another product repo as editable files.
# Usage: bash scripts/instalar-cadena-revision.sh <repo-destino> [repo-origen]
# Never overwrites a skill that already exists in the destination.
set -euo pipefail
DEST="${1:?uso: instalar-cadena-revision.sh <repo-destino> [repo-origen]}"
SRC="${2:-$HOME/max-assistent-pocock}"
[ -d "$SRC/.claude/skills/improve-codebase-architecture" ] || { echo "origen sin la cadena: $SRC"; exit 1; }
[ -d "$DEST/.git" ] || [ -f "$DEST/.git" ] || { echo "destino no es un repo git: $DEST"; exit 1; }
mkdir -p "$DEST/.claude/skills"
for n in improve-codebase-architecture codebase-design diagnosing-bugs domain-modeling prototype retro tdd writing-for-agents revision-dos-ejes grilling trozos-con-test-primero verification-before-completion; do
  if [ -e "$DEST/.claude/skills/$n" ]; then
    echo "ya existe, no se toca: $n"
  else
    cp -r "$SRC/.claude/skills/$n" "$DEST/.claude/skills/$n" && echo "copiada: $n"
  fi
done
for f in ORIGEN-mattpocock.md LICENSE-mattpocock-skills.txt; do
  [ -e "$DEST/.claude/skills/$f" ] || cp "$SRC/.claude/skills/$f" "$DEST/.claude/skills/$f"
done
echo "Revisar en el destino las notas locales de revision-dos-ejes, grilling y trozos-con-test-primero: nombran ficheros de Linus."
