# Accent judge for Linus's voice: one bench recording per turn (.webm from bench/kundenpruefung with
# KP_TON=1, or .ogg), converted to wav with ffmpeg, heard by Gemini 2.5 Pro through OpenRouter.
# Usage: python3 -I juzgar-acento-openrouter.py <carpeta>   (clave en ~/.config/openrouter/api.key, nunca se imprime)
# Prints one JSON line per file: akzent (keiner | leicht englisch | deutlich englisch), stellen, englische_woerter.
import base64, json, os, sys, glob, subprocess, tempfile, urllib.request, time
key = open(os.path.expanduser("~/.config/openrouter/api.key")).read().strip()
ffmpeg = os.path.expanduser("~/.local/bin/ffmpeg") if os.path.exists(os.path.expanduser("~/.local/bin/ffmpeg")) else "ffmpeg"
PROMPT = ("Du bist Phonetiker für Deutsch. Diese Aufnahme ist ein Gesprächszug eines Sprachassistenten, der Deutsch sprechen soll. "
          "Am Anfang kann kurz eine andere, synthetische Stimme (der Nutzer) zu hören sein: die bewertest du NICHT. Höre den Assistenten ganz an und antworte NUR mit JSON: "
          "{\"transkript\": wörtlich, \"akzent\": \"keiner\"|\"leicht englisch\"|\"deutlich englisch\", "
          "\"stellen\": [Wörter oder Satzteile mit englischem Akzent, mit ungefährer Sekunde], "
          "\"englische_woerter\": [Wörter, die auf Englisch statt Deutsch gesagt werden (keine Eigennamen), mit Sekunde], "
          "\"stimmwechsel\": true|false}. Sei streng und konkret, erfinde nichts: ist alles sauber, sag es.")
files = sorted(glob.glob(os.path.join(sys.argv[1], "*.webm")) + glob.glob(os.path.join(sys.argv[1], "*.ogg")),
               key=lambda f: (int(f.split("-zug-")[1].split(".")[0]) if "-zug-" in f else 0, f))
for f in files:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        wav = t.name
    r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "16000", wav], capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({"datei": os.path.basename(f), "fehler": "ffmpeg: " + r.stderr[:120]}, ensure_ascii=False)); continue
    data = base64.b64encode(open(wav, "rb").read()).decode(); os.unlink(wav)
    body = {"model": "google/gemini-2.5-pro", "temperature": 0.1,
            "messages": [{"role": "user", "content": [{"type": "text", "text": PROMPT},
                                                      {"type": "input_audio", "input_audio": {"data": data, "format": "wav"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "X-Title": "iamasters-os"})
    for intento in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=300).read())
            txt = out["choices"][0]["message"]["content"].strip()
            txt = txt[txt.find("{"): txt.rfind("}") + 1]
            res = json.loads(txt); res["datei"] = os.path.basename(f)
            print(json.dumps(res, ensure_ascii=False)); break
        except Exception as e:
            if intento == 2: print(json.dumps({"datei": os.path.basename(f), "fehler": str(e)[:150].replace(key, "***")}, ensure_ascii=False))
            time.sleep(3)
