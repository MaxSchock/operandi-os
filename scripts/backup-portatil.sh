#!/bin/bash
# Copia de seguridad cifrada del portatil al Object Storage de Contabo (restic por S3). Cron 23:30.
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
CFG="$HOME/.config/restic"; LOG="$CFG/ultimo.log"; HIST="$CFG/historial.log"
DRY=""; [ "${1:-}" = "--dry-run" ] && DRY="--dry-run"
OUT=$(mktemp); ERR=1; ANADIDO=""; FIN=0

# Deja rastro aunque el script muera a medias: INICIO al empezar, resultado al salir.
[ -z "$DRY" ] && echo "$(date '+%Y-%m-%d %H:%M:%S') | INICIO | en curso" > "$LOG"
cierre() {
  rm -f "$OUT"
  [ -n "$DRY" ] && return
  if [ $FIN -eq 1 ]; then
    if [ $ERR -eq 0 ]; then RES="OK"; else RES="ERROR (ver $CFG/ultimo-detalle.log)"; fi
  else
    RES="ERROR (el script se interrumpio antes de terminar)"
  fi
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $RES | añadido: ${ANADIDO:-n/d}" > "$LOG"
  cat "$LOG" >> "$HIST"
}
trap cierre EXIT

set -a; . "$CFG/contabo-s3.env"; set +a
export RESTIC_REPOSITORY="s3:https://eu2.contabostorage.com/thinkpad-restic"
export RESTIC_PASSWORD_FILE="$CFG/thinkpad.pass"
RUTAS=("$HOME/iamasters-os" "$HOME/.claude" "$HOME/.config" "$HOME/src" "$HOME/.ssh" "$HOME/backups" "$HOME/backups-linus" "$CFG/crontab.txt")
crontab -l > "$CFG/crontab.txt" 2>/dev/null

ERR=0
restic backup $DRY --tag thinkpad --exclude-file "$CFG/excludes.txt" --exclude-caches --one-file-system "${RUTAS[@]}" >"$OUT" 2>&1 || ERR=1
if [ -z "$DRY" ]; then
  if [ $ERR -eq 0 ]; then
    restic forget --prune --tag thinkpad --keep-daily 7 --keep-weekly 4 --keep-monthly 6 >>"$OUT" 2>&1 || ERR=1
  fi
  ANADIDO=$(grep -m1 -E "^Added to the repository" "$OUT" | sed 's/Added to the repository: //')
  cp "$OUT" "$CFG/ultimo-detalle.log"
else
  cat "$OUT"
fi
FIN=1; exit $ERR
