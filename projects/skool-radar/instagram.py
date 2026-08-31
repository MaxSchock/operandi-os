"""Pull what a handful of Instagram creators publish, into the same radar.

Instagram is not Skool: driving it with Max's own logged-in session is what gets
accounts restricted, and the official Graph API only reaches your own
professional account (business_discovery aside). So this goes through Apify,
which brings back public posts without Max's account touching anything.

Rows land in the same table as Skool, with community = "ig:<handle>", so
review.py and the video pass work unchanged.

    python3 instagram.py --profiles creador1,creador2 [--limit 20]
    python3 instagram.py --profiles creador1 --reels
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402

ENV = os.path.expanduser("~/iamasters-os/.env")
ACTOR_POSTS = "apify~instagram-scraper"
API = "https://api.apify.com/v2"


def token():
    """Read the Apify token from the .env without ever printing it."""
    with open(ENV) as f:
        for line in f:
            if line.startswith("APIFY_API_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("No hay APIFY_API_TOKEN en ~/iamasters-os/.env")


def run_actor(actor, payload, tok, timeout=600):
    url = f"{API}/acts/{actor}/run-sync-get-dataset-items?token={tok}&timeout={timeout}"
    out = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 60)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        raise SystemExit(f"Apify no devolvio JSON: {out.stdout[:200]}")


def row_from(item, handle):
    """One Instagram post as a radar row."""
    videos = []
    if item.get("videoUrl"):
        videos.append({"provider": "instagram", "video_id": item.get("shortCode"),
                       "url": item["videoUrl"], "len_ms": None,
                       "title": (item.get("caption") or "")[:80]})
    caption = item.get("caption") or ""
    return {
        "id": item.get("id") or item.get("shortCode"),
        "community": f"ig:{handle}",
        "slug": item.get("shortCode"),
        "url": item.get("url"),
        "kind": "post",
        # Instagram has no titles: the first line of the caption is the closest thing
        "title": (caption.strip().splitlines() or ["(sin texto)"])[0][:120],
        "content": caption,
        "author": handle,
        "labels": " ".join(item.get("hashtags") or []),
        "upvotes": item.get("likesCount") or 0,
        "n_comments": item.get("commentsCount") or 0,
        "videos": json.dumps(videos, ensure_ascii=False),
        "created_at": item.get("timestamp"),
        "updated_at": item.get("timestamp"),
        "course": None,
        "module": None,
    }


def save_comments(con, post_id, item):
    rows = []
    for c in (item.get("latestComments") or []):
        cid = c.get("id")
        if not cid:
            continue
        rows.append((cid, post_id, None, 0, c.get("ownerUsername"),
                     c.get("text"), c.get("likesCount") or 0, c.get("timestamp")))
    if rows:
        db.save_comments(con, post_id, rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True, help="handles separados por coma")
    ap.add_argument("--limit", type=int, default=20, help="publicaciones por perfil")
    args = ap.parse_args()

    tok = token()
    con = db.connect()
    handles = [h.strip().lstrip("@") for h in args.profiles.split(",") if h.strip()]

    for h in handles:
        known = db.known_post_ids(con, f"ig:{h}")
        run_id = db.start_run(con, f"ig:{h}")
        print(f"\n@{h} · {len(known)} publicaciones ya en la base")
        items = run_actor(ACTOR_POSTS, {
            "directUrls": [f"https://www.instagram.com/{h}/"],
            "resultsType": "posts",
            "resultsLimit": args.limit,
            "addParentData": False,
        }, tok)
        if isinstance(items, dict) and items.get("error"):
            print("  error de Apify:", str(items["error"])[:160])
            continue
        nuevos = 0
        for it in items:
            if not isinstance(it, dict) or not (it.get("id") or it.get("shortCode")):
                continue
            row = row_from(it, h)
            if row["id"] in known:
                continue
            db.upsert_post(con, row)
            n = save_comments(con, row["id"], it)
            nuevos += 1
            vid = " [reel]" if it.get("videoUrl") else ""
            print(f"  + {str(row['created_at'])[:10]} {row['upvotes']:>7} likes · "
                  f"{row['title'][:58]}{vid} ({n} comentarios)")
        con.commit()
        db.end_run(con, run_id, nuevos)
        print(f"  nuevas: {nuevos} de {len(items)} traidas")
        time.sleep(1)
    return 0


raise SystemExit(main())
