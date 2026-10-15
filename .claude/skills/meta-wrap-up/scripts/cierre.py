#!/usr/bin/env python3
"""Piezas del cierre de sesion que hasta hoy se reescribian a mano en un cierre.py distinto cada vez.

Aparecio un cierre.py casero en 25 sesiones y el mismo AssertionError al editar MEMORY.md en 24
(el texto a sustituir ya no estaba tal cual). Aqui cada pieza hace copia previa, no borra nada
(lo retirado va a un archivo) y, si no encuentra el ancla, dice que lineas se parecen en vez de
romperse con un assert.

Uso (siempre con -I):
  cierre.py resumen-diario --bloque FICHERO.md [--fecha YYYY-MM-DD]
      Mete el bloque (que empieza por "## Titulo") en ~/.claude/skills/_daily-summaries/<fecha>.md
      justo antes de "## Para mañana". Si ya hay una seccion con el mismo titulo, la sustituye.
      Si el resumen del dia no existe, lo crea con las tres cabeceras habituales.
  cierre.py session-log --slug texto-corto --fichero FICHERO.md [--fecha F] [--hora HHMM]
      Copia el fichero a memory/session-logs/<fecha>-<hora>-<slug>.md. Nunca pisa uno existente.
      Avisa si el texto lleva rayas largas (em-dash), que Max no admite.
  cierre.py memory-linea --linea "- (emoji) [...](session-logs/..)" [--reemplaza "texto que identifica la linea vieja"]
      Pone la linea arriba del "## Inbox" de MEMORY.md. La reemplazada va a inbox-archive-<fecha>.md.
      Avisa si MEMORY.md pasa de 17 KB (tope de lectura del indice).
  cierre.py working-memory --seccion "Hilos activos" --linea "- **Tema** · ..." [--reemplaza "**Tema**"]
      Reemplaza la linea que contiene --reemplaza (o añade al final de la seccion) en
      context/working-memory.md. Avisa si pasa del tope de 2.500 caracteres.
Opciones globales: --mem DIR, --os DIR, --daily DIR (para probar sobre copias), --dry (no escribe).
Copias previas: ~/.claude/backups/cierre/<nombre>.<sello>
"""
import argparse
import datetime
import os
import re
import shutil
import sys

H = os.path.expanduser("~")
MEM = H + "/.claude/projects/-home-max-iamasters-os/memory"
OSD = H + "/iamasters-os"
DAILY = H + "/.claude/skills/_daily-summaries"
SELLO = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def copia(ruta):
    if os.path.exists(ruta):
        d = H + "/.claude/backups/cierre"
        os.makedirs(d, exist_ok=True)
        shutil.copy2(ruta, "%s/%s.%s" % (d, os.path.basename(ruta), SELLO))


def leer(ruta):
    return open(ruta, encoding="utf-8").read()


def escribir(a, ruta, txt):
    if a.dry:
        print("[dry] escribiria %d caracteres en %s" % (len(txt), ruta))
        return
    copia(ruta)
    open(ruta, "w", encoding="utf-8").write(txt)
    print("escrito: " + ruta)


def parecidas(texto, ancla, n=3):
    palabras = set(re.findall(r"\w{5,}", ancla.lower()))
    pts = sorted(((len(palabras & set(re.findall(r"\w{5,}", l.lower()))), l) for l in texto.splitlines()), reverse=True)
    return [l[:140] for p, l in pts[:n] if p > 0]


def cmd_resumen(a):
    fecha = a.fecha or datetime.date.today().isoformat()
    ruta = os.path.join(a.daily, fecha + ".md")
    bloque = leer(a.bloque).strip() + "\n\n"
    titulo = bloque.splitlines()[0]
    if not titulo.startswith("## "):
        sys.exit("el bloque debe empezar por '## Titulo'")
    s = leer(ruta) if os.path.exists(ruta) else "# Resumen %s\n\n## Hecho\n\n## Para mañana\n\n## Quick Resume\n" % fecha
    m = re.search(r"^" + re.escape(titulo) + r"\n.*?(?=^## |\Z)", s, re.M | re.S)
    if m:
        s = s[:m.start()] + bloque + s[m.end():]
    elif "## Para mañana" in s:
        i = s.index("## Para mañana")
        s = s[:i] + bloque + s[i:]
    else:
        s = s.rstrip() + "\n\n" + bloque
    escribir(a, ruta, s)


def cmd_session_log(a):
    fecha = a.fecha or datetime.date.today().isoformat()
    hora = a.hora or datetime.datetime.now().strftime("%H%M")
    slug = re.sub(r"[^a-z0-9]+", "-", a.slug.lower()).strip("-")
    destino = "%s/session-logs/%s-%s-%s.md" % (a.mem, fecha, hora, slug)
    if os.path.exists(destino):
        sys.exit("ya existe, no se pisa: " + destino)
    txt = leer(a.fichero)
    if "—" in txt:
        print("AVISO: el texto lleva rayas largas (em-dash); Max no las admite", file=sys.stderr)
    if a.dry:
        print("[dry] crearia " + destino)
        return
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, "w", encoding="utf-8").write(txt)
    print("creado: " + destino)


def cmd_memory(a):
    ruta = a.mem + "/MEMORY.md"
    s = leer(ruta)
    if "## Inbox" not in s:
        sys.exit("MEMORY.md no tiene '## Inbox'")
    lineas = s.split("\n")
    retirada = None
    if a.reemplaza:
        for i, l in enumerate(lineas):
            if a.reemplaza in l and l.startswith("- "):
                retirada = lineas.pop(i)
                break
        else:
            cand = parecidas(s, a.reemplaza)
            sys.exit("no hay ninguna linea con %r. Parecidas:\n  " % a.reemplaza + "\n  ".join(cand))
    i = next(k for k, l in enumerate(lineas) if l.startswith("## Inbox"))
    while i + 1 < len(lineas) and lineas[i + 1].strip() == "":
        i += 1
    lineas.insert(i + 1, a.linea.rstrip())
    nuevo = "\n".join(lineas)
    if retirada:
        arch = "%s/inbox-archive-%s.md" % (a.mem, datetime.date.today().strftime("%Y%m%d"))
        if not a.dry:
            os.makedirs(a.mem, exist_ok=True)
            with open(arch, "a", encoding="utf-8") as f:
                f.write(retirada + "\n")
        print("retirada a %s: %s" % (arch, retirada[:90]))
    escribir(a, ruta, nuevo)
    n = len(nuevo.encode("utf-8"))
    if n > 17000:
        print("AVISO: MEMORY.md pesa %d bytes (tope de lectura 17000): retira entradas cerradas" % n, file=sys.stderr)


def cmd_wm(a):
    ruta = a.os + "/context/working-memory.md"
    s = leer(ruta)
    m = re.search(r"^## " + re.escape(a.seccion) + r"\s*\n(.*?)(?=^## |\Z)", s, re.M | re.S)
    if not m:
        sys.exit("no hay seccion %r. Secciones: %s" % (a.seccion, ", ".join(re.findall(r"^## (.*)$", s, re.M))))
    cuerpo = m.group(1)
    lineas = cuerpo.rstrip("\n").split("\n")
    if a.reemplaza:
        hit = [i for i, l in enumerate(lineas) if a.reemplaza in l]
        if not hit:
            sys.exit("no hay linea con %r en %r. Parecidas:\n  %s" % (a.reemplaza, a.seccion, "\n  ".join(parecidas(cuerpo, a.reemplaza))))
        lineas[hit[0]] = a.linea.rstrip()
    else:
        lineas.append(a.linea.rstrip())
    nuevo = s[:m.start(1)] + "\n".join(lineas).rstrip("\n") + "\n\n" + s[m.end(1):]
    escribir(a, ruta, nuevo)
    if len(nuevo) > 2500:
        print("AVISO: working-memory pesa %d caracteres (tope ~2.500)" % len(nuevo), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mem", default=MEM)
    ap.add_argument("--os", default=OSD)
    ap.add_argument("--daily", default=DAILY)
    ap.add_argument("--dry", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("resumen-diario")
    s.add_argument("--bloque", required=True)
    s.add_argument("--fecha")
    s.set_defaults(f=cmd_resumen)
    s = sub.add_parser("session-log")
    s.add_argument("--slug", required=True)
    s.add_argument("--fichero", required=True)
    s.add_argument("--fecha")
    s.add_argument("--hora")
    s.set_defaults(f=cmd_session_log)
    s = sub.add_parser("memory-linea")
    s.add_argument("--linea", required=True)
    s.add_argument("--reemplaza")
    s.set_defaults(f=cmd_memory)
    s = sub.add_parser("working-memory")
    s.add_argument("--seccion", required=True)
    s.add_argument("--linea", required=True)
    s.add_argument("--reemplaza")
    s.set_defaults(f=cmd_wm)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
