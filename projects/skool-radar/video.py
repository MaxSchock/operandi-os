"""Watch the videos, not just read the posts.

For every collected post or lesson that carries a video and has no notes yet:
  YouTube  -> Gemini reads the URL directly (visual + audio, no download)
  anything else (Skool-hosted, Loom, Vimeo) -> yt-dlp pulls it, scp to
  ki-prod-01, Gemini File API, then both copies are deleted.

The Gemini key never leaves ki-prod-01 and is never printed.

    python3 video.py [--limit 5] [--community <slug>] [--max-min 45]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402

REMOTE = "ki-prod-01"
REMOTE_SCRIPT = "/root/skool-gemini_video.py"
YTDLP = os.path.join(HERE, ".venv", "bin", "yt-dlp")


def ensure_remote_script():
    subprocess.run(["scp", "-q", os.path.join(HERE, "remote", "gemini_video.py"),
                    f"{REMOTE}:{REMOTE_SCRIPT}"], check=True)


def gemini_youtube(url):
    r = subprocess.run(["ssh", REMOTE, "python3", REMOTE_SCRIPT, "youtube", f'"{url}"'],
                       capture_output=True, text=True, timeout=1800)
    return r.stdout.strip(), r.stderr.strip()


def gemini_file(local_path):
    remote_path = f"/tmp/{os.path.basename(local_path)}"
    subprocess.run(["scp", "-q", local_path, f"{REMOTE}:{remote_path}"], check=True)
    r = subprocess.run(["ssh", REMOTE, "python3", REMOTE_SCRIPT, "file", remote_path],
                       capture_output=True, text=True, timeout=3600)
    return r.stdout.strip(), r.stderr.strip()


def download(url, workdir):
    """Grab a compact copy: 480p is plenty for reading slides and UI."""
    out = os.path.join(workdir, "v.mp4")
    cmd = [YTDLP, "-q", "--no-warnings", "-f",
           "bv*[height<=480]+ba/b[height<=480]/b", "--merge-output-format", "mp4",
           "-o", out, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
    if not os.path.exists(out):
        return None, (r.stderr or r.stdout)[-300:]
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--community")
    ap.add_argument("--max-min", type=int, default=60, help="salta videos mas largos")
    args = ap.parse_args()

    con = db.connect()
    sql = ("SELECT id, community, title, url, videos FROM posts "
           "WHERE videos NOT IN ('[]','') AND transcript IS NULL")
    params = []
    if args.community:
        sql += " AND community = ?"
        params.append(args.community)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(args.limit)
    rows = con.execute(sql, params).fetchall()
    if not rows:
        print("No hay videos pendientes.")
        return 0

    ensure_remote_script()
    for row in rows:
        vids = json.loads(row["videos"])
        v = vids[0]
        mins = round((v.get("len_ms") or 0) / 60000)
        head = f"{row['title'][:60]} ({v['provider']}, {mins} min)"
        if mins > args.max_min:
            print(f"  saltado por duracion: {head}")
            continue
        print(f"  analizando: {head}")

        if v["provider"] == "youtube" and v.get("video_id"):
            notes, err = gemini_youtube(f"https://www.youtube.com/watch?v={v['video_id']}")
        else:
            with tempfile.TemporaryDirectory() as wd:
                path, derr = download(v.get("url") or row["url"], wd)
                if not path:
                    print(f"    no se pudo descargar: {derr}")
                    continue
                size_mb = os.path.getsize(path) / 1e6
                print(f"    descargado {size_mb:.0f} MB, subiendo a ki-prod-01")
                notes, err = gemini_file(path)

        if not notes:
            print(f"    sin notas: {err[:200]}")
            continue
        con.execute("UPDATE posts SET transcript = ? WHERE id = ?", (notes, row["id"]))
        con.commit()
        print(f"    guardadas {len(notes)} letras de notas")
    return 0


raise SystemExit(main())
