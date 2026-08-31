"""Runs on ki-prod-01. Analyses a video with Gemini and prints notes to stdout.

Two modes:
  youtube <url>   -> hands Gemini the YouTube URL directly (no download)
  file <path>     -> uploads a local file via the File API, then deletes it

The API key is read from /root/secrets/gemini-api-key.txt and never printed.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

KEY_PATH = "/root/secrets/gemini-api-key.txt"
G = "https://generativelanguage.googleapis.com"
MODEL = "gemini-2.5-pro"

PROMPT = """Analiza este video (clase de una comunidad, reel o post de un creador).
Cubre lo que se VE en pantalla, no solo lo que se dice: interfaces, herramientas
concretas, pasos de configuración, código y diagramas.

Devuelve en español:
1. RESUMEN (5-8 lineas): que enseña y para quien.
2. HERRAMIENTAS Y SERVICIOS que aparecen, con el uso exacto que se les da.
3. PASOS TÉCNICOS reproducibles (lo que habría que hacer para replicarlo).
4. LO NO OBVIO: trucos, límites, errores que el autor menciona haber cometido.
5. APLICABILIDAD: para quien construye automatizaciones n8n, pipelines RAG,
   agentes de voz y outreach multilingüe para pymes, ¿qué de esto es aprovechable
   y qué es relleno? Sé duro: si el video no aporta nada nuevo, dilo.
Si el video no trata de tecnología ni de negocio, responde solo con una línea
diciendo de qué va y para. No rellenes las cinco secciones a la fuerza.
Sin paja, sin introducciones, sin recordatorios."""


def key():
    with open(KEY_PATH) as f:
        return f.read().strip()


def post(url, payload, k):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": k},
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())


def generate(part, k):
    payload = {"contents": [{"parts": [part, {"text": PROMPT}]}]}
    out = post(f"{G}/v1beta/models/{MODEL}:generateContent", payload, k)
    cands = out.get("candidates") or []
    if not cands:
        return "[sin respuesta] " + json.dumps(out)[:400]
    return "".join(p.get("text", "") for p in cands[0]["content"]["parts"])


def upload(path, k):
    size = os.path.getsize(path)
    mime = "video/mp4"
    req = urllib.request.Request(
        f"{G}/upload/v1beta/files?uploadType=media",
        data=open(path, "rb").read(),
        headers={"x-goog-api-key": k, "Content-Type": mime,
                 "X-Goog-Upload-Protocol": "raw", "Content-Length": str(size)},
    )
    with urllib.request.urlopen(req, timeout=1800) as r:
        info = json.loads(r.read())["file"]
    name, uri = info["name"], info["uri"]
    for _ in range(120):
        chk = urllib.request.Request(f"{G}/v1beta/{name}", headers={"x-goog-api-key": k})
        with urllib.request.urlopen(chk, timeout=60) as r:
            st = json.loads(r.read())
        if st.get("state") == "ACTIVE":
            return name, uri, st.get("mimeType", mime)
        if st.get("state") == "FAILED":
            raise SystemExit("Gemini rechazo el fichero")
        time.sleep(5)
    raise SystemExit("timeout esperando ACTIVE")


def delete(name, k):
    req = urllib.request.Request(f"{G}/v1beta/{name}", method="DELETE",
                                 headers={"x-goog-api-key": k})
    try:
        urllib.request.urlopen(req, timeout=60)
    except Exception:
        pass


def main():
    mode, target = sys.argv[1], sys.argv[2]
    k = key()
    if mode == "youtube":
        print(generate({"file_data": {"file_uri": target}}, k))
        return
    name, uri, mime = upload(target, k)
    try:
        print(generate({"file_data": {"file_uri": uri, "mime_type": mime}}, k))
    finally:
        delete(name, k)
        os.remove(target)


try:
    main()
except urllib.error.HTTPError as e:
    body = e.read().decode()[:500]
    print(f"[HTTP {e.code}] {body}", file=sys.stderr)
    sys.exit(2)
