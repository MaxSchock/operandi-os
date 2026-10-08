#!/usr/bin/env python3
"""Measure what the Claude Code setup actually does (read-only).

Sources: session transcripts of the project (hook output is recorded there as
attachments), the rules index and rule files of the activator, and the Sinapsis
instinct log / indexes. Nothing is modified; the report goes to
docs/medicion-setup/<date>.md.

Usage: python3 scripts/medir-setup.py [--dias 28]
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import statistics

HOME = os.path.expanduser("~")
PROY = os.path.join(HOME, ".claude/projects/-home-max-iamasters-os")
MEM = os.path.join(PROY, "memory")
SKILLS = os.path.join(HOME, ".claude/skills")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Full blocks ("### file [level]") and, since 2026-10-08, one-line repeats
# ("- file [level]: ...") that the activator prints for rules already shown in the session.
RE_REGLA = re.compile(r"^(?:### |- )([\w.-]+\.md) \[(\w+)\]", re.M)
RE_COMANDO = re.compile(r"<command-name>/?([\w:-]+)</command-name>")


def corto(cmd):
    """Short, stable label for a hook command."""
    cmd = (cmd or "").strip()
    m = re.search(r"([\w.-]+\.(?:py|sh))", cmd)
    if m:
        return m.group(1)
    return "rtk hook" if "rtk" in cmd else (cmd[-40:] or "(sin nombre)")


def pct(valores, p):
    if not valores:
        return 0
    v = sorted(valores)
    return v[min(len(v) - 1, int(len(v) * p))]


def frontmatter(ruta):
    meta = {}
    try:
        with open(ruta, encoding="utf-8") as fh:
            if fh.readline().strip() != "---":
                return meta
            for linea in fh:
                if linea.strip() == "---":
                    break
                m = re.match(r"\s*([\w-]+):\s*(.*)", linea)
                if m:
                    meta[m.group(1)] = m.group(2).strip().strip("\"'")
    except OSError:
        pass
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=28)
    args = ap.parse_args()
    ahora = dt.datetime.now(dt.timezone.utc)
    desde = ahora - dt.timedelta(days=args.dias)
    desde_iso = desde.strftime("%Y-%m-%dT%H:%M:%S")

    reglas = collections.Counter()          # rule file -> activations
    reglas_ses = collections.defaultdict(set)
    hooks = collections.defaultdict(lambda: {
        "salidas": 0, "car": 0, "ms": [], "timeouts": 0, "errores": 0, "bloqueos": 0})
    pasivas = collections.Counter()         # injected text -> times
    instintos_tx = collections.Counter()
    skills = collections.Counter()
    comandos = collections.Counter()
    herramientas = collections.Counter()
    bloqueos_txt = collections.Counter()
    sesiones, turnos = set(), 0
    car_msg_sistema = 0

    ficheros = [f for f in glob.glob(os.path.join(PROY, "*.jsonl"))
                if os.path.getmtime(f) >= desde.timestamp()]
    for f in ficheros:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                try:
                    d = json.loads(linea)
                except ValueError:
                    continue
                ts = d.get("timestamp") or ""
                if ts and ts < desde_iso:
                    continue
                sid = d.get("sessionId")
                tipo = d.get("type")
                if tipo == "assistant":
                    sesiones.add(sid)
                    for b in (d.get("message") or {}).get("content") or []:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            herramientas[b.get("name")] += 1
                            if b.get("name") == "Skill":
                                skills[(b.get("input") or {}).get("skill", "?")] += 1
                elif tipo == "user":
                    c = (d.get("message") or {}).get("content")
                    txt = c if isinstance(c, str) else " ".join(
                        x.get("text", "") for x in c or [] if isinstance(x, dict) and x.get("type") == "text")
                    if not d.get("isSidechain") and txt and "tool_result" not in str(c)[:40]:
                        turnos += 1
                    for m in RE_COMANDO.findall(txt or ""):
                        comandos[m] += 1
                elif tipo == "system" and d.get("subtype") == "stop_hook_summary":
                    for h in d.get("hookInfos") or []:
                        if h.get("durationMs") is not None:
                            hooks[corto(h.get("command"))]["ms"].append(h["durationMs"])
                elif tipo == "attachment":
                    a = d.get("attachment") or {}
                    t = a.get("type") or ""
                    if "hook" not in t:
                        continue
                    if t == "hook_system_message":
                        car_msg_sistema += len(a.get("content") or "")
                        continue
                    if t == "hook_blocking_error":
                        txt = ((a.get("blockingError") or {}).get("blockingError") or "")
                        m = re.search(r"GATE ([\w-]+)|^([\w-]+):", txt)
                        nombre = (m.group(1) or m.group(2)) if m else (a.get("hookName") or "?")
                        bloqueos_txt[nombre] += 1
                        hooks[nombre + ".py" if not nombre.endswith(".py") else nombre]["bloqueos"] += 1
                        continue
                    if not a.get("command"):
                        continue
                    k = corto(a.get("command"))
                    h = hooks[k]
                    if a.get("durationMs") is not None:
                        h["ms"].append(a["durationMs"])
                    if t == "hook_cancelled":
                        h["timeouts"] += 1
                        continue
                    if t == "hook_non_blocking_error":
                        h["errores"] += 1
                        continue
                    salida = (a.get("stdout") or "") + (a.get("content") or "")
                    h["salidas"] += 1
                    msg = ""
                    try:
                        msg = json.loads(a.get("stdout") or "{}").get("systemMessage") or ""
                    except (ValueError, AttributeError):
                        pass
                    h["car"] += len(msg or a.get("content") or "")
                    if k == "activador-reglas.py":
                        for nombre, _nivel in RE_REGLA.findall(salida):
                            reglas[nombre] += 1
                            reglas_ses[nombre].add(sid)
                    elif k == "_passive-activator.sh" and msg:
                        for trozo in msg.split("\n"):
                            if trozo.strip():
                                pasivas[trozo.strip()[:70]] += 1
                    elif k == "_instinct-activator.sh" and msg:
                        instintos_tx[msg.strip()[:70]] += 1

    # ---- rules index and rule files ------------------------------------
    indice = json.load(open(os.path.join(MEM, "_reglas-index.json"), encoding="utf-8"))
    meta_regla = {}
    for r in indice:
        fm = frontmatter(os.path.join(MEM, r["file"]))
        meta_regla[r["file"]] = {
            "nivel": r.get("nivel", "?"), "vigente": r.get("vigente", True),
            "fusionada": bool(r.get("fusionada_en") or fm.get("fusionada_en")),
            "reinc": int(re.sub(r"\D", "", fm.get("reincidencias", "0")) or 0),
            "creada": fm.get("creada", ""), "existe": bool(fm)}
    activas = {f: m for f, m in meta_regla.items() if m["vigente"] and not m["fusionada"]}
    nunca = sorted(f for f in activas if reglas[f] == 0)
    fuera_indice = sorted(set(reglas) - set(meta_regla))

    # ---- Sinapsis (read-only) ------------------------------------------
    inst_idx = json.load(open(os.path.join(SKILLS, "_instincts-index.json"), encoding="utf-8"))["instincts"]
    inst_log = collections.Counter()
    decaidos = collections.Counter()
    try:
        with open(os.path.join(SKILLS, "_instinct.log"), encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                p = [x.strip() for x in linea.split("|")]
                if len(p) < 3 or p[0] < desde_iso:
                    continue
                for i in p[2].split(","):
                    if i.strip():
                        inst_log[i.strip()] += 1
                if len(p) > 3 and p[3].startswith("DECAYED:"):
                    for i in p[3][8:].split(","):
                        decaidos[re.sub(r"\(.*", "", i.strip())] += 1
    except OSError:
        pass
    pas_idx = json.load(open(os.path.join(SKILLS, "_passive-rules.json"), encoding="utf-8"))["rules"]
    pas_cuenta = {}
    for r in pas_idx:
        clave = (r.get("inject") or "").strip()[:70]
        pas_cuenta[r["id"]] = sum(v for k, v in pasivas.items() if clave and (k.startswith(clave[:50]) or clave.startswith(k[:50])))
    try:
        props = json.load(open(os.path.join(SKILLS, "_instinct-proposals.json"), encoding="utf-8"))
        n_props = len(props.get("proposals", props) if isinstance(props, dict) else props)
    except (OSError, ValueError):
        n_props = "?"

    skills_os = sorted(os.path.basename(os.path.dirname(p))
                       for p in glob.glob(os.path.join(REPO, ".claude/skills/*/SKILL.md")))

    # ---- report ---------------------------------------------------------
    o = []
    w = o.append
    hoy = dt.date.today().isoformat()
    w(f"# Medición del setup · {hoy}\n")
    w(f"Ventana: últimos {args.dias} días (desde {desde.date()}). {len(ficheros)} transcripts, "
      f"{len(sesiones)} sesiones, {turnos} mensajes de usuario, {sum(herramientas.values())} llamadas a herramientas "
      f"({herramientas['Bash']} de terminal).\n")
    w("Límite de la fuente: un hook que termina bien y sin escribir nada no deja rastro en el transcript. "
      "Las cuentas de hooks son «veces que dijo algo», no «veces que corrió».\n")

    w("## Reglas del activador\n")
    niveles = collections.Counter(m["nivel"] for m in activas.values())
    w(f"- En el índice: {len(indice)}. Vigentes y sin fusionar: {len(activas)} "
      f"({', '.join(f'{n} {k}' for k, n in niveles.most_common())}).")
    w(f"- Activadas al menos una vez: {len(activas) - len(nunca)}. **Nunca activadas: {len(nunca)}** "
      f"({sum(1 for f in nunca if activas[f]['nivel'] == 'irrompible')} de ellas irrompibles).")
    w(f"- Activaciones totales: {sum(reglas.values())} en {hooks['activador-reglas.py']['salidas']} mensajes "
      f"({sum(reglas.values()) / max(1, hooks['activador-reglas.py']['salidas']):.1f} reglas por mensaje con reglas).")
    if fuera_indice:
        w(f"- Activadas pero ya fuera del índice: {len(fuera_indice)}.")
    w("\n**Las 25 que más saltan**\n\n| Regla | Nivel | Veces | Sesiones | Reincidencias |\n|---|---|---|---|---|")
    for f, n in reglas.most_common(25):
        m = meta_regla.get(f, {})
        w(f"| {f[:-3]} | {m.get('nivel', '-')} | {n} | {len(reglas_ses[f])} | {m.get('reinc', 0)} |")
    w("\n**Reglas con 3 o más reincidencias** (se incumplen aunque se activen)\n\n"
      "| Regla | Nivel | Reincidencias | Veces activada |\n|---|---|---|---|")
    for f, m in sorted(meta_regla.items(), key=lambda x: -x[1]["reinc"]):
        if m["reinc"] >= 3:
            w(f"| {f[:-3]} | {m['nivel']} | {m['reinc']} | {reglas[f]} |")
    w("\n**Nunca activadas en la ventana**\n")
    por_nivel = collections.defaultdict(list)
    for f in nunca:
        por_nivel[activas[f]["nivel"]].append(f[:-3])
    for nivel, fs in sorted(por_nivel.items()):
        w(f"- {nivel} ({len(fs)}): {', '.join(fs)}")

    w("\n## Instincts de Sinapsis\n")
    ids = [i["id"] for i in inst_idx]
    w(f"- En el índice: {len(ids)}. Con activación en la ventana: {sum(1 for i in ids if inst_log[i])}. "
      f"Sin ninguna: {sum(1 for i in ids if not inst_log[i])}. Propuestas sin revisar: {n_props}.")
    total_inst = sum(inst_log.values())
    w(f"- Activaciones: {total_inst}. Las 3 primeras concentran "
      f"{100 * sum(n for _, n in inst_log.most_common(3)) / max(1, total_inst):.0f} %.")
    w("\n| Instinct | Nivel | Veces | Marcado «caducado» |\n|---|---|---|---|")
    nivel_i = {i["id"]: i.get("level", "?") for i in inst_idx}
    for i, n in inst_log.most_common(15):
        w(f"| {i} | {nivel_i.get(i, 'fuera del índice')} | {n} | {decaidos[i]} |")
    w(f"\n- Sin activación: {', '.join(i for i in ids if not inst_log[i]) or 'ninguno'}")
    if decaidos:
        w(f"- El registro marca «DECAYED» {sum(decaidos.values())} veces sobre {len(decaidos)} instincts "
          f"(los más repetidos: {', '.join(f'{k} {v}' for k, v in decaidos.most_common(3))}): "
          "la misma rebaja se anota una y otra vez, señal de que no se guarda.")

    w("\n## Passive rules\n")
    w(f"- En el fichero: {len(pas_idx)}. Con activación: {sum(1 for v in pas_cuenta.values() if v)}. "
      f"Sin ninguna: {sum(1 for v in pas_cuenta.values() if not v)}.")
    w("\n| Regla | Veces |\n|---|---|")
    for k, v in sorted(pas_cuenta.items(), key=lambda x: -x[1]):
        if v:
            w(f"| {k} | {v} |")
    w(f"\n- Sin activación: {', '.join(k for k, v in pas_cuenta.items() if not v) or 'ninguna'}")

    w("\n## Hooks\n")
    w("| Hook | Veces que dijo algo | Texto metido en contexto (KB) | Mediana ms | p95 ms | Cortado por tiempo | Errores | Bloqueos |\n"
      "|---|---|---|---|---|---|---|---|")
    for k, h in sorted(hooks.items(), key=lambda x: -x[1]["car"] - x[1]["salidas"]):
        med = int(statistics.median(h["ms"])) if h["ms"] else 0
        w(f"| {k} | {h['salidas']} | {h['car'] / 1024:.0f} | {med} | {pct(h['ms'], 0.95)} | "
          f"{h['timeouts']} | {h['errores']} | {h['bloqueos']} |")
    w(f"\n- Mensajes de sistema de hooks sin autor identificable en el transcript: {car_msg_sistema / 1024:.0f} KB.")
    if bloqueos_txt:
        w(f"- Bloqueos por guard: {', '.join(f'{k} {v}' for k, v in bloqueos_txt.most_common())}.")

    w("\n## Skills y comandos\n")
    w(f"- Skills del OS instaladas: {len(skills_os)}. Invocadas con la herramienta Skill: "
      f"{', '.join(f'{k} {v}' for k, v in skills.most_common()) or 'ninguna'}.")
    w(f"- Comandos de barra: {', '.join(f'{k} {v}' for k, v in comandos.most_common()) or 'ninguno'}.")
    usadas = set(skills) | set(comandos)
    w(f"- Skills del OS sin un solo uso: {', '.join(s for s in skills_os if s not in usadas and 'meta-' + s not in usadas)}.")

    # Machine-readable sidecar for podar-reglas.py and the maintenance routine.
    datos = {"fecha": hoy, "dias": args.dias, "desde": desde.date().isoformat(),
             "sesiones": len(sesiones), "reglas": dict(reglas),
             "instintos": dict(inst_log), "pasivas": pas_cuenta,
             "skills": dict(skills), "comandos": dict(comandos),
             "kb_hooks": {k: round(h["car"] / 1024) for k, h in hooks.items() if h["car"]},
             "timeouts": {k: h["timeouts"] for k, h in hooks.items() if h["timeouts"]}}
    lateral = os.path.join(HOME, ".claude/session-env")
    os.makedirs(lateral, exist_ok=True)
    with open(os.path.join(lateral, f"medicion-setup-{args.dias}d.json"), "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False)

    destino = os.path.join(REPO, "docs/medicion-setup")
    os.makedirs(destino, exist_ok=True)
    ruta = os.path.join(destino, f"{hoy}.md" if args.dias == 28 else f"{hoy}-{args.dias}d.md")
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(o) + "\n")
    print(ruta)


if __name__ == "__main__":
    main()
