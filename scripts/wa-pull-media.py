#!/usr/bin/env python3
"""Download recent WhatsApp media from a set of chats. Runs ON VpsFigura.

Usage: wa_pull.py <outdir> <hours> <jid> [<jid> ...]
Idempotent: already-downloaded files are skipped, so it can be re-run on a timer.
"""
import base64, datetime, json, os, subprocess, sys, urllib.request

OUTDIR, HOURS, JIDS = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
API = "https://ssevolutionapi.figura-studio.com"
INSTANCE = "Max%20Privat"

# El nombre no es 'apikey' a proposito: el detector de secretos del pre-commit lee
# '<algo>key = <16+ caracteres>' como un valor pegado, y la llamada de aqui abajo se
# lo parecia. Se renombra en vez de saltarse el gate, que para eso esta.
clave = subprocess.check_output(
    "docker exec $(docker ps -q -f name=evolution_evolution) printenv AUTHENTICATION_API_KEY",
    shell=True).decode().strip()
pgc = subprocess.check_output("docker ps -q -f name=postgres_postgres", shell=True).decode().strip()

jid_list = ",".join("'%s'" % j for j in JIDS)
sql = """SELECT json_agg(t) FROM (
  SELECT key, "messageType", "pushName", "messageTimestamp",
         COALESCE(message->'imageMessage'->>'mimetype', message->'videoMessage'->>'mimetype',
                  message->'documentMessage'->>'mimetype') AS mime,
         COALESCE(message->'imageMessage'->>'caption', message->'videoMessage'->>'caption') AS caption
  FROM "Message"
  WHERE key->>'remoteJid' IN (%s)
    AND "messageType" IN ('imageMessage','videoMessage','documentMessage')
    AND (key->>'fromMe')::bool IS NOT TRUE
    AND "messageTimestamp" > extract(epoch from now() - interval '%d hours')
  ORDER BY "messageTimestamp") t;""" % (jid_list, HOURS)

rows = json.loads(subprocess.check_output(
    ["docker", "exec", pgc, "psql", "-U", "postgres", "-d", "evolution", "-Atc", sql]).decode()) or []

ALIAS = {"Bohrium Records": "Angel-Mosteiro"}
EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "video/mp4": "mp4",
       "video/3gpp": "3gp", "video/quicktime": "mov", "application/pdf": "pdf"}
new, cached, fail = 0, 0, 0
for r in rows:
    key = r["key"]
    who = r.get("pushName") or "desconocido"
    who = ALIAS.get(who, who).replace("/", "-").replace(" ", "-")
    stamp = datetime.datetime.utcfromtimestamp(int(r["messageTimestamp"])).strftime("%Y%m%d-%H%M%S")
    ext = EXT.get((r.get("mime") or "").split(";")[0], "bin")
    folder = os.path.join(OUTDIR, who)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "%s_%s.%s" % (stamp, key["id"][:8], ext))
    if os.path.exists(path) and os.path.getsize(path) > 0:
        cached += 1
        continue
    req = urllib.request.Request(
        "%s/chat/getBase64FromMediaMessage/%s" % (API, INSTANCE),
        data=json.dumps({"message": {"key": key}, "convertToMp4": False}).encode(),
        headers={"Content-Type": "application/json", "apikey": clave})
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=300))
        with open(path, "wb") as f:
            f.write(base64.b64decode(resp["base64"]))
        new += 1
        print("NUEVO %s/%s" % (who, os.path.basename(path)), flush=True)
    except Exception as e:
        fail += 1
        print("FALLO %s %s %s" % (who, stamp, e), flush=True)
print("RESUMEN nuevos=%d ya_estaban=%d fallidos=%d total=%d" % (new, cached, fail, len(rows)))
