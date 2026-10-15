#!/usr/bin/env python3
"""Captura (PNG) o PDF de una pagina web o de un HTML local con el chromium ya instalado.

Sustituye a los shot.py, render.py y pdf.py que se reescribian en 58 sesiones con el mismo
arranque (executable_path, --no-sandbox, viewport, new_context, full_page, print_background).
El chromium se resuelve con ~/.config/playwright-exe.py (la version que pide el paquete casi
nunca coincide con la cacheada). Con `python3 -I` el paquete playwright "no existe" porque -I
ignora ~/.local/lib: este script añade esa ruta él mismo.

Uso (siempre con -I):
  render-pagina.py <url|fichero.html> --png salida.png [--ancho 1280] [--alto 800] [--completa]
  render-pagina.py <url|fichero.html> --pdf salida.pdf [--formato A4] [--escala 1.0]
  render-pagina.py <url|fichero.html> --png salida.png --movil          (390x844, x2, tactil)
  render-pagina.py <url|fichero.html> --png salida.png --selector "#hero"   (solo ese elemento)
Opciones:
  --espera MS      pausa extra tras cargar (por defecto 500)
  --sin-red-ociosa no esperar a "networkidle" (paginas con websockets o sondeos que nunca se calman)
  --bloquea PATRON no cargar las URLs que contengan el patron (repetible; p. ej. analytics, gtm)
  --cookies-json F cookies de sesion en JSON (lista de objetos de Playwright); nunca se imprimen
  --consola        imprime errores de consola y respuestas >=400 (diagnostico)
El PDF respeta @page del CSS (prefer_css_page_size) y pinta fondos. Para entregar un PDF a Max
despues: scripts/abrir.sh <archivo>. Para PDF de mucho texto weasyprint va mejor (ver CLAUDE.md).
No hace clic, no escribe en formularios y no envia nada: solo mira y captura.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys

for d in glob.glob(os.path.expanduser("~/.local/lib/python3*/site-packages")):
    if d not in sys.path:
        sys.path.append(d)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("falta el paquete playwright (pip install --user playwright) o el chromium en ~/.cache/ms-playwright")


def chromium():
    spec = importlib.util.spec_from_file_location("pe", os.path.expanduser("~/.config/playwright-exe.py"))
    pe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pe)
    return pe.chromium_exe()


def destino(x):
    if x.startswith(("http://", "https://", "file://", "data:")):
        return x
    ruta = os.path.abspath(os.path.expanduser(x))
    if not os.path.exists(ruta):
        sys.exit("no existe: " + ruta)
    return "file://" + ruta


def main():
    ap = argparse.ArgumentParser(description="Captura o PDF con chromium")
    ap.add_argument("origen")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--png")
    g.add_argument("--pdf")
    ap.add_argument("--ancho", type=int, default=1280)
    ap.add_argument("--alto", type=int, default=800)
    ap.add_argument("--movil", action="store_true")
    ap.add_argument("--completa", action="store_true")
    ap.add_argument("--selector")
    ap.add_argument("--espera", type=int, default=500)
    ap.add_argument("--sin-red-ociosa", action="store_true")
    ap.add_argument("--bloquea", action="append", default=[])
    ap.add_argument("--cookies-json")
    ap.add_argument("--formato", default="A4")
    ap.add_argument("--escala", type=float, default=1.0)
    ap.add_argument("--consola", action="store_true")
    a = ap.parse_args()

    ctx_args = {"viewport": {"width": a.ancho, "height": a.alto}}
    if a.movil:
        ctx_args = {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2, "is_mobile": True, "has_touch": True}
    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True, executable_path=chromium(),
                                args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = nav.new_context(**ctx_args)
        if a.cookies_json:
            ctx.add_cookies(json.load(open(os.path.expanduser(a.cookies_json))))
        if a.bloquea:
            ctx.route("**/*", lambda r: r.abort() if any(b in r.request.url for b in a.bloquea) else r.continue_())
        pg = ctx.new_page()
        if a.consola:
            pg.on("console", lambda m: print("consola[%s] %s" % (m.type, m.text[:200])) if m.type in ("error", "warning") else None)
            pg.on("response", lambda r: print("HTTP %s %s" % (r.status, r.url[:140])) if r.status >= 400 else None)
        pg.goto(destino(a.origen), wait_until="load", timeout=60000)
        if not a.sin_red_ociosa:
            try:
                pg.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
        pg.wait_for_timeout(a.espera)
        if a.png:
            os.makedirs(os.path.dirname(os.path.abspath(a.png)), exist_ok=True)
            if a.selector:
                pg.locator(a.selector).first.screenshot(path=a.png)
            else:
                pg.screenshot(path=a.png, full_page=a.completa)
            print("png: %s (%d bytes)" % (a.png, os.path.getsize(a.png)))
        else:
            os.makedirs(os.path.dirname(os.path.abspath(a.pdf)), exist_ok=True)
            pg.pdf(path=a.pdf, format=a.formato, prefer_css_page_size=True, print_background=True, scale=a.escala)
            print("pdf: %s (%d bytes)" % (a.pdf, os.path.getsize(a.pdf)))
        nav.close()


if __name__ == "__main__":
    main()
