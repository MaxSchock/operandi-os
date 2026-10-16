"""Open a OneTimeSecret link once (one-shot links from clients: the content is lost if the first open fails,
so HTML, text and a screenshot go to disk in the same pass; the secret itself never reaches the chat) and store the secret in a 0600 file. Never prints the secret.
Usage: ots_fetch.py <url> <dest-file>
"""
import os, sys, time, re
sys.path.insert(0, '/home/max/.config')
from playwright_exe import chromium_exe
from playwright.sync_api import sync_playwright

url, dest = sys.argv[1], os.path.expanduser(sys.argv[2])
os.makedirs(os.path.dirname(dest), exist_ok=True)
S = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=chromium_exe(), args=['--no-sandbox', '--disable-dev-shm-usage'])
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    print("pagina 1:", pg.title(), "|", pg.url)
    pg.screenshot(path=S + "/ots1.png")
    body1 = pg.inner_text("body")
    if re.search(r"(no longer available|not found|already been viewed|burned|expired)", body1, re.I):
        sys.exit("el enlace ya no vale: " + body1[:300].replace("\n", " | "))
    clicked = False
    for sel in ("button[type=submit]", "button:has-text('View')", "button:has-text('Continue')", "button:has-text('reveal')", "a:has-text('View')"):
        try:
            pg.click(sel, timeout=3000); clicked = True; print("pulsado", sel); break
        except Exception:
            pass
    time.sleep(3)
    # keep everything in a private file before trying to parse (nothing gets lost)
    raw = pg.content()
    fd = os.open(dest + ".html", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, raw.encode()); os.close(fd)
    secret = None
    for sel in ("textarea", "pre", "#secret-content", "[data-testid=secret-content]", "code"):
        try:
            el = pg.locator(sel).first
            if el.count():
                v = el.input_value() if sel == "textarea" else el.inner_text()
                v = v.strip()
                if v and len(v) < 500 and "\n" not in v:
                    secret = v; print("secreto en", sel, "| longitud", len(v)); break
        except Exception:
            pass
    body2 = pg.inner_text("body")
    fd = os.open(dest + ".txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, body2.encode()); os.close(fd)
    if secret:
        fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, (secret + "\n").encode()); os.close(fd)
        print("guardado en", dest)
    else:
        print("no he localizado el secreto en la página; texto completo guardado en", dest + ".txt", "(revisar sin imprimir)")
    b.close()
