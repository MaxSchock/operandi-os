#!/usr/bin/env bash
# Trae a Downloads los medios que el cron del VPS (*/10, /root/wa-ibiza-pull.sh) va salvando
# de los chats de la pandilla de Ibiza antes de que WhatsApp los caduque (~14 dias).
# El rescate en el VPS es lo importante; esto solo sincroniza a local.
set -euo pipefail
DEST="${1:-/mnt/c/Users/PC/Downloads/ibiza-despedida}"
mkdir -p "$DEST"
rsync -a --out-format='%n' --exclude 'pull.log' -e "ssh -o ConnectTimeout=15" \
  root@207.180.226.148:/root/wa-ibiza/ "$DEST/" | grep -v '/$' || true
