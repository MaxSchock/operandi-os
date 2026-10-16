#!/usr/bin/env python3
"""Weekly correction rate: Max's turns since the last run, classified by Jev (OpenRouter).

Plan .claude/plans/2026-10-14-barreras-patrones-de-correccion.md, fase 4. Runs every Monday
inside scripts/mantenimiento-setup.sh. Turns are anonymized locally by extraer.py before
anything leaves the machine. Appends a section to docs/medicion-setup/<today>.md and keeps
the weekly numbers in docs/medicion-setup/correcciones-historial.json.

  medir-correcciones.py            week since the last run (default: last 7 days)
  medir-correcciones.py --semilla  rebuild the history from jev_todo.json (no API calls)
"""
import datetime as dt
import json
import os
import subprocess
import sys
from collections import defaultdict

REPO = os.path.expanduser("~/iamasters-os")
JC = os.path.join(REPO, "projects/investigacion-reels-2026-10-14/jev-correcciones")
DOCS = os.path.join(REPO, "docs/medicion-setup")
HIST = os.path.join(DOCS, "correcciones-historial.json")
UMBRAL = 0.5
OBJETIVO = 12  # % por quincena, dos seguidas (aceptacion del plan)
NOMBRES = {
    "unverified_claim": "Afirmar sin comprobar", "ignored_instruction": "No seguir instruccion o decision",
    "asks_instead_of_doing": "Pasar a Max lo que podia hacer yo", "forgot_context": "Olvidar lo ya dicho",
    "poor_output_quality": "Entregable malo o sin revisar", "ai_style_writing": "Forma de escribir",
    "scope_creep": "Inventar o añadir lo no pedido", "wrong_account_or_entity": "Cuenta o cliente equivocado",
    "risky_action": "Accion arriesgada", "patching_symptoms": "Parchear sintomas", "other_mistake": "Otro",
}


def resumen(filas):
    corr = [r for r in filas if "error" not in r and r["corr"] >= UMBRAL]
    pat = defaultdict(lambda: [0, set(), 0])
    for r in corr:
        p = pat[r["pattern"]]
        p[0] += 1
        p[1].add(r["sid"])
        p[2] += r["sev"] >= 1.5  # Jev score 0-2: top band = real damage
    return {"turnos": len(filas), "correcciones": len(corr), "sesiones": len({r["sid"] for r in filas}),
            "sesiones_con_correccion": len({r["sid"] for r in corr}),
            "errores": sum("error" in r for r in filas), "coste": round(sum(r.get("cost", 0) or 0 for r in filas), 4),
            "patrones": {k: {"turnos": v[0], "sesiones": len(v[1]), "graves": v[2]} for k, v in pat.items()}}


def lunes(d):
    return d - dt.timedelta(days=d.weekday())


def cargar_hist():
    try:
        return json.load(open(HIST))
    except Exception:
        return {"semanas": []}


def semilla():
    """History from the 14-10 run (turnos.json + jev_todo.json), complete weeks only."""
    t = json.load(open(os.path.join(JC, "turnos.json")))
    j = json.load(open(os.path.join(JC, "jev_todo.json")))
    ruido = ("Stop hook feedback", "Another Claude session sent")
    por_sem = defaultdict(list)
    hoy_lunes = lunes(dt.date.today())
    for r in j:
        o = t[r["i"]]
        if o["max"].startswith(ruido) or o["claude"].lstrip().startswith(("API Error", "You've hit")):
            continue
        d = dt.date.fromisoformat(r["ts"])
        if lunes(d) < hoy_lunes:
            por_sem[lunes(d).isoformat()].append(r)
    hist = {"semanas": [dict(desde=k, hasta=(dt.date.fromisoformat(k) + dt.timedelta(days=6)).isoformat(), **resumen(v))
                        for k, v in sorted(por_sem.items())],
            "marca": (hoy_lunes - dt.timedelta(days=1)).isoformat()}
    json.dump(hist, open(HIST, "w"), ensure_ascii=False, indent=1)
    print("semilla:", len(hist["semanas"]), "semanas hasta", hist["marca"])


def quincenas(hist):
    """Rate per pair of consecutive weeks, newest last."""
    s = hist["semanas"]
    out = []
    for a, b in zip(s[::2], s[1::2]) if len(s) % 2 == 0 else zip(s[1::2], s[2::2]):
        t = a["turnos"] + b["turnos"]
        c = a["correcciones"] + b["correcciones"]
        out.append((a["desde"], b["hasta"], c, t, round(100 * c / t) if t else 0))
    return out


def informe(sem, hist):
    tasa = round(100 * sem["correcciones"] / sem["turnos"]) if sem["turnos"] else 0
    L = [f"\n## Correcciones de Max ({sem['desde']} a {sem['hasta']}, Jev, umbral {UMBRAL})\n",
         f"- {sem['correcciones']} de {sem['turnos']} turnos de Max son correcciones: **{tasa} %**. "
         f"Sesiones con alguna: {sem['sesiones_con_correccion']} de {sem['sesiones']}. Coste {sem['coste']} $."]
    if sem["errores"]:
        L.append(f"- {sem['errores']} turnos sin clasificar por error de la API.")
    L.append("- Semanas anteriores: " + ", ".join(
        f"{w['desde'][5:]} {round(100 * w['correcciones'] / w['turnos']) if w['turnos'] else 0} %" for w in hist["semanas"][-7:-1]))
    q = quincenas(hist)
    if q:
        ult = q[-2:]
        ok = len(ult) == 2 and all(x[4] < OBJETIVO for x in ult)
        L.append("- Quincenas: " + ", ".join(f"{a[5:]}..{b[5:]} {p} %" for a, b, c, t, p in q[-4:])
                 + f". Objetivo del plan: menos del {OBJETIVO} % dos quincenas seguidas: {'CUMPLIDO' if ok else 'no cumplido'}.")
    L.append("\n| Patron | Turnos | Sesiones | Graves |\n|---|---|---|---|")
    for k, v in sorted(sem["patrones"].items(), key=lambda x: (-x[1]["sesiones"], -x[1]["turnos"])):
        L.append(f"| {NOMBRES.get(k, k)} | {v['turnos']} | {v['sesiones']} | {v['graves']} |")
    return "\n".join(L) + "\n"


def main():
    if "--semilla" in sys.argv:
        return semilla()
    hist = cargar_hist()
    hoy = dt.date.today()
    hasta = hoy - dt.timedelta(days=1)
    desde = (dt.date.fromisoformat(hist["marca"]) + dt.timedelta(days=1)) if hist.get("marca") else hoy - dt.timedelta(days=7)
    if desde > hasta:
        print("nada nuevo desde", hist.get("marca"))
        return
    tmp = os.path.expanduser("~/.claude/session-env")
    entrada, salida = os.path.join(tmp, "correcciones-turnos.json"), os.path.join(tmp, "correcciones-jev.json")
    subprocess.run([sys.executable, "extraer.py", desde.isoformat(), hasta.isoformat(), entrada], cwd=JC, check=True)
    subprocess.run([sys.executable, "clasificar.py", entrada, salida], cwd=JC, check=True)
    filas = json.load(open(salida))
    sem = dict(desde=desde.isoformat(), hasta=hasta.isoformat(), **resumen(filas))
    hist["semanas"].append(sem)
    hist["marca"] = hasta.isoformat()
    json.dump(hist, open(HIST, "w"), ensure_ascii=False, indent=1)
    texto = informe(sem, hist)
    with open(os.path.join(DOCS, f"{hoy.isoformat()}.md"), "a", encoding="utf-8") as fh:
        fh.write(texto)
    for f in (entrada, salida):
        os.remove(f)  # anonymized, but no reason to keep Max's turns around
    print(texto)


if __name__ == "__main__":
    main()
