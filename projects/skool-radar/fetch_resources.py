"""Download the files attached to classroom lessons.

Skool serves attachments only through a signed URL created when you click the
resource, so there is nothing to fetch by address: the click has to happen in a
real browser. This opens each lesson, clicks its resources one by one and saves
whatever comes back.

    python3 fetch_resources.py --course "Claude Code" [--limit 10] [--redo]

Read-only towards Skool: clicking a resource downloads it, nothing else.
"""
import argparse
import asyncio
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402
from lib.skool import Skool  # noqa: E402

STATE = os.path.join(HERE, "state", "skool-session.json")
OUT = os.path.join(HERE, "data", "resources")


def slug(text, n=60):
    text = re.sub(r"[^\w\s.-]", "", (text or "sin-titulo"), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", text.strip())[:n].strip("-.") or "sin-titulo"


async def grab(sk, item, dest_dir):
    """Ask Skool for a signed URL and save the file. Returns (path, error)."""
    url, err = await sk.download_url(item["file_id"])
    if not url or not url.startswith("http"):
        return None, f"sin url ({err or url})"
    try:
        resp = await sk.ctx.request.get(url, timeout=120000)
        if not resp.ok:
            return None, f"http {resp.status}"
        body = await resp.body()
    except Exception as e:
        return None, str(e).splitlines()[0][:80]
    os.makedirs(dest_dir, exist_ok=True)
    name = item["file_name"] or f"{item['file_id']}.bin"
    path = os.path.join(dest_dir, slug(os.path.splitext(name)[0], 70) + os.path.splitext(name)[1])
    with open(path, "wb") as f:
        f.write(body)
    return path, None


async def run(args):
    con = db.connect()
    sql = ("SELECT r.id, r.title, r.file_id, r.file_name, r.file_type, p.id pid, p.url, p.title ptitle, "
           "p.course, p.module FROM resources r JOIN posts p ON p.id = r.post_id "
           "WHERE r.file_id != ''")
    params = []
    if args.course:
        sql += " AND p.course LIKE ?"
        params.append(f"%{args.course}%")
    if not args.redo:
        sql += " AND (r.local_path IS NULL OR r.local_path = '')"
    sql += " ORDER BY p.course, p.module, p.title"
    rows = con.execute(sql, params).fetchall()
    if not rows:
        print("No hay adjuntos pendientes.")
        return 0

    by_lesson = {}
    for r in rows:
        by_lesson.setdefault(r["pid"], []).append(r)
    print(f"{len(rows)} adjuntos en {len(by_lesson)} lecciones")

    saved = failed = 0
    async with Skool(storage_state=STATE) as sk:
        for n, (pid, items) in enumerate(by_lesson.items(), 1):
            first = items[0]
            dest = os.path.join(OUT, slug(first["course"], 40), slug(first["ptitle"]))
            if args.limit and n > args.limit:
                break
            print(f"  [{n}/{len(by_lesson)}] {str(first['ptitle'])[:52]}")
            for it in items:
                path, err = await grab(sk, it, dest)
                if path:
                    con.execute("UPDATE resources SET local_path = ? WHERE id = ?", (path, it["id"]))
                    saved += 1
                    size = os.path.getsize(path)
                    print(f"        ok  {size/1024:7.1f} KB  {it['file_name']}")
                else:
                    failed += 1
                    print(f"        --  {it['file_name']}  ({err})")
            con.commit()
    print(f"\nguardados: {saved} · fallidos: {failed}")
    print(f"carpeta: {OUT}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course")
    ap.add_argument("--limit", type=int, help="numero de lecciones, no de ficheros")
    ap.add_argument("--redo", action="store_true")
    args = ap.parse_args()
    raise SystemExit(asyncio.run(run(args)))


main()
