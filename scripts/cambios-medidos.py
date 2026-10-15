#!/usr/bin/env python3
"""Registro de cambios al sistema y su medicion posterior (15-10-2026).

Todo cambio hecho para mejorar el rendimiento (arnes de Claude Code, reglas, hooks, skills,
prompts de Linus o de agentes de clientes, workflows de n8n, servicios del VPS) se registra en
docs/cambios-medidos.jsonl con una metrica y fechas de revision. Los lunes
(scripts/mantenimiento-setup.sh) `check` mide lo vencido y lo compara con la base.

  cambios-medidos.py add --sistema arnes-os --que "..." --ficheros "..." --metrica m1,m2 \
                         --entidad iamasters --como-revertir "..." [--base m=valor ...] [--revisiones 7,14]
  cambios-medidos.py list [--todo]
  cambios-medidos.py check [--hoy AAAA-MM-DD] [--seco]
  cambios-medidos.py close <id> <estado> <nota>
  cambios-medidos.py medir <metrica>         mide una metrica del catalogo y la imprime
  cambios-medidos.py tabla                   tabla markdown de abiertos (la usa el informe del lunes)

Metricas del catalogo: ver CATALOGO. `manual:<descripcion>` queda sin medir (se cierra a mano).
Cada funcion del catalogo devuelve (valor, unidad, motivo, detalle); valor None = no se pudo medir.
"""
import argparse
import datetime as dt
import glob
import importlib.util
import json
import os
import re
import statistics
import subprocess
import sys
import time

REPO = os.path.expanduser("~/iamasters-os")
REGISTRO = os.path.join(REPO, "docs/cambios-medidos.jsonl")
DOCS = os.path.join(REPO, "docs/medicion-setup")
PROYECTOS = os.path.expanduser("~/.claude/projects/-home-max-iamasters-os")
VENV_PY = os.path.expanduser("~/.claude/venv-tiktoken/bin/python")
BANCO_OS = os.path.join(REPO, "projects/arnes-medicion-2026-10-15/banco/resultados")
BANCO_LINUS = os.path.join(REPO, "clients/kisult/clients/rhp/banco-objetivos-2026-10-14")
ESTADOS = ("abierto", "mejora", "sin_cambio", "empeora", "revertido", "sin_medir")
UMBRAL_REL = 0.05  # cambios de menos del 5 % respecto a la base se dan por ruido


# ---------------------------------------------------------------- catalogo

def _tokens(textos):
    """Tokens cl100k de una lista de textos. Venv efimero con tiktoken; si falta, chars/4 (marcado)."""
    if os.path.exists(VENV_PY):
        try:
            r = subprocess.run(
                [VENV_PY, "-c",
                 "import sys,json,tiktoken;e=tiktoken.get_encoding('cl100k_base');"
                 "print(json.dumps([len(e.encode(t,disallowed_special=())) for t in json.load(sys.stdin)]))"],
                input=json.dumps(textos), capture_output=True, text=True, timeout=300)
            if r.returncode == 0:
                return json.loads(r.stdout), "cl100k"
        except Exception:
            pass
    return [len(t) // 4 for t in textos], "chars/4 (sin tiktoken)"


def _sesiones_recientes(dias=7, hasta=None):
    ahora = hasta or time.time()
    out = []
    for f in glob.glob(os.path.join(PROYECTOS, "*.jsonl")):
        m = os.path.getmtime(f)
        if ahora - 86400 * dias <= m <= ahora + 86400:
            out.append(f)
    return sorted(out, key=os.path.getmtime)


def _lineas(f):
    with open(f, encoding="utf-8", errors="replace") as fh:
        for l in fh:
            if '"type":"api-request' in l[:60] or '"type": "api-request' in l[:60]:
                continue  # blobs enormes, no llevan nada que medir
            try:
                yield json.loads(l)
            except Exception:
                continue


def m_tasa_correccion_semanal():
    """Ultima semana completa del historial que escribe scripts/medir-correcciones.py (lunes, Jev)."""
    ruta = os.path.join(REPO, "scripts/medir-correcciones.py")
    spec = importlib.util.spec_from_file_location("medir_correcciones", ruta)
    mc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mc)
    sem = [s for s in mc.cargar_hist().get("semanas", []) if s.get("turnos")]
    if not sem:
        return None, "%", "historial de correcciones vacio", ""
    s = sem[-1]
    tasa = 100.0 * s["correcciones"] / s["turnos"]
    return round(tasa, 1), "%", "", f"semana {s['desde']}..{s['hasta']}: {s['correcciones']} de {s['turnos']} turnos"


def m_tokens_fijos_arranque():
    """Tokens inyectados antes del primer prompt de Max (metodo del paso 1, paso1-medicion.md).

    Por sesion de los ultimos 7 dias que arranco de cero (el hook salud-os dejo >1000 car. en
    SessionStart): suma de lo que Claude Code registro como adjuntos al arrancar (primeras 400 filas)
    (CLAUDE.md x2 y MEMORY.md, hook de arranque, lista de skills, definiciones de herramientas,
    prompt de sistema, herramientas diferidas, MCP, agentes, session_context). Media de sesiones.
    """
    sesiones = []
    for f in _sesiones_recientes(7):
        comp = {}
        for n, o in enumerate(_lineas(f)):
            if n > 400:
                break  # los adjuntos de arranque caen en las primeras filas, aunque algunos tras la primera respuesta
            a = o.get("attachment") or {}
            t = a.get("type")
            if t == "prompt_snapshot":
                comp.setdefault("sistema", json.dumps(a.get("systemPrompt", ""), ensure_ascii=False))
                if a.get("tools"):
                    comp.setdefault("herramientas", json.dumps(a["tools"], ensure_ascii=False))
                continue
            if t == "instructions":
                comp.setdefault("instrucciones", "\n".join(x.get("content", "") for x in a.get("files", [])))
            elif t == "hook_success" and a.get("hookEvent") == "SessionStart" and "salud-os" in a.get("command", ""):
                comp["hook_arranque"] = a.get("content", "")
            elif t == "skill_listing":
                comp["skills"] = a.get("content", "")
            elif t == "deferred_tools_delta":
                comp["diferidas"] = "\n".join(a.get("addedLines", []))
            elif t == "mcp_instructions_delta":
                comp["mcp"] = "\n".join(a.get("addedBlocks", []))
            elif t == "agent_listing_delta":
                comp["agentes"] = "\n".join(a.get("addedLines", []))
            elif t == "session_context":
                comp["contexto"] = json.dumps(a.get("context", ""), ensure_ascii=False)
        if len(comp.get("hook_arranque", "")) > 1000 and "instrucciones" in comp:
            sesiones.append(comp)
    if not sesiones:
        return None, "tokens", "ninguna sesion de los ultimos 7 dias arranco de cero con los adjuntos registrados", ""
    textos = [t for c in sesiones for t in c.values()]
    cuentas, tok = _tokens(textos)
    i, totales = 0, []
    for c in sesiones:
        totales.append(sum(cuentas[i:i + len(c)]))
        i += len(c)
    return round(statistics.mean(totales)), "tokens", "", \
        f"{len(sesiones)} sesiones de cero, rango {min(totales)}-{max(totales)}, tokenizador {tok}"


def _prompts_con_inyeccion(dias=7):
    """Por cada inyeccion del activador: (n_reglas, texto del prompt que la disparo)."""
    out = []
    for f in _sesiones_recientes(dias):
        filas, mapa = [], {}
        for o in _lineas(f):
            if "uuid" not in o:
                continue
            a = o.get("attachment") or {}
            txt = None
            if o.get("type") == "user":
                c = (o.get("message") or {}).get("content")
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list) and not any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                    txt = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            elif a.get("type") == "queued_command":
                txt = a.get("prompt")
            mapa[o["uuid"]] = (o.get("parentUuid"), txt)
            if a.get("hookEvent") == "UserPromptSubmit" and "<reglas-que-aplican-a-esto>" in a.get("content", ""):
                filas.append((o.get("parentUuid"), a["content"]))
        for p, contenido in filas:
            txt = None
            for _ in range(10):
                if p not in mapa:
                    break
                par, t = mapa[p]
                if t:
                    txt = t
                    break
                p = par
            n = len(re.findall(r"^### ", contenido, re.M)) + len(re.findall(r"^- \S+\.md", contenido, re.M))
            out.append((n, txt or ""))
    return out


def _es_entre_sesiones(txt):
    return "<cross-session-message" in txt or "Another Claude session sent" in txt


def m_reglas_por_prompt():
    inj = _prompts_con_inyeccion(7)
    if not inj:
        return None, "reglas/inyeccion", "ninguna inyeccion del activador en 7 dias", ""
    media = statistics.mean(n for n, _ in inj)
    cross = sum(_es_entre_sesiones(t) for _, t in inj)
    noMax = sum(t.lstrip().startswith("<") or _es_entre_sesiones(t) for _, t in inj)
    return round(media, 2), "reglas/inyeccion", "", \
        (f"{len(inj)} inyecciones; {100 * cross / len(inj):.0f} % sobre mensajes entre sesiones, "
         f"{100 * noMax / len(inj):.0f} % sobre cualquier mensaje que no es de Max")


def m_pct_inyecciones_entre_sesiones():
    inj = _prompts_con_inyeccion(7)
    if not inj:
        return None, "%", "ninguna inyeccion del activador en 7 dias", ""
    return round(100 * sum(_es_entre_sesiones(t) for _, t in inj) / len(inj), 1), "%", "", f"{len(inj)} inyecciones"


def m_banco_os():
    """Ultima puntuacion del banco del OS. Formato esperado: banco/resultados/<corrida>/resumen.json
    con al menos {"puntuacion_media": <numero>} (el paso 2 lo esta construyendo)."""
    cands = sorted(glob.glob(os.path.join(BANCO_OS, "*", "resumen.json")), key=os.path.getmtime)
    if not cands:
        return None, "puntos", "banco sin resultados (falta banco/resultados/<corrida>/resumen.json con puntuacion_media)", ""
    d = json.load(open(cands[-1], encoding="utf-8"))
    v = d.get("puntuacion_media")
    if v is None:
        return None, "puntos", f"{cands[-1]} no trae puntuacion_media", ""
    return v, d.get("unidad", "puntos"), "", f"corrida {os.path.basename(os.path.dirname(cands[-1]))}"


def m_errores_n8n_7d(workflow=None):
    """public.n8n_errors_inbox por workflow_name en 7 dias. Solo con clave local de Supabase."""
    url = os.environ.get("SUPABASE_URL", "https://xepotlbqlwmriwievyvc.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        return None, "errores", ("sin clave de Supabase en local (SUPABASE_SERVICE_KEY solo vive en el .env de los "
                                 "servicios del VPS; el MCP de claude.ai no es invocable desde un script)"), ""
    if not workflow:
        return None, "errores", "falta el workflow: errores_n8n_7d:<workflow_name>", ""
    import urllib.parse
    import urllib.request
    desde = (dt.datetime.utcnow() - dt.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = urllib.parse.urlencode({"select": "id", "workflow_name": f"eq.{workflow}", "occurred_at": f"gte.{desde}"})
    req = urllib.request.Request(f"{url}/rest/v1/n8n_errors_inbox?{q}", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        filas = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        return None, "errores", f"consulta fallida: {type(e).__name__}", ""
    return len(filas), "errores", "", f"workflow {workflow}, 7 dias"


def m_banco_linus():
    """Ultima pasada del banco por objetivos de Linus guardada en local (informes de rhp/banco-objetivos-*).
    Cuenta formas que pasan sobre el total de la pasada mas reciente por campo `datum`. No ejecuta el banco."""
    cands = glob.glob(os.path.join(BANCO_LINUS, "*.json"))
    mejor = None
    for f in cands:
        try:
            d = json.load(open(f, encoding="utf-8"))
            if not isinstance(d, dict) or "ergebnisse" not in d:
                continue
        except Exception:
            continue
        if len(d["ergebnisse"]) < 100:
            continue  # pasadas parciales no son comparables
        if mejor is None or d.get("datum", "") > mejor[1].get("datum", ""):
            mejor = (f, d)
    if not mejor:
        return None, "formas ok", f"sin pasadas completas del banco de Linus en {BANCO_LINUS}", ""
    f, d = mejor
    ok = sum(1 for r in d["ergebnisse"] if r.get("ok"))
    return ok, "formas ok", "", f"{ok}/{len(d['ergebnisse'])} en {d.get('commit')} ({d.get('datum', '')[:16]})"


# nombre -> (funcion, mejor: "bajar" | "subir")
CATALOGO = {
    "tasa_correccion_semanal": (m_tasa_correccion_semanal, "bajar"),
    "tokens_fijos_arranque": (m_tokens_fijos_arranque, "bajar"),
    "reglas_por_prompt": (m_reglas_por_prompt, "bajar"),
    "pct_inyecciones_entre_sesiones": (m_pct_inyecciones_entre_sesiones, "bajar"),
    "banco_os": (m_banco_os, "subir"),
    "errores_n8n_7d": (m_errores_n8n_7d, "bajar"),
    "banco_linus": (m_banco_linus, "subir"),
}


def medir(nombre):
    """(valor, unidad, motivo, detalle, mejor). Valor None si no se puede medir."""
    base, _, arg = nombre.partition(":")
    if base == "manual" or base not in CATALOGO:
        return None, "", ("metrica manual, se mide a mano" if base == "manual" else f"metrica {base!r} fuera del catalogo"), "", "bajar"
    fn, mejor = CATALOGO[base]
    try:
        v, u, motivo, det = fn(arg) if base == "errores_n8n_7d" else fn()
    except Exception as e:
        return None, "", f"error al medir: {type(e).__name__}: {e}", "", mejor
    return v, u, motivo, det, mejor


# ---------------------------------------------------------------- registro

def leer():
    out = []
    if os.path.exists(REGISTRO):
        for l in open(REGISTRO, encoding="utf-8"):
            l = l.strip()
            if l:
                out.append(json.loads(l))
    return out


def guardar(entradas):
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    tmp = REGISTRO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for e in entradas:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    os.replace(tmp, REGISTRO)


def hoy_de(args=None):
    h = getattr(args, "hoy", None)
    return dt.date.fromisoformat(h) if h else dt.date.today()


def metricas_de(e):
    return [m.strip() for m in e["metrica"].split(",") if m.strip()]


def veredicto(base, actual, mejor):
    if base is None or actual is None:
        return None
    if base == 0:
        return "sin_cambio" if actual == 0 else ("empeora" if mejor == "bajar" else "mejora")
    rel = (actual - base) / abs(base)
    if abs(rel) < UMBRAL_REL:
        return "sin_cambio"
    bueno = rel < 0 if mejor == "bajar" else rel > 0
    return "mejora" if bueno else "empeora"


def cmd_add(a):
    entradas = leer()
    hoy = hoy_de(a)
    n = 1 + sum(1 for e in entradas if e["id"].startswith(hoy.isoformat()))
    ident = a.id or f"{hoy.isoformat()}-{n:02d}"
    if any(e["id"] == ident for e in entradas):
        sys.exit(f"ya existe {ident}")
    dias = [int(x) for x in a.revisiones.split(",")]
    base = {}
    for par in a.base or []:
        k, _, v = par.partition("=")
        base[k] = None if v in ("", "null", "pendiente") else float(v)
    notas = [a.notas] if a.notas else []
    for m in [x.strip() for x in a.metrica.split(",") if x.strip()]:
        if m in base:
            continue
        if m.startswith("manual:"):
            base[m] = None
            continue
        v, u, motivo, det, _ = medir(m)
        base[m] = v
        notas.append(f"base {m}: {v} {u} ({det})" if v is not None else f"base {m} sin medir: {motivo}")
    e = dict(id=ident, fecha=hoy.isoformat(), entidad=a.entidad, sistema=a.sistema, que_cambio=a.que,
             ficheros_o_servicios=a.ficheros, metrica=a.metrica, valor_base=base, como_medir=a.como_medir or "cambios-medidos.py check",
             revisiones=[(hoy + dt.timedelta(days=d)).isoformat() for d in dias], como_revertir=a.como_revertir,
             estado="abierto", notas=" | ".join(notas), mediciones=[])
    entradas.append(e)
    guardar(entradas)
    print(f"registrado {ident}; revisiones {e['revisiones']}; base {base}")


def vencidas(e, hoy):
    hechas = {m["revision"] for m in e.get("mediciones", [])}
    return [r for r in e["revisiones"] if r <= hoy.isoformat() and r not in hechas]


def cmd_list(a):
    hoy = hoy_de(a)
    for e in leer():
        if e["estado"] != "abierto" and not a.todo:
            continue
        v = vencidas(e, hoy) if e["estado"] == "abierto" else []
        marca = "VENCIDO " if v else ""
        print(f"{e['id']} [{e['estado']}] {marca}{e['sistema']}: {e['que_cambio']} | metrica {e['metrica']} | revisiones {e['revisiones']}")


def cmd_check(a):
    hoy = hoy_de(a)
    entradas = leer()
    lineas, cambios = [], 0
    for e in entradas:
        if e["estado"] != "abierto":
            continue
        for rev in vencidas(e, hoy):
            ultima = rev == e["revisiones"][-1]
            res = {}
            for m in metricas_de(e):
                v, u, motivo, det, mejor = medir(m)
                base = e["valor_base"].get(m)
                tardia = False
                if base is None and v is not None and not m.startswith("manual:"):
                    e["valor_base"][m] = base = v   # la base no se pudo medir al registrar: la primera medicion la fija
                    tardia = True
                ver = None if tardia else veredicto(base, v, mejor)
                res[m] = dict(valor=v, unidad=u, base=base, veredicto=ver, detalle=det, motivo=motivo, base_tardia=tardia)
            e.setdefault("mediciones", []).append(dict(revision=rev, medido_el=hoy.isoformat(), resultados=res))
            cambios += 1
            vers = [r["veredicto"] for r in res.values() if r["veredicto"]]
            if ultima:
                if not vers:
                    e["estado"] = "sin_medir"
                elif "empeora" in vers:
                    e["estado"] = "empeora"
                elif "mejora" in vers:
                    e["estado"] = "mejora"
                else:
                    e["estado"] = "sin_cambio"
            lineas.append((e, rev, res, ultima))
    if cambios and not a.seco:
        guardar(entradas)
    texto = informe(lineas, hoy)
    if lineas and not a.seco:
        os.makedirs(DOCS, exist_ok=True)
        with open(os.path.join(DOCS, f"cambios-{hoy.isoformat()}.md"), "a", encoding="utf-8") as fh:
            fh.write(texto)
    print(texto if lineas else "ninguna revision vencida")
    return 0


def informe(lineas, hoy):
    if not lineas:
        return ""
    L = [f"# Cambios medidos, revision del {hoy.isoformat()}\n"]
    for e, rev, res, ultima in lineas:
        L.append(f"## {e['id']} ({e['sistema']}), revision {rev}{' (ultima)' if ultima else ''}\n")
        L.append(f"{e['que_cambio']}. Estado tras esta medicion: **{e['estado']}**. Revertir: {e['como_revertir']}\n")
        L.append("| Metrica | Base | Actual | Veredicto | Detalle |\n|---|---|---|---|---|")
        for m, r in res.items():
            act = f"{r['valor']} {r['unidad']}".strip() if r["valor"] is not None else f"sin medir: {r['motivo']}"
            ver = "base fijada ahora" if r["base_tardia"] else (r["veredicto"] or "-")
            L.append(f"| {m} | {r['base'] if r['base'] is not None else '-'} | {act} | {ver} | {r['detalle']} |")
        L.append("")
    return "\n".join(L) + "\n"


def cmd_close(a):
    if a.estado not in ESTADOS:
        sys.exit(f"estado debe ser uno de {ESTADOS}")
    entradas = leer()
    for e in entradas:
        if e["id"] == a.id:
            e["estado"] = a.estado
            e["notas"] = (e.get("notas", "") + f" | cierre {dt.date.today().isoformat()}: {a.nota}").strip(" |")
            guardar(entradas)
            print(f"{a.id} -> {a.estado}")
            return
    sys.exit(f"no existe {a.id}")


def cmd_medir(a):
    v, u, motivo, det, _ = medir(a.metrica)
    print(f"{a.metrica}: {v} {u}" + (f" ({det})" if det else "") + (f" SIN MEDIR: {motivo}" if v is None else ""))


def cmd_tabla(a):
    """Tabla markdown de cambios abiertos: base, actual (medido ahora) y estado. Para el informe del lunes."""
    hoy = hoy_de(a)
    abiertos = [e for e in leer() if e["estado"] == "abierto"]
    print("\n## Cambios medidos abiertos\n")
    if not abiertos:
        print("Ninguno abierto.")
        return
    print("| Id | Cambio | Metrica | Base | Actual | Revision | Estado |\n|---|---|---|---|---|---|---|")
    for e in abiertos:
        prox = next((r for r in e["revisiones"] if r not in {m["revision"] for m in e.get("mediciones", [])}), "-")
        for m in metricas_de(e):
            v, u, motivo, _, _ = medir(m)
            base = e["valor_base"].get(m)
            act = f"{v} {u}".strip() if v is not None else f"sin medir ({motivo[:40]})"
            venc = " VENCIDA" if prox != "-" and prox <= hoy.isoformat() else ""
            print(f"| {e['id']} | {e['que_cambio'][:60]} | {m} | {base if base is not None else '-'} | {act} | {prox}{venc} | {e['estado']} |")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("add")
    a.add_argument("--id")
    a.add_argument("--entidad", default="iamasters")
    a.add_argument("--sistema", required=True, help="arnes-os | linus | n8n:<cliente> | operandi-services | otro")
    a.add_argument("--que", required=True)
    a.add_argument("--ficheros", required=True)
    a.add_argument("--metrica", required=True, help="catalogo o manual:<descripcion>; varias separadas por coma")
    a.add_argument("--base", action="append", help="metrica=valor (o metrica=pendiente); si falta, se mide ahora")
    a.add_argument("--como-medir")
    a.add_argument("--revisiones", default="7,14", help="dias desde hoy, por defecto 7,14")
    a.add_argument("--como-revertir", required=True)
    a.add_argument("--notas", default="")
    a.add_argument("--hoy")
    a.set_defaults(f=cmd_add)
    l = sp.add_parser("list")
    l.add_argument("--todo", action="store_true")
    l.add_argument("--hoy")
    l.set_defaults(f=cmd_list)
    c = sp.add_parser("check")
    c.add_argument("--hoy")
    c.add_argument("--seco", action="store_true", help="no escribe registro ni informe")
    c.set_defaults(f=cmd_check)
    x = sp.add_parser("close")
    x.add_argument("id")
    x.add_argument("estado")
    x.add_argument("nota")
    x.set_defaults(f=cmd_close)
    m = sp.add_parser("medir")
    m.add_argument("metrica")
    m.set_defaults(f=cmd_medir)
    t = sp.add_parser("tabla")
    t.add_argument("--hoy")
    t.set_defaults(f=cmd_tabla)
    args = p.parse_args()
    sys.exit(args.f(args) or 0)


if __name__ == "__main__":
    main()
