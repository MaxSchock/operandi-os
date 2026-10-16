#!/usr/bin/env bash
# Abre un archivo para Max en Windows (trabaja desde PowerShell y no puede abrir enlaces
# ni ver archivos del chat). Uso: scripts/abrir.sh <archivo> [...]
# Windows trata \\wsl.localhost como origen no fiable y Fotos pide confirmacion cada vez
# (captura 14-10-2026 14:30), asi que primero se copia el archivo a una carpeta de Windows
# y se abre desde alli con la aplicacion por defecto.
set -euo pipefail
[ $# -ge 1 ] || { echo "uso: $0 <archivo> [...]" >&2; exit 2; }
DEST=/mnt/c/Users/PC/Downloads/claude-abiertos
mkdir -p "$DEST"
for f in "$@"; do
  [ -e "$f" ] || { echo "no existe: $f" >&2; continue; }
  cp -f "$f" "$DEST/$(basename "$f")"
  w=$(wslpath -w "$DEST/$(basename "$f")")
  (cd /mnt/c && /mnt/c/Windows/System32/cmd.exe /c start "" "$w" >/dev/null 2>&1) || true
  echo "abierto: $w"
done
