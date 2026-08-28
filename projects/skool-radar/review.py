"""Export what is new into one markdown file, ready to be judged.

The judging itself happens in a Claude Code session: it reads this file against
interests.md and writes the digest. Keeping the LLM pass out of cron means the
criterion can be argued with and changed, instead of frozen in a prompt.

    python3 review.py [--community <slug>] [--days 7] [--all]
    python3 review.py --mark            # flag the exported items as reported
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402

OUT = os.path.join(HERE, "out")


def fetch(con, community, days, include_reported):
    sql = ("SELECT id, community, title, content, author, url, upvotes, n_comments, "
           "videos, transcript, created_at, kind, course, module FROM posts WHERE 1=1")
    p = []
    if community:
        sql += " AND community = ?"
        p.append(community)
    if not include_reported:
        sql += " AND reported_at IS NULL"
    if days:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        sql += " AND (created_at >= ? OR kind = 'lesson')"
        p.append(since)
    sql += " ORDER BY (upvotes + n_comments) DESC, created_at DESC"
    return con.execute(sql, p).fetchall()


def comments_for(con, post_id, limit=12):
    return con.execute(
        "SELECT depth, author, content FROM comments WHERE post_id = ? "
        "ORDER BY upvotes DESC LIMIT ?", (post_id, limit)).fetchall()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--community")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--all", action="store_true", help="incluye lo ya reportado")
    ap.add_argument("--mark", action="store_true", help="marca lo exportado como reportado")
    args = ap.parse_args()

    con = db.connect()
    rows = fetch(con, args.community, None if args.all else args.days, args.all)
    if not rows:
        print("Nada nuevo que revisar.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(OUT, f"{stamp}-material.md")
    n_vid = 0
    with open(path, "w") as f:
        f.write(f"# Material de Skool sin revisar · {stamp}\n\n")
        f.write(f"{len(rows)} entradas\n\n")
        for r in rows:
            vids = json.loads(r["videos"] or "[]")
            f.write(f"\n---\n\n## {r['title']}\n\n")
            meta = [f"{r['community']}", f"{r['kind']}", f"por {r['author'] or '-'}",
                    f"{r['upvotes']} votos", f"{r['n_comments']} comentarios",
                    (r["created_at"] or "")[:10]]
            if r["course"]:
                meta.append(f"curso: {r['course']} / {r['module']}")
            f.write(" · ".join(str(m) for m in meta) + f"\n{r['url']}\n\n")
            if r["content"]:
                f.write(r["content"].strip()[:4000] + "\n\n")
            for v in vids:
                mins = round((v.get("len_ms") or 0) / 60000)
                f.write(f"**Vídeo** ({v['provider']}, {mins} min): {v.get('title') or ''}\n")
            if r["transcript"]:
                n_vid += 1
                f.write("\n<notas-del-video>\n" + r["transcript"].strip() + "\n</notas-del-video>\n")
            elif vids:
                f.write("\n_(vídeo sin analizar todavía: `python3 video.py`)_\n")
            cs = comments_for(con, r["id"])
            if cs:
                f.write("\n**Comentarios destacados**\n\n")
                for c in cs:
                    txt = (c["content"] or "").replace("\n", " ").strip()[:400]
                    if txt:
                        f.write(f"{'  ' * (c['depth'] or 0)}- {c['author']}: {txt}\n")
        f.write("\n")

    print(f"{len(rows)} entradas ({n_vid} con vídeo analizado) -> {path}")
    if args.mark:
        con.executemany("UPDATE posts SET reported_at = ? WHERE id = ?",
                        [(db.now(), r["id"]) for r in rows])
        con.commit()
        print("marcadas como reportadas")
    return 0


raise SystemExit(main())
