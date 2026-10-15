#!/usr/bin/env python3
"""Transcripcion literal de audio y video con Gemini 2.5 Pro a traves de OpenRouter.

Generaliza transcribir-openrouter.py (solo .ogg). Sirve para ogg/opus de WhatsApp, mp3, m4a,
wav, flac, aac y para video (mp4, mov, mkv, webm, m4v: se transcribe SOLO la pista de audio;
para analizar lo que se ve en pantalla hace falta Gemini con video nativo, ver CLAUDE.md global).

Uso (siempre con -I):
    python3 -I scripts/transcribir-medios.py <fichero|carpeta> [...] [opciones]

Opciones:
    --salida DIR       guarda <nombre>.txt por fichero en DIR (ademas de imprimir)
    --tramo-min N      longitud de cada tramo en minutos cuando hay que trocear (por defecto 10)
    --max-mb N         tamano maximo por peticion en MB; por encima se trocea (por defecto 12)
    --idioma TEXTO     pista de idioma para el modelo (por defecto: el que se hable, es/de/en)
    --modelo ID        modelo de OpenRouter (por defecto google/gemini-2.5-pro)
    --solo-plan        no llama a la red: muestra duracion, tamano, tramos y silencios

Que hace:
  * El ogg/opus de WhatsApp pequeno va tal cual (sin ffmpeg). Todo lo demas se convierte a
    mp3 mono 48 kbps con ffmpeg (el video pierde la imagen).
  * Si el fichero pasa de --max-mb o de --tramo-min minutos se corta en tramos y cada tramo
    es una peticion; el texto sale con la marca [tramo i/n mm:ss-mm:ss].
  * Clave: ~/.config/openrouter/api.key (se lee del fichero, nunca se imprime).
  * ffmpeg/ffprobe: se buscan en PATH, en ~/.local/bin y en imageio_ffmpeg. Si salta
    "ffprobe: command not found" es que el PATH de esa shell no incluye ~/.local/bin (paso en
    19 sesiones): este script lo resuelve solo.

AVISO sobre alucinaciones: Gemini INVENTA texto en tramos de musica o silencio (frases
plausibles que nadie dijo, o el mismo renglon repetido). Por eso el script (1) mide los
silencios de cada tramo con ffmpeg y marca los que tienen mas de 40 % de silencio, (2) pide al
modelo que conteste exactamente [SIN VOZ] cuando no haya voz, y (3) marca con "!! REVISAR" los
tramos con bucles de repeticion o con [SIN VOZ] mezclado. La musica con letra o sin voz no se
detecta con certeza: un tramo marcado se escucha a mano antes de citarlo.
"""
import argparse
import base64
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

AUDIO = {".ogg", ".opus", ".oga", ".mp3", ".m4a", ".wav", ".flac", ".aac", ".wma", ".amr"}
VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".3gp"}
URL = "https://openrouter.ai/api/v1/chat/completions"
CLAVE = os.path.expanduser("~/.config/openrouter/api.key")

PROMPT = (
    "Transcribe este audio literalmente, en el idioma en que se habla{idioma}, sin resumir, "
    "sin traducir y sin anadir nada. Solo el texto hablado. Si en el audio no hay voz humana "
    "(silencio, ruido o musica), contesta exactamente [SIN VOZ] y nada mas: no inventes "
    "palabras ni completes letras de canciones."
)


def buscar_bin(nombre):
    ruta = shutil.which(nombre)
    if ruta:
        return ruta
    local = os.path.expanduser("~/.local/bin/" + nombre)
    if os.path.exists(local):
        return local
    if nombre == "ffmpeg":
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return None


FFMPEG = buscar_bin("ffmpeg")
FFPROBE = buscar_bin("ffprobe")


def duracion(ruta):
    """Segundos de un fichero de audio/video (ffprobe, o ffmpeg -i si no hay ffprobe)."""
    if FFPROBE:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", ruta], capture_output=True, text=True)
        try:
            return float(r.stdout.strip())
        except ValueError:
            pass
    if FFMPEG:
        r = subprocess.run([FFMPEG, "-i", ruta], capture_output=True, text=True)
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return None


def silencio_pct(ruta, dur):
    """Porcentaje del tramo por debajo de -35 dB durante mas de 1,5 s (ffmpeg silencedetect)."""
    if not FFMPEG or not dur:
        return None
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", ruta, "-af",
                        "silencedetect=noise=-35dB:d=1.5", "-f", "null", "-"],
                       capture_output=True, text=True)
    total = sum(float(x) for x in re.findall(r"silence_duration: ([\d.]+)", r.stderr))
    return min(100.0, 100.0 * total / dur)


def convertir(origen, destino):
    r = subprocess.run([FFMPEG, "-y", "-v", "error", "-i", origen, "-vn", "-ac", "1", "-ar", "24000",
                        "-b:a", "48k", destino], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg no pudo convertir: " + r.stderr[-200:])


def trocear(origen, carpeta, minutos):
    patron = os.path.join(carpeta, "tramo_%03d.mp3")
    r = subprocess.run([FFMPEG, "-y", "-v", "error", "-i", origen, "-vn", "-ac", "1", "-ar", "24000",
                        "-b:a", "48k", "-f", "segment", "-segment_time", str(int(minutos * 60)),
                        "-reset_timestamps", "1", patron], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg no pudo trocear: " + r.stderr[-200:])
    return sorted(glob.glob(os.path.join(carpeta, "tramo_*.mp3")))


def preparar(ruta, args, tmp):
    """Devuelve [(ruta_tramo, formato, inicio_s, fin_s)] y la duracion total."""
    ext = os.path.splitext(ruta)[1].lower()
    dur = duracion(ruta)
    mb = os.path.getsize(ruta) / 1e6
    entra = mb <= args.max_mb and (dur is None or dur <= args.tramo_min * 60)
    if ext in (".ogg", ".opus", ".oga") and entra:
        return [(ruta, "ogg", 0, dur)], dur
    if ext == ".mp3" and entra:
        return [(ruta, "mp3", 0, dur)], dur
    if ext == ".wav" and entra:
        return [(ruta, "wav", 0, dur)], dur
    if not FFMPEG:
        raise RuntimeError("hace falta ffmpeg para convertir/trocear " + os.path.basename(ruta))
    if entra:
        destino = os.path.join(tmp, "conv.mp3")
        convertir(ruta, destino)
        if os.path.getsize(destino) / 1e6 <= args.max_mb:
            return [(destino, "mp3", 0, dur)], dur
    trozos = trocear(ruta, tmp, args.tramo_min)
    plan, t = [], 0.0
    for z in trozos:
        d = duracion(z) or args.tramo_min * 60
        plan.append((z, "mp3", t, t + d))
        t += d
    return plan, dur


def llamar(clave, modelo, prompt, ruta, formato):
    datos = base64.b64encode(open(ruta, "rb").read()).decode()
    cuerpo = {"model": modelo, "temperature": 0,
              "messages": [{"role": "user", "content": [
                  {"type": "text", "text": prompt},
                  {"type": "input_audio", "input_audio": {"data": datos, "format": formato}}]}]}
    req = urllib.request.Request(URL, data=json.dumps(cuerpo).encode(), headers={
        "Authorization": "Bearer " + clave, "Content-Type": "application/json", "X-Title": "iamasters-os"})
    ultimo = ""
    for intento in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=300).read())
            return out["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            ultimo = "HTTP %s %s" % (e.code, e.read()[:200].decode("utf-8", "replace").replace(clave, "***"))
        except Exception as e:
            ultimo = "ERROR " + str(e)[:150].replace(clave, "***")
        time.sleep(3 * (intento + 1))
    return "!! FALLO " + ultimo


def sospechoso(texto, sil):
    """Motivos por los que un tramo huele a invencion del modelo."""
    motivos = []
    if sil is not None and sil > 40:
        motivos.append("%.0f %% de silencio" % sil)
    if "[SIN VOZ]" in texto:
        motivos.append("el modelo dice que no hay voz" if texto.strip() == "[SIN VOZ]" else "mezcla [SIN VOZ] con texto")
    frases = [f.strip().lower() for f in re.split(r"[.!?\n]+", texto) if len(f.strip()) > 3]
    if frases:
        mas = max(frases.count(f) for f in set(frases))
        if mas >= 4:
            motivos.append("el mismo renglon se repite %d veces" % mas)
    return motivos


def mmss(s):
    s = int(s or 0)
    return "%02d:%02d" % (s // 60, s % 60)


def recoger(entradas):
    ficheros = []
    for e in entradas:
        e = os.path.expanduser(e)
        if os.path.isdir(e):
            for f in sorted(os.listdir(e)):
                if os.path.splitext(f)[1].lower() in AUDIO | VIDEO:
                    ficheros.append(os.path.join(e, f))
        elif os.path.exists(e):
            ficheros.append(e)
        else:
            print("no existe: " + e, file=sys.stderr)
    return ficheros


def main():
    ap = argparse.ArgumentParser(description="Transcribe audio/video con Gemini via OpenRouter")
    ap.add_argument("entradas", nargs="+")
    ap.add_argument("--salida")
    ap.add_argument("--tramo-min", type=float, default=10)
    ap.add_argument("--max-mb", type=float, default=12)
    ap.add_argument("--idioma", default="")
    ap.add_argument("--modelo", default="google/gemini-2.5-pro")
    ap.add_argument("--solo-plan", action="store_true")
    args = ap.parse_args()

    clave = None
    if not args.solo_plan:
        clave = open(CLAVE).read().strip()
    prompt = PROMPT.format(idioma=(" (" + args.idioma + ")") if args.idioma else " (espanol, aleman o ingles)")
    if args.salida:
        os.makedirs(args.salida, exist_ok=True)

    print("AVISO: Gemini inventa contenido en tramos de musica o silencio; los tramos marcados con "
          "'!! REVISAR' se escuchan a mano antes de citarlos.\n")
    for ruta in recoger(args.entradas):
        nombre = os.path.basename(ruta)
        with tempfile.TemporaryDirectory(prefix="transcribir-") as tmp:
            try:
                plan, dur = preparar(ruta, args, tmp)
            except Exception as e:
                print("== %s\n!! %s\n" % (nombre, e))
                continue
            print("== %s (%s, %.1f MB, %d tramo%s)" % (nombre, mmss(dur) if dur else "duracion?",
                  os.path.getsize(ruta) / 1e6, len(plan), "" if len(plan) == 1 else "s"))
            bloques = []
            for i, (tramo, fmt, ini, fin) in enumerate(plan, 1):
                d = (fin - ini) if fin is not None else None
                sil = silencio_pct(tramo, d)
                if args.solo_plan:
                    print("   tramo %d/%d %s-%s %s silencio=%s" % (i, len(plan), mmss(ini), mmss(fin), fmt,
                          "?" if sil is None else "%.0f%%" % sil))
                    continue
                txt = llamar(clave, args.modelo, prompt, tramo, fmt)
                mot = sospechoso(txt, sil)
                marca = "[tramo %d/%d %s-%s]" % (i, len(plan), mmss(ini), mmss(fin)) if len(plan) > 1 else ""
                aviso = "  !! REVISAR: " + "; ".join(mot) if mot else ""
                bloques.append((marca + aviso + "\n" if (marca or aviso) else "") + txt)
            if args.solo_plan:
                print()
                continue
            texto = "\n\n".join(bloques)
            print(texto + "\n")
            if args.salida:
                base = os.path.splitext(nombre)[0]
                with open(os.path.join(args.salida, base + ".txt"), "w", encoding="utf-8") as fh:
                    fh.write(texto + "\n")


if __name__ == "__main__":
    main()
