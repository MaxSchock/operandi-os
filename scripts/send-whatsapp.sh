#!/usr/bin/env bash
# WhatsApp desde el numero personal de Max (instancia Evolution "Max Privat" en VpsFigura).
#
# Uso:
#   send-whatsapp.sh resolve "<nombre parcial de grupo/chat>"   -> lista JIDs que matchean
#   send-whatsapp.sh peek <jid>                                 -> ultimos 8 mensajes del hilo
#   send-whatsapp.sh send-file <jid> <archivo local> [caption]  -> envia documento
#   send-whatsapp.sh send-text <jid> "<texto>"                  -> envia texto
#
# REGLA IRROMPIBLE: hacer SIEMPRE `peek` y juzgar el hilo antes de cualquier send.
# Via tecnica (descubierta 2026-07-15, no re-derivar):
#   - MCP evolution NO sirve para archivos (base64 por el contexto = inviable) y los
#     nombres de grupo llegan vacios -> resolver por BD evolution en el VPS.
#   - API publica: https://ssevolutionapi.figura-studio.com, apikey = env
#     AUTHENTICATION_API_KEY del contenedor (se lee on-the-fly, nunca se persiste local).
#   - El contenedor evolution no tiene python3; la IP overlay 10.0.x.x no se alcanza
#     desde el host -> todo va contra la URL publica, con base64 generado en el VPS.

set -euo pipefail

VPS="root@207.180.226.148"
INSTANCE="Max%20Privat"
API="https://ssevolutionapi.figura-studio.com"
CMD="${1:?comando: resolve|peek|send-file|send-text}"

pg() { ssh "$VPS" "docker exec \$(docker ps -q -f name=postgres_postgres) psql -U postgres -d evolution -Atc \"$1\""; }

case "$CMD" in
  resolve)
    NAME="${2:?nombre a buscar}"
    pg "SELECT \\\"remoteJid\\\"||' | '||COALESCE(name,'') FROM \\\"Chat\\\" WHERE name ILIKE '%${NAME}%' ORDER BY \\\"updatedAt\\\" DESC LIMIT 10;"
    ;;
  peek)
    JID="${2:?jid}"
    pg "SELECT to_timestamp(\\\"messageTimestamp\\\")::timestamp||' | '||CASE WHEN (key->>'fromMe')::bool THEN 'YO' ELSE COALESCE(\\\"pushName\\\",'?') END||' | '||left(COALESCE(message->>'conversation', message->'extendedTextMessage'->>'text', message->'documentMessage'->>'fileName', \\\"messageType\\\"),120) FROM \\\"Message\\\" WHERE key->>'remoteJid'='${JID}' ORDER BY \\\"messageTimestamp\\\" DESC LIMIT 8;"
    ;;
  send-file)
    JID="${2:?jid}"; FILE="${3:?archivo}"; CAPTION="${4:-}"
    BASENAME=$(basename "$FILE")
    MIME=$(file -b --mime-type "$FILE")
    scp -q "$FILE" "$VPS:/tmp/wa-send-$BASENAME"
    ssh "$VPS" "TOKEN=\$(docker exec \$(docker ps -q -f name=evolution_evolution) printenv AUTHENTICATION_API_KEY); \
      python3 - <<'PYEOF'
import base64, json, urllib.request, os
media = base64.b64encode(open('/tmp/wa-send-$BASENAME','rb').read()).decode()
payload = {'number': '$JID', 'mediatype': 'document', 'mimetype': '$MIME',
           'fileName': '$BASENAME', 'media': media}
cap = '''$CAPTION'''
if cap: payload['caption'] = cap
req = urllib.request.Request('$API/message/sendMedia/$INSTANCE',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json', 'apikey': os.popen(
        'docker exec \$(docker ps -q -f name=evolution_evolution) printenv AUTHENTICATION_API_KEY').read().strip()})
r = json.load(urllib.request.urlopen(req))
print(json.dumps({'id': r.get('key',{}).get('id'), 'status': r.get('status')}))
os.remove('/tmp/wa-send-$BASENAME')
PYEOF"
    ;;
  send-text)
    JID="${2:?jid}"; TEXT="${3:?texto}"
    ssh "$VPS" "python3 - <<'PYEOF'
import json, urllib.request, os
req = urllib.request.Request('$API/message/sendText/$INSTANCE',
    data=json.dumps({'number': '$JID', 'text': '''$TEXT'''}).encode(),
    headers={'Content-Type': 'application/json', 'apikey': os.popen(
        'docker exec \$(docker ps -q -f name=evolution_evolution) printenv AUTHENTICATION_API_KEY').read().strip()})
r = json.load(urllib.request.urlopen(req))
print(json.dumps({'id': r.get('key',{}).get('id'), 'status': r.get('status')}))
PYEOF"
    ;;
  *)
    echo "comando desconocido: $CMD" >&2; exit 1
    ;;
esac
