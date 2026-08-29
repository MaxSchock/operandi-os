"""Probe: discover which internal XHR endpoints Skool calls when opening a post.

Run once to learn the comment/classroom API shape. Read-only, no session needed
for a public community.
"""
import asyncio
import json
import sys

sys.path.insert(0, "/home/max/.config")
from playwright_exe import chromium_exe  # noqa: E402

from playwright.async_api import async_playwright  # noqa: E402

TARGET = sys.argv[1] if len(sys.argv) > 1 else (
    "https://www.skool.com/ai-automation-society/"
    "new-video-i-cloned-calendly-and-now-its-free-forever"
)


async def main():
    calls = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            executable_path=chromium_exe(),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 1000},
        )
        page = await ctx.new_page()

        async def on_response(resp):
            url = resp.url
            if "skool.com" not in url:
                return
            if any(url.endswith(ext) for ext in (".js", ".css", ".png", ".jpg", ".webp", ".svg", ".woff2")):
                return
            ct = (resp.headers or {}).get("content-type", "")
            if "json" not in ct:
                return
            try:
                body = await resp.text()
            except Exception:
                body = ""
            calls.append({
                "status": resp.status,
                "method": resp.request.method,
                "url": url,
                "bytes": len(body),
                "head": body[:300],
            })

        page.on("response", on_response)
        await page.goto(TARGET, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(9000)
        await browser.close()

    for c in calls:
        print(f"[{c['status']}] {c['method']} {c['bytes']:>7}B  {c['url'][:150]}")
    print("\n--- bodies of the biggest json responses ---")
    for c in sorted(calls, key=lambda x: -x["bytes"])[:4]:
        print(f"\n### {c['url'][:180]}\n{c['head']}")


asyncio.run(main())
