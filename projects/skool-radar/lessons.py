"""Pull the written body of each classroom lesson.

Skool only ships the description of the lesson that is currently open, so this
visits them one by one and stores the text. That text is the cheap layer: what
the lesson teaches, the gotchas the author calls out, and the attached
resources. Video analysis then only has to touch what the text says is worth it.

    python3 lessons.py --course "N8N" [--limit 20] [--redo]
    python3 lessons.py --all
"""
import argparse
import asyncio
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402
from lib.skool import Skool  # noqa: E402

STATE = os.path.join(HERE, "state", "skool-session.json")


def find_node(node, target_id):
    """Locate a lesson inside the {course, children} tree."""
    inner = node.get("course") or node
    if inner.get("id") == target_id:
        return inner
    for child in (node.get("children") or []):
        hit = find_node(child, target_id)
        if hit:
            return hit
    return None


async def run(args):
    con = db.connect()
    sql = ("SELECT id, title, url, course FROM posts WHERE kind='lesson' "
           "AND community='ia-masters-automations'")
    p = []
    if args.course:
        sql += " AND course LIKE ?"
        p.append(f"%{args.course}%")
    if not args.redo:
        sql += " AND (content IS NULL OR content = '')"
    sql += " ORDER BY course, module"
    if args.limit:
        sql += f" LIMIT {int(args.limit)}"
    rows = con.execute(sql, p).fetchall()
    if not rows:
        print("Nada pendiente.")
        return 0
    print(f"{len(rows)} lecciones por leer")

    ok = empty = 0
    async with Skool(storage_state=STATE) as sk:
        for i, r in enumerate(rows, 1):
            course_id = r["url"].split("/classroom/")[1].split("?")[0]
            url = (f"https://www.skool.com/ia-masters-automations/classroom/"
                   f"{course_id[:8]}?md={r['id']}")
            try:
                props = await sk.page_props(url, wait_ms=2600)
            except Exception as e:
                print(f"  [{i}/{len(rows)}] error de carga: {str(e)[:70]}")
                continue
            node = (props or {}).get("course") or {}
            hit = find_node(node, r["id"])
            md = (hit or {}).get("metadata") or {}
            text = sk._rich_text(md.get("desc"))
            transcript = md.get("transcript") or ""
            if text or transcript:
                con.execute(
                    "UPDATE posts SET content = ?, transcript = COALESCE(NULLIF(?,''), transcript) "
                    "WHERE id = ?", (text, transcript, r["id"]))
                ok += 1
                flag = " +transcripcion" if transcript else ""
                print(f"  [{i}/{len(rows)}] {len(text):>5} letras{flag} · {str(r['title'])[:52]}")
            else:
                empty += 1
                print(f"  [{i}/{len(rows)}] sin texto · {str(r['title'])[:52]}")
            if i % 10 == 0:
                con.commit()
        con.commit()
    print(f"\ncon texto: {ok} · vacías: {empty}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", help="filtro por nombre de curso, p.ej. N8N")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--redo", action="store_true", help="revisita las que ya tienen texto")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    raise SystemExit(asyncio.run(run(args)))


main()
