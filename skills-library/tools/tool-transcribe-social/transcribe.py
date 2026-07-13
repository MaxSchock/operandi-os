#!/usr/bin/env python3
"""
transcribe-social — descarga audio de Reels/TikTok/YouTube y lo transcribe con Groq Whisper.
Si la URL es de Instagram, además extrae caption + hashtags + comentarios públicos.

Uso:
    python3 transcribe.py <url> [--lang es|en|auto] [--out path/dir]

Salida: imprime markdown a stdout. Si --out, también guarda <shortcode>.md ahí.
"""

import argparse
from datetime import date
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3-turbo"
MAX_GROQ_BYTES = 24 * 1024 * 1024  # margen sobre el límite de 25MB


def load_groq_key() -> str:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key

    candidates = [
        Path.cwd() / ".env",
        Path.cwd() / ".env.local",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            if line.startswith("GROQ_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ERROR: GROQ_API_KEY no encontrada. Configúrala como variable de entorno o en .env del repo.")


def require_binary(name: str, install_hint: str) -> None:
    if not shutil.which(name):
        sys.exit(f"ERROR: falta {name} en PATH. Instala con: {install_hint}")


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "instagram.com" in host:
        return "instagram"
    if "tiktok.com" in host:
        return "tiktok"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "twitter.com" in host or "x.com" in host:
        return "twitter"
    if "facebook.com" in host or "fb.watch" in host:
        return "facebook"
    return "other"


def ig_shortcode(url: str) -> Optional[str]:
    m = re.search(r"instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def download_audio(url: str, workdir: Path) -> Tuple[Path, dict]:
    """Descarga audio + metadata con yt-dlp. Devuelve (ruta_audio, info_dict)."""
    require_binary("yt-dlp", "brew install yt-dlp")
    out_tpl = str(workdir / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "5",  # ~64kbps, suficiente para voz
        "--no-playlist",
        "--write-info-json",
        "--no-warnings",
        "-o", out_tpl,
        url,
    ]
    r = run(cmd)
    if r.returncode != 0:
        sys.exit(f"ERROR yt-dlp:\n{r.stderr.strip()}")

    audios = list(workdir.glob("*.mp3"))
    if not audios:
        sys.exit("ERROR: yt-dlp no produjo audio mp3.")
    audio = audios[0]

    info = {}
    for ij in workdir.glob("*.info.json"):
        try:
            info = json.loads(ij.read_text())
        except Exception:
            pass
        break
    return audio, info


def shrink_if_needed(audio: Path, workdir: Path) -> Path:
    """Si supera el límite de Groq, recomprime a 16kHz mono."""
    if audio.stat().st_size <= MAX_GROQ_BYTES:
        return audio
    require_binary("ffmpeg", "brew install ffmpeg")
    out = workdir / f"{audio.stem}-16k.mp3"
    r = run([
        "ffmpeg", "-y", "-i", str(audio),
        "-ac", "1", "-ar", "16000", "-b:a", "32k",
        str(out),
    ])
    if r.returncode != 0:
        sys.exit(f"ERROR ffmpeg al recomprimir: {r.stderr.strip()}")
    return out


def transcribe_groq(audio: Path, lang: str, key: str) -> str:
    headers = {"Authorization": f"Bearer {key}"}
    data = {"model": GROQ_MODEL, "response_format": "text"}
    if lang and lang != "auto":
        data["language"] = lang
    with audio.open("rb") as f:
        files = {"file": (audio.name, f, "audio/mpeg")}
        r = requests.post(GROQ_ENDPOINT, headers=headers, data=data, files=files, timeout=120)
    if r.status_code != 200:
        sys.exit(f"ERROR Groq {r.status_code}: {r.text[:400]}")
    return r.text.strip()


def fetch_instagram_meta(shortcode: str) -> dict:
    """Extrae caption, hashtags, comentarios públicos via Instaloader (sin login)."""
    try:
        import instaloader
    except ImportError:
        return {}
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=True,
        save_metadata=False,
        post_metadata_txt_pattern="",
        quiet=True,
    )
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        return {"_error": f"instaloader: {e}"}

    caption = post.caption or ""
    hashtags = sorted(set(post.caption_hashtags or []))
    mentions = sorted(set(post.caption_mentions or []))

    comments = []
    try:
        for c in post.get_comments():
            comments.append({
                "owner": c.owner.username,
                "text": (c.text or "").strip(),
                "likes": getattr(c, "likes_count", 0),
            })
            if len(comments) >= 30:
                break
    except Exception:
        pass

    return {
        "owner": post.owner_username,
        "date": str(post.date_utc),
        "likes": post.likes,
        "comments_count": post.comments,
        "video_duration": getattr(post, "video_duration", None),
        "caption": caption,
        "hashtags": hashtags,
        "mentions": mentions,
        "top_comments": comments,
    }


def render_markdown(url: str, platform: str, info: dict, ig_meta: dict, transcript: str) -> str:
    title = info.get("title") or info.get("description") or url
    uploader = info.get("uploader") or info.get("channel") or info.get("creator") or ""
    duration = info.get("duration")
    view_count = info.get("view_count")
    like_count = info.get("like_count")

    out = []
    out.append(f"# Transcripción social — {platform}")
    out.append("")
    out.append(f"- **URL:** {url}")
    if uploader:
        out.append(f"- **Autor:** {uploader}")
    if duration:
        out.append(f"- **Duración:** {duration}s")
    if view_count:
        out.append(f"- **Vistas:** {view_count:,}".replace(",", "."))
    if like_count:
        out.append(f"- **Likes:** {like_count:,}".replace(",", "."))

    if ig_meta and "_error" not in ig_meta:
        out.append(f"- **Owner IG:** @{ig_meta.get('owner')}")
        out.append(f"- **Fecha:** {ig_meta.get('date')}")
        out.append(f"- **Likes IG:** {ig_meta.get('likes')}")
        out.append(f"- **Comentarios totales:** {ig_meta.get('comments_count')}")
        if ig_meta.get("hashtags"):
            out.append(f"- **Hashtags:** {' '.join('#' + h for h in ig_meta['hashtags'])}")
        if ig_meta.get("mentions"):
            out.append(f"- **Menciones:** {' '.join('@' + m for m in ig_meta['mentions'])}")

    if ig_meta and ig_meta.get("caption"):
        out.append("")
        out.append("## Caption del post")
        out.append("")
        out.append(ig_meta["caption"].strip())

    out.append("")
    out.append("## Transcripción del audio")
    out.append("")
    out.append(transcript if transcript else "_(sin audio detectable)_")

    if ig_meta and ig_meta.get("top_comments"):
        out.append("")
        out.append(f"## Comentarios públicos ({len(ig_meta['top_comments'])} primeros)")
        out.append("")
        for c in ig_meta["top_comments"]:
            text = c["text"].replace("\n", " ").strip()
            out.append(f"- **@{c['owner']}** ({c['likes']} ❤): {text}")

    if ig_meta and ig_meta.get("_error"):
        out.append("")
        out.append(f"_Nota: metadata IG no disponible ({ig_meta['_error']})._")

    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--lang", default="es", help="es|en|auto (default es)")
    ap.add_argument("--out", default=None, help="directorio para guardar .md")
    args = ap.parse_args()

    key = load_groq_key()
    platform = detect_platform(args.url)

    with tempfile.TemporaryDirectory(prefix="transcribe-social-") as tmp:
        workdir = Path(tmp)
        print(f"⬇️  Descargando audio de {platform}…", file=sys.stderr)
        audio, info = download_audio(args.url, workdir)
        audio = shrink_if_needed(audio, workdir)

        ig_meta = {}
        if platform == "instagram":
            sc = ig_shortcode(args.url)
            if sc:
                print(f"📸 Extrayendo metadata IG de {sc}…", file=sys.stderr)
                ig_meta = fetch_instagram_meta(sc)

        print(f"🎙  Transcribiendo con Groq {GROQ_MODEL}…", file=sys.stderr)
        transcript = transcribe_groq(audio, args.lang, key)

        md = render_markdown(args.url, platform, info, ig_meta, transcript)
        print(md)

        outdir = Path(args.out).expanduser() if args.out else Path.cwd() / "projects" / "transcribe-social" / date.today().isoformat()
        outdir.mkdir(parents=True, exist_ok=True)
        slug = info.get("id") or ig_shortcode(args.url) or "transcript"
        outfile = outdir / f"{slug}.md"
        outfile.write_text(md)
        print(f"Guardado en {outfile}", file=sys.stderr)


if __name__ == "__main__":
    main()
