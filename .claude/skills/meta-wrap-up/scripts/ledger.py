#!/usr/bin/env python3
"""Ledger de horas (docs/horas-ledger.csv): apuntar, sumar y comprobar sin escribir CSV a mano.

Sustituye al printf/echo '>>' con comillas a mano que se repitio en 129 sesiones (y a las
lineas perdidas por reescrituras, 14-10). Solo AÑADE al final: nunca reescribe lo anterior.

Uso (siempre con -I):
  ledger.py add --entidad kisult --cliente rhp --proyecto linus [--fecha 2026-10-15] \
            [--tipo sesion|reunion|maquina] --horas 1,5 "descripcion corta"
      Normaliza entidad a minusculas, acepta coma decimal, pone fecha de hoy si falta, salta la
      linea si ya existe la misma (fecha+cliente+proyecto+descripcion) y hace antes una copia
      del fichero en ~/.claude/backups/ledger/ (una por ejecucion).
  ledger.py suma [--entidad E] [--cliente C] [--proyecto P] [--desde F] [--hasta F] [--por cliente|proyecto|mes|entidad]
      Suma horas del ledger (la respuesta a "cuantas horas lleva X": sale de aqui, no de memoria).
  ledger.py check
      Detecta filas con columnas de mas o de menos, fechas o horas invalidas, entidades raras.
Opciones globales: --ledger RUTA (por defecto ~/iamasters-os/docs/horas-ledger.csv).
Horas = tiempo real de sesion Claude (regla del CLAUDE.md global), nunca horas de consultor.
"""
import argparse
import csv
import datetime
import io
import os
import shutil
import sys
from collections import defaultdict

LEDGER = os.path.expanduser("~/iamasters-os/docs/horas-ledger.csv")
CAB = ["fecha", "entidad", "cliente", "proyecto", "tipo", "horas", "descripcion"]
ENTIDADES = {"kisult", "operandi", "falkenlead", "interno", "personal", "rotary", "iamasters"}
TIPOS = {"sesion", "reunion", "maquina"}


def horas(txt):
    return float(str(txt).strip().replace(",", "."))


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def cmd_add(a):
    try:
        h = horas(a.horas)
    except ValueError:
        sys.exit("horas no numericas: %r" % a.horas)
    fecha = a.fecha or datetime.date.today().isoformat()
    datetime.date.fromisoformat(fecha)
    ent = a.entidad.strip().lower()
    if ent not in ENTIDADES and not a.nueva:
        sys.exit("entidad %r no conocida (%s). Usa --nueva si es a proposito." % (ent, ", ".join(sorted(ENTIDADES))))
    if a.tipo not in TIPOS:
        sys.exit("tipo debe ser sesion, reunion o maquina")
    desc = " ".join(a.descripcion).strip()
    if not desc:
        sys.exit("falta la descripcion")
    fila = [fecha, ent, a.cliente.strip().lower(), a.proyecto.strip().lower(), a.tipo, ("%g" % h), desc]
    filas = leer(a.ledger)
    clave = (fila[0], fila[2], fila[3], fila[6])
    for r in filas[1:]:
        if len(r) >= 7 and (r[0], r[2].lower(), r[3].lower(), r[6]) == clave:
            print("ya existe, no se duplica: %s %s %s" % (fecha, fila[2], fila[3]))
            return
    if not a.sin_copia:
        d = os.path.expanduser("~/.claude/backups/ledger")
        os.makedirs(d, exist_ok=True)
        shutil.copy2(a.ledger, os.path.join(d, "horas-ledger-%s.csv" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(fila)
    with open(a.ledger, "rb+") as f:
        f.seek(0, 2)
        if f.tell():
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(buf.getvalue().encode("utf-8"))
    print("apuntado: " + buf.getvalue().strip())


def cmd_suma(a):
    filas = leer(a.ledger)[1:]
    tot, n = defaultdict(float), 0
    for r in filas:
        if len(r) < 7:
            continue
        try:
            h = horas(r[5])
        except ValueError:
            continue
        if a.entidad and r[1].lower() != a.entidad.lower():
            continue
        if a.cliente and r[2].lower() != a.cliente.lower():
            continue
        if a.proyecto and r[3].lower() != a.proyecto.lower():
            continue
        if a.desde and r[0] < a.desde:
            continue
        if a.hasta and r[0] > a.hasta:
            continue
        k = {"cliente": r[2], "proyecto": "%s/%s" % (r[2], r[3]), "mes": r[0][:7], "entidad": r[1].lower()}.get(a.por, "total")
        tot[k.lower() if a.por != "mes" else k] += h
        n += 1
    for k, v in sorted(tot.items()):
        print("%-40s %8.2f h" % (k, v))
    if a.por:
        print("%-40s %8.2f h  (%d filas)" % ("TOTAL", sum(tot.values()), n))
    elif not tot:
        print("sin filas")


def cmd_check(a):
    filas = leer(a.ledger)
    malas = 0
    if filas[0] != CAB:
        print("cabecera distinta: %s" % filas[0])
    for i, r in enumerate(filas[1:], 2):
        p = []
        if len(r) != 7:
            p.append("%d columnas" % len(r))
        else:
            try:
                datetime.date.fromisoformat(r[0])
            except ValueError:
                p.append("fecha invalida")
            try:
                horas(r[5])
            except ValueError:
                p.append("horas invalidas")
            if r[1] not in ENTIDADES:
                p.append("entidad %r" % r[1])
            if r[4] not in TIPOS:
                p.append("tipo %r" % r[4])
        if p:
            malas += 1
            print("linea %d: %s" % (i, ", ".join(p)))
    print("%d filas, %d con problemas" % (len(filas) - 1, malas))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=LEDGER)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("--fecha")
    s.add_argument("--entidad", required=True)
    s.add_argument("--cliente", required=True)
    s.add_argument("--proyecto", required=True)
    s.add_argument("--tipo", default="sesion")
    s.add_argument("--horas", required=True)
    s.add_argument("--nueva", action="store_true")
    s.add_argument("--sin-copia", action="store_true")
    s.add_argument("descripcion", nargs="+")
    s.set_defaults(f=cmd_add)
    s = sub.add_parser("suma")
    for k in ("entidad", "cliente", "proyecto", "desde", "hasta"):
        s.add_argument("--" + k)
    s.add_argument("--por", choices=["cliente", "proyecto", "mes", "entidad"])
    s.set_defaults(f=cmd_suma)
    s = sub.add_parser("check")
    s.set_defaults(f=cmd_check)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
