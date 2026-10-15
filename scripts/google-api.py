#!/usr/bin/env python3
"""Google por OAuth directo (Drive, Sheets, Gmail de solo lectura) sin reescribir el refresco cada vez.

Cada sesion volvia a escribir las mismas lineas (leer client_id/secret/refresh_token de
~/.config/gcp, POST a oauth2.googleapis.com/token, Bearer a la API): 55 sesiones. Y el helper
oficial ~/.config/gcp/refresh-token.py abre un login interactivo y cuelga a Claude, asi que
aqui se refresca directo, como dice la regla reference-google-sheets-drive-mecanismos.

Cuentas (REGLA DURA del CLAUDE.md global):
  operandi  -> ~/.config/gcp/token-operandi.json        (maximilian.schock@operandiconsultancy.com)
  kisult    -> ~/.config/gcp/accounts/kisult.json        (max@kisult.com)
  jonas     -> ~/.config/gcp/accounts/jonas.json
  linus-audit-max-kisult -> ~/.config/gcp/accounts/linus-audit-max-kisult.json
  personal  -> RECHAZADA: el personal va por Unipile (correo) o el MCP de claude.ai (Drive).

Uso (siempre con -I). El token de acceso NUNCA se imprime; los comandos lo usan por dentro.
  google-api.py cuentas                              lista cuentas y si el refresco funciona
  google-api.py token <cuenta>                       comprueba el refresco (caduca en N s, scopes)
  google-api.py drive-ls <cuenta> [--carpeta ID] [--q "texto"] [--max 50]
  google-api.py drive-get <cuenta> <fileId> <destino> [--exportar application/pdf]
  google-api.py drive-put <cuenta> <fichero> [--carpeta ID] [--actualiza fileId] [--nombre N] [--dry]
        (--actualiza cambia el contenido del MISMO fichero sin cambiar el enlace; sin --dry escribe en Drive)
  google-api.py sheets-get <cuenta> <spreadsheetId> <rango A1>     devuelve JSON de celdas
  google-api.py gmail-list <cuenta> --q "from:x newer_than:7d" [--max 10]   id, fecha, remitente, asunto
Como libreria (otro script):  importlib sobre este fichero y  token_de("kisult")  devuelve el access_token.
Si sale invalid_grant, el refresh_token esta revocado: lo renueva Max con refresh-token.py (interactivo).
"""
import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GCP = os.path.expanduser("~/.config/gcp")
CUENTAS = {
    "operandi": GCP + "/token-operandi.json",
    "kisult": GCP + "/accounts/kisult.json",
    "jonas": GCP + "/accounts/jonas.json",
    "linus-audit-max-kisult": GCP + "/accounts/linus-audit-max-kisult.json",
}
_cache = {}


class Fallo(Exception):
    pass


def _credencial(cuenta):
    if cuenta == "personal":
        raise Fallo("la cuenta personal no se toca por OAuth directo: correo por Unipile, Drive por el MCP de claude.ai")
    if cuenta not in CUENTAS:
        raise Fallo("cuenta desconocida %r. Validas: %s" % (cuenta, ", ".join(CUENTAS)))
    return json.load(open(CUENTAS[cuenta]))


def token_de(cuenta):
    """Devuelve (access_token, segundos de vida, scopes). Cachea en el proceso."""
    if cuenta in _cache and _cache[cuenta][1] > time.time() + 60:
        return _cache[cuenta][0]
    c = _credencial(cuenta)
    cuerpo = urllib.parse.urlencode({
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
    try:
        r = json.load(urllib.request.urlopen(c.get("token_uri") or "https://oauth2.googleapis.com/token", cuerpo, timeout=30))
    except urllib.error.HTTPError as e:
        try:
            motivo = json.loads(e.read()).get("error", "?")
        except Exception:
            motivo = "?"
        raise Fallo("refresco de %s rechazado: HTTP %s %s%s" % (
            cuenta, e.code, motivo, " (token revocado: lo renueva Max con refresh-token.py)" if motivo == "invalid_grant" else ""))
    _cache[cuenta] = (r["access_token"], time.time() + int(r.get("expires_in", 3000)), r.get("scope", ""))
    return _cache[cuenta][0]


def _llamar(cuenta, url, metodo="GET", datos=None, cabeceras=None, crudo=False):
    h = {"Authorization": "Bearer " + token_de(cuenta)}
    h.update(cabeceras or {})
    req = urllib.request.Request(url, data=datos, headers=h, method=metodo)
    try:
        r = urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        raise Fallo("HTTP %s en %s: %s" % (e.code, url.split("?")[0], e.read()[:300].decode("utf-8", "replace")))
    return r if crudo else json.loads(r or b"{}")


def cmd_cuentas(a):
    for n in CUENTAS:
        try:
            token_de(n)
            print("%-24s ok" % n)
        except Fallo as e:
            print("%-24s FALLA: %s" % (n, e))
        except Exception as e:
            print("%-24s FALLA: %s" % (n, str(e)[:100]))
    print("%-24s rechazada a proposito (Unipile / MCP)" % "personal")


def cmd_token(a):
    token_de(a.cuenta)
    _, hasta, scopes = _cache[a.cuenta]
    print("ok: caduca en %d s" % (hasta - time.time()))
    print("scopes: " + ", ".join(s.rsplit("/", 1)[-1] for s in scopes.split()))


def cmd_drive_ls(a):
    q = []
    if a.carpeta:
        q.append("'%s' in parents" % a.carpeta)
    if a.q:
        q.append("name contains '%s'" % a.q.replace("'", "\\'"))
    q.append("trashed=false")
    url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode({
        "q": " and ".join(q), "pageSize": a.max, "orderBy": "modifiedTime desc",
        "fields": "files(id,name,mimeType,size,modifiedTime)", "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"})
    for f in _llamar(a.cuenta, url).get("files", []):
        print("%s  %s  %s  %s" % (f["id"], f.get("modifiedTime", "")[:10], f["mimeType"].split(".")[-1].split("/")[-1], f["name"]))


def cmd_drive_get(a):
    if a.exportar:
        url = "https://www.googleapis.com/drive/v3/files/%s/export?mimeType=%s" % (a.id, urllib.parse.quote(a.exportar))
    else:
        url = "https://www.googleapis.com/drive/v3/files/%s?alt=media&supportsAllDrives=true" % a.id
    datos = _llamar(a.cuenta, url, crudo=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.destino)), exist_ok=True)
    open(a.destino, "wb").write(datos)
    print("bajado: %s (%d bytes)" % (a.destino, len(datos)))


def cmd_drive_put(a):
    if not os.path.exists(a.fichero):
        raise Fallo("no existe " + a.fichero)
    nombre = a.nombre or os.path.basename(a.fichero)
    tipo = mimetypes.guess_type(a.fichero)[0] or "application/octet-stream"
    cuerpo = open(a.fichero, "rb").read()
    if a.dry:
        print("[dry] %s %s (%d bytes, %s) en %s" % ("actualizaria" if a.actualiza else "subiria", nombre, len(cuerpo), tipo, a.actualiza or a.carpeta or "raiz"))
        return
    if a.actualiza:
        url = "https://www.googleapis.com/upload/drive/v3/files/%s?uploadType=media&supportsAllDrives=true" % a.actualiza
        r = _llamar(a.cuenta, url, "PATCH", cuerpo, {"Content-Type": tipo})
    else:
        meta = {"name": nombre}
        if a.carpeta:
            meta["parents"] = [a.carpeta]
        lim = "iamasters-os-limite"
        multi = ("--%s\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n%s\r\n--%s\r\nContent-Type: %s\r\n\r\n" % (
            lim, json.dumps(meta), lim, tipo)).encode() + cuerpo + ("\r\n--%s--" % lim).encode()
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true&fields=id,name,size"
        r = _llamar(a.cuenta, url, "POST", multi, {"Content-Type": "multipart/related; boundary=" + lim})
    print("subido: %s" % json.dumps(r, ensure_ascii=False))


def cmd_sheets_get(a):
    url = "https://sheets.googleapis.com/v4/spreadsheets/%s/values/%s" % (a.id, urllib.parse.quote(a.rango))
    print(json.dumps(_llamar(a.cuenta, url), ensure_ascii=False))


def cmd_gmail_list(a):
    base = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    ids = _llamar(a.cuenta, base + "?" + urllib.parse.urlencode({"q": a.q, "maxResults": a.max})).get("messages", [])
    for m in ids:
        d = _llamar(a.cuenta, "%s/%s?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date" % (base, m["id"]))
        h = {x["name"]: x["value"] for x in d["payload"]["headers"]}
        print("%s | %s | %s | %s" % (m["id"], h.get("Date", "")[:25], h.get("From", "")[:50], h.get("Subject", "")[:80]))
    if not ids:
        print("sin resultados")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("cuentas")
    s.set_defaults(f=cmd_cuentas)
    s = sub.add_parser("token")
    s.add_argument("cuenta")
    s.set_defaults(f=cmd_token)
    s = sub.add_parser("drive-ls")
    s.add_argument("cuenta")
    s.add_argument("--carpeta")
    s.add_argument("--q")
    s.add_argument("--max", type=int, default=50)
    s.set_defaults(f=cmd_drive_ls)
    s = sub.add_parser("drive-get")
    s.add_argument("cuenta")
    s.add_argument("id")
    s.add_argument("destino")
    s.add_argument("--exportar")
    s.set_defaults(f=cmd_drive_get)
    s = sub.add_parser("drive-put")
    s.add_argument("cuenta")
    s.add_argument("fichero")
    s.add_argument("--carpeta")
    s.add_argument("--actualiza")
    s.add_argument("--nombre")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(f=cmd_drive_put)
    s = sub.add_parser("sheets-get")
    s.add_argument("cuenta")
    s.add_argument("id")
    s.add_argument("rango")
    s.set_defaults(f=cmd_sheets_get)
    s = sub.add_parser("gmail-list")
    s.add_argument("cuenta")
    s.add_argument("--q", required=True)
    s.add_argument("--max", type=int, default=10)
    s.set_defaults(f=cmd_gmail_list)
    a = ap.parse_args()
    try:
        a.f(a)
    except Fallo as e:
        sys.exit("ERROR: %s" % e)


if __name__ == "__main__":
    main()
