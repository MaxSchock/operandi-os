"""Open a real browser window so Max logs into Skool once; save the session.

Runs headful through WSLg (DISPLAY=:0). Nothing is typed, read or logged by the
script: it just waits until the account is authenticated, then writes the
Playwright storage state to state/skool-session.json (chmod 600).

    python3 login.py
"""
import asyncio
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/max/.config")
from playwright_exe import chromium_exe  # noqa: E402

from playwright.async_api import async_playwright  # noqa: E402

STATE_DIR = os.path.join(HERE, "state")
STATE = os.path.join(STATE_DIR, "skool-session.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


async def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    os.chmod(STATE_DIR, 0o700)
    print("Abriendo una ventana de Chromium. Entra en Skool con tu cuenta.")
    print("Cuando estes dentro y veas tus comunidades, vuelve aqui: se guarda solo.\n")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            executable_path=chromium_exe(),
            args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1440,1000"],
        )
        ctx = await browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 1000},
                                        locale="en-US")
        page = await ctx.new_page()
        await page.goto("https://www.skool.com/login", wait_until="domcontentloaded")

        for _ in range(180):  # up to 15 minutes
            await page.wait_for_timeout(5000)
            try:
                cookies = await ctx.cookies("https://www.skool.com")
            except Exception:
                break
            names = {c["name"] for c in cookies}
            if any(n.lower().startswith(("auth", "session", "sk_")) for n in names):
                await ctx.storage_state(path=STATE)
                os.chmod(STATE, 0o600)
                print(f"Sesion guardada en {STATE} (solo lectura para tu usuario).")
                print("Cierra la ventana cuando quieras. Ya puedo entrar a tus comunidades.")
                await page.wait_for_timeout(3000)
                await browser.close()
                return 0
        print("No detecte sesion iniciada. Vuelve a lanzarlo cuando puedas.")
        await browser.close()
    return 1


raise SystemExit(asyncio.run(main()))
