#!/usr/bin/env python3
"""Cross-review runner: sends a repo's code, chunk by chunk, to a cheap OpenRouter model
together with the 15-point checklist, and stores the suspected findings as JSONL.

Usage: see README.md next to this file. Run with --seco first (no network to the model).

Design notes:
- Unknown or abbreviated arguments abort with exit code 2 and touch nothing.
- A chunk is marked done in estado.json only AFTER its findings are written; on --reanudar,
  findings of chunks not marked done are dropped and the chunk is reviewed again.
- The spend cap is checked BEFORE each call with a worst-case estimate (input + max output),
  so the run stops before crossing it, not after.
- The API key is read from OPENROUTER_API_KEY or ~/.config/openrouter/api.key and is never
  printed; any error text is scrubbed of it.
"""
import argparse
import ast
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

OS_ROOT = os.path.expanduser("~/iamasters-os")
DEFAULT_LISTA = os.path.join(OS_ROOT, "docs/revision-cruzada/patrones-de-error-2026-10-14.md")
DEFAULT_SALIDA = os.path.join(OS_ROOT, "docs/revision-cruzada")
DEFAULT_MODELO = "deepseek/deepseek-v3.2"
KEY_FILE = os.path.expanduser("~/.config/openrouter/api.key")
API = "https://openrouter.ai/api/v1"

SPLIT_BYTES = 60 * 1024          # files above this are split by top-level unit
CHARS_PER_TOKEN = 3.5            # conservative estimate for code (no tokenizer available)
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage", "__pycache__",
             ".venv", "venv", ".turbo", ".cache", "out"}
OVERLAP_LINES = 15               # context lines shown (not reviewed) before a split chunk
TS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
TS_TOP = re.compile(r"^(export\s+(default\s+)?)?(declare\s+)?(async\s+)?"
                    r"(function\*?|class|const|let|var|interface|type|enum|abstract\s+class)\b"
                    r"|^export\s*[{*]")
TS_IMPORT = re.compile(r"""(?:import|export)\s[^;]*?from\s+["'](\.{1,2}/[^"']+)["']"""
                       r"""|import\s*\(\s*["'](\.{1,2}/[^"']+)["']\s*\)"""
                       r"""|require\(\s*["'](\.{1,2}/[^"']+)["']\s*\)""")
CAMPOS = ["punto", "fichero", "linea", "linea_prueba", "resumen", "escenario_de_fallo", "confianza"]
MAX_POR_TROZO = 3


class Abort(Exception):
    """Fatal condition: the run stops, state already saved."""


# ---------------------------------------------------------------- arguments

def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="pasar.py", allow_abbrev=False,
        description="Pase de revisión cruzada con un modelo de OpenRouter.")
    p.add_argument("repo", help="carpeta a revisar")
    p.add_argument("--ext", required=True, help="extensiones separadas por comas, p. ej. .ts,.tsx")
    p.add_argument("--nombre", help="nombre del repo para la carpeta de salida (por defecto, la raíz git)")
    p.add_argument("--modelo", default=DEFAULT_MODELO)
    p.add_argument("--tope", type=float, required=True, help="tope de gasto en dólares")
    p.add_argument("--seco", action="store_true", help="trocea y estima sin llamar al modelo")
    p.add_argument("--reanudar", action="store_true", help="continúa el pase de --fecha (o el último sin terminar)")
    p.add_argument("--fecha", help="AAAA-MM-DD de la carpeta de salida (por defecto hoy)")
    p.add_argument("--tarifa-entrada", type=float, help="$/M tokens de entrada si OpenRouter no da precio")
    p.add_argument("--tarifa-salida", type=float, help="$/M tokens de salida si OpenRouter no da precio")
    p.add_argument("--presupuesto", type=int, default=24000, help="tokens máximos de código por trozo (con imports)")
    p.add_argument("--max-salida", type=int, default=4000, help="max_tokens de la respuesta")
    p.add_argument("--excluir", action="append", default=[], help="patrón glob de ruta relativa a excluir (repetible)")
    p.add_argument("--lista", default=DEFAULT_LISTA, help="documento con el apartado D")
    p.add_argument("--salida", default=DEFAULT_SALIDA, help="carpeta base de resultados")
    a = p.parse_args(argv)   # unknown args -> SystemExit(2), nothing touched
    exts = [e.strip() for e in a.ext.split(",") if e.strip()]
    if not exts or any(not re.fullmatch(r"\.[A-Za-z0-9]+", e) for e in exts):
        p.error("--ext: lista de extensiones con punto, p. ej. .ts,.py")
    a.ext = sorted(set(exts))
    if a.tope <= 0:
        p.error("--tope debe ser mayor que 0")
    if a.fecha and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.fecha):
        p.error("--fecha con formato AAAA-MM-DD")
    if (a.tarifa_entrada is None) != (a.tarifa_salida is None):
        p.error("--tarifa-entrada y --tarifa-salida van juntas")
    if a.seco and a.reanudar:
        p.error("--seco y --reanudar no se combinan")
    a.repo = os.path.abspath(os.path.expanduser(a.repo))
    if not os.path.isdir(a.repo):
        p.error(f"no existe la carpeta {a.repo}")
    return a


# ---------------------------------------------------------------- checklist

def leer_lista(path):
    """Return section D of the patterns document (the 15 points), verbatim."""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"^## D\..*?$(.*?)(?=^## |\Z)", txt, re.S | re.M)
    if not m:
        raise Abort(f"no encuentro el apartado «## D.» en {path}")
    cuerpo = m.group(1).strip()
    puntos = re.findall(r"^(\d+)\. ", cuerpo, re.M)
    if [int(x) for x in puntos] != list(range(1, 16)):
        raise Abort(f"el apartado D de {path} no tiene los puntos 1 a 15 seguidos")
    return cuerpo


# ---------------------------------------------------------------- files and chunks

def recoger_ficheros(root, exts, excluir):
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for fn in sorted(files):
            if os.path.splitext(fn)[1] not in exts:
                continue
            rel = os.path.relpath(os.path.join(d, fn), root)
            if any(fnmatch.fnmatch(rel, pat) for pat in excluir):
                continue
            out.append(rel)
    return out


def tokens_de(texto):
    return int(len(texto) / CHARS_PER_TOKEN) + 1


def _cortes_python(texto):
    """Start lines (1-based) of top-level statements, decorators included."""
    try:
        tree = ast.parse(texto)
    except SyntaxError:
        return None
    starts = []
    for node in tree.body:
        ln = node.lineno
        for dec in getattr(node, "decorator_list", []) or []:
            ln = min(ln, dec.lineno)
        starts.append(ln)
    return starts


def _cortes_ts(lineas):
    return [i + 1 for i, l in enumerate(lineas) if TS_TOP.match(l)]


def _cabecera(lineas, texto, ext):
    """Number of leading lines that hold the imports (shown as context with every split chunk)."""
    if ext == ".py":
        try:
            tree = ast.parse(texto)
        except SyntaxError:
            return 0
        fin = 0
        for node in tree.body:
            es_doc = isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant)
            if isinstance(node, (ast.Import, ast.ImportFrom)) or (es_doc and fin == 0):
                fin = node.end_lineno
            else:
                break
        return fin
    fin, dentro = 0, False
    for i, l in enumerate(lineas):
        s = l.strip()
        if dentro:
            fin = i + 1
            if re.search(r"""from\s+["'][^"']+["']|;\s*$""", s):
                dentro = False
            continue
        if s.startswith("import ") or s.startswith("import{") or (s.startswith("export ") and " from " in s):
            fin = i + 1
            dentro = not re.search(r"""(from\s+)?["'][^"']+["']\s*;?\s*$""", s)
            continue
        if not s or s.startswith(("//", "/*", "*", "*/", "'use ", '"use ')):
            continue
        break
    return fin


def trocear_fichero(rel, texto, max_bytes):
    """Split one file into chunks. Returns list of dicts with desde/hasta (1-based, inclusive)
    and the context lines (import header and overlap) that travel with each chunk."""
    lineas = texto.splitlines()
    n = len(lineas)
    if len(texto.encode("utf-8")) <= SPLIT_BYTES or n == 0:
        return [{"fichero": rel, "desde": 1, "hasta": max(n, 1), "contexto": ""}]
    ext = os.path.splitext(rel)[1]
    cortes = _cortes_python(texto) if ext == ".py" else None
    if cortes is None:
        cortes = _cortes_ts(lineas)
    cortes = sorted({c for c in cortes if 1 <= c <= n} | {1})
    # units: [start, end] between consecutive cut points
    unidades = [(c, (cortes[i + 1] - 1) if i + 1 < len(cortes) else n) for i, c in enumerate(cortes)]

    def tam(a, b):
        return sum(len(lineas[k].encode("utf-8")) + 1 for k in range(a - 1, b))

    # split oversized units by lines
    finas = []
    for a, b in unidades:
        if tam(a, b) <= max_bytes:
            finas.append((a, b))
            continue
        s = a
        acc = 0
        for k in range(a, b + 1):
            acc += len(lineas[k - 1].encode("utf-8")) + 1
            if acc > max_bytes and k > s:
                finas.append((s, k - 1))
                s, acc = k, len(lineas[k - 1].encode("utf-8")) + 1
        finas.append((s, b))
    # greedy grouping up to max_bytes
    grupos = []
    for a, b in finas:
        if grupos and tam(grupos[-1][0], b) <= max_bytes:
            grupos[-1] = (grupos[-1][0], b)
        else:
            grupos.append((a, b))
    cab = _cabecera(lineas, texto, ext)
    trozos = []
    for a, b in grupos:
        ctx = []
        if cab and a > cab:
            ctx.append(_numerar(lineas, 1, cab))
        o = max(cab + 1, a - OVERLAP_LINES)
        if o < a:
            ctx.append(_numerar(lineas, o, a - 1))
        trozos.append({"fichero": rel, "desde": a, "hasta": b, "contexto": "\n...\n".join(ctx)})
    return trozos


def _numerar(lineas, a, b):
    return "\n".join(f"{k:>5}| {lineas[k - 1]}" for k in range(a, b + 1))


def imports_locales(root, rel, texto):
    """Relative paths (within root) of same-package files imported by this file."""
    ext = os.path.splitext(rel)[1]
    base = os.path.dirname(os.path.join(root, rel))
    found = []
    if ext == ".py":
        try:
            tree = ast.parse(texto)
        except SyntaxError:
            return []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                d = base
                for _ in range(node.level - 1):
                    d = os.path.dirname(d)
                mods = [node.module] if node.module else []
                # "from .pkg import name": name may itself be a submodule
                mods += [((node.module + ".") if node.module else "") + a.name for a in node.names]
                for m in mods:
                    p = os.path.join(d, *m.split("."))
                    for cand in (p + ".py", os.path.join(p, "__init__.py")):
                        found.append(cand)
    elif ext in TS_EXTS:
        for m in TS_IMPORT.finditer(texto):
            spec = next(g for g in m.groups() if g)
            p = os.path.normpath(os.path.join(base, spec))
            stem = re.sub(r"\.(js|mjs|cjs|jsx)$", "", p)
            cands = [p] + [stem + e for e in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts")] + \
                    [os.path.join(p, "index" + e) for e in (".ts", ".tsx", ".js")]
            found.extend(cands)
    out = []
    root_abs = os.path.abspath(root)
    for c in found:
        c = os.path.abspath(c)
        if os.path.isfile(c) and c.startswith(root_abs + os.sep):
            r = os.path.relpath(c, root_abs)
            if r != rel and r not in out:
                out.append(r)
    return out


def construir_trozos(root, ficheros, presupuesto_tokens):
    """Chunks for all files, each with the same-package imports that fit the token budget."""
    max_bytes = int(presupuesto_tokens * CHARS_PER_TOKEN * 0.6)   # leave room for imports/context
    max_bytes = min(max_bytes, SPLIT_BYTES)
    textos = {}

    def leer(r):
        if r not in textos:
            with open(os.path.join(root, r), encoding="utf-8", errors="replace") as f:
                textos[r] = f.read()
        return textos[r]

    trozos = []
    for rel in ficheros:
        texto = leer(rel)
        partes = trocear_fichero(rel, texto, max_bytes)
        lineas = texto.splitlines()
        # a pure barrel (only imports/re-exports) gains nothing from the imported files' bodies
        barril = _cabecera(lineas, texto, os.path.splitext(rel)[1]) >= len(lineas)
        imps = [] if barril else imports_locales(root, rel, texto)
        for i, t in enumerate(partes):
            codigo = _numerar(lineas, t["desde"], t["hasta"]) if lineas else ""
            usado = tokens_de(codigo) + tokens_de(t["contexto"])
            adj, fuera = [], []
            for imp in imps:
                it = leer(imp)
                if usado + tokens_de(it) <= presupuesto_tokens:
                    adj.append(imp)
                    usado += tokens_de(it)
                else:
                    fuera.append(imp)
            h = hashlib.sha1(codigo.encode("utf-8")).hexdigest()[:10]
            t.update({"id": f"{rel}:{t['desde']}-{t['hasta']}:{h}", "parte": i + 1,
                      "partes": len(partes), "codigo": codigo, "imports": adj,
                      "imports_fuera": fuera})
            trozos.append(t)
    return trozos, textos


# ---------------------------------------------------------------- prompt and validation

SISTEMA = """Eres un revisor de código. Buscas SOLO los 15 tipos de fallo de esta lista, ordenada por daño:

{lista}

Reglas de respuesta:
- Devuelve EXCLUSIVAMENTE un array JSON, sin texto antes ni después y sin bloques de código.
- Cada elemento: {{"punto": <entero 1-15>, "fichero": "<ruta tal cual aparece>", "linea": <entero, número de línea del fichero revisado>, "linea_prueba": "<la línea del CÓDIGO A REVISAR que produce el fallo, copiada tal cual, sin el número>", "resumen": "<una frase>", "escenario_de_fallo": "<qué entrada o situación real lo hace fallar y qué se pierde>", "confianza": <número entre 0 y 1>}}
- Solo hallazgos del CÓDIGO A REVISAR. El contexto e imports sirven para entenderlo; no los revises.
- Si no hay nada, devuelve [].
- No inventes: si no puedes describir un escenario de fallo concreto, no lo incluyas.
- Antes de incluir un hallazgo, recorre el CÓDIGO A REVISAR completo y comprueba que ninguna otra regla, rama o patrón del mismo trozo ya cubre ese caso. Si lo cubre, no lo incluyas.
- Si un comentario del código explica ese comportamiento como decisión tomada o medida, no es un hallazgo, salvo que el escenario rompa lo que el propio comentario promete.
- Quedan fuera: rendimiento, memoria, textos o avisos al usuario, «podría fallar si hubiera un error interno» y los casos que fallan hacia el lado seguro (bloquear, tapar o rechazar de más).
- "escenario_de_fallo" da la entrada literal (el texto, valor o llamada concretos) y el recorrido por líneas que lleva al fallo. Si no puedes escribir la entrada literal, no lo incluyas.
- "linea_prueba" es una línea que existe en el CÓDIGO A REVISAR; un hallazgo cuya línea no aparezca ahí se descarta sin leerlo.
- Como mucho 3 hallazgos, los de más daño. Lo normal en código revisado es devolver []."""


def mensaje_usuario(t, textos):
    partes = []
    if t["imports"]:
        for imp in t["imports"]:
            partes.append(f"=== IMPORT DEL MISMO PAQUETE (solo contexto): {imp} ===\n{textos[imp]}")
    if t["contexto"]:
        partes.append(f"=== CONTEXTO DE {t['fichero']} (no revisar) ===\n{t['contexto']}")
    partes.append(f"=== CÓDIGO A REVISAR: {t['fichero']} líneas {t['desde']}-{t['hasta']} "
                  f"(parte {t['parte']} de {t['partes']}) ===\n{t['codigo']}")
    return "\n\n".join(partes)


def validar_salida(texto):
    """Return the parsed list or raise ValueError with the reason. Only a whole-response
    ``` fence is tolerated; anything else around the JSON is rejected."""
    s = texto.strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", s, re.S)
    if m:
        s = m.group(1)
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"no es JSON válido: {e}")
    if not isinstance(data, list):
        raise ValueError("no es un array")
    for i, h in enumerate(data):
        if not isinstance(h, dict):
            raise ValueError(f"elemento {i} no es un objeto")
        falta = [c for c in CAMPOS if c not in h]
        if falta:
            raise ValueError(f"elemento {i} sin {falta}")
        if not isinstance(h["punto"], int) or not 1 <= h["punto"] <= 15:
            raise ValueError(f"elemento {i}: punto fuera de 1-15")
        if not isinstance(h["linea"], int) or isinstance(h["linea"], bool):
            raise ValueError(f"elemento {i}: linea no es entero")
        if not isinstance(h["confianza"], (int, float)) or not 0 <= h["confianza"] <= 1:
            raise ValueError(f"elemento {i}: confianza fuera de 0-1")
        for c in ("fichero", "linea_prueba", "resumen", "escenario_de_fallo"):
            if not isinstance(h[c], str):
                raise ValueError(f"elemento {i}: {c} no es texto")
    return data


def _normal(texto):
    return re.sub(r"\s+", " ", texto).strip()


def filtrar_por_prueba(hallazgos, codigo):
    """Split findings into (kept, discarded). A finding is kept only if its linea_prueba appears
    in the reviewed code (numbering and whitespace ignored); of those, the MAX_POR_TROZO with the
    highest confidence survive. Each discarded finding carries a 'descartado' reason."""
    lineas = [_normal(re.sub(r"^\s*\d+\| ?", "", l)) for l in codigo.splitlines()]
    todo = " ".join(lineas)
    validos, fuera = [], []
    for h in hallazgos:
        prueba = _normal(re.sub(r"^\s*\d+\| ?", "", h["linea_prueba"]))
        if len(prueba) < 6 or prueba not in todo:
            fuera.append({**h, "descartado": "linea_prueba no está en el trozo"})
        else:
            validos.append(h)
    validos.sort(key=lambda h: -h["confianza"])
    fuera += [{**h, "descartado": f"más de {MAX_POR_TROZO} en el trozo"} for h in validos[MAX_POR_TROZO:]]
    return validos[:MAX_POR_TROZO], fuera


# ---------------------------------------------------------------- OpenRouter

def leer_clave():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if k:
        return k
    try:
        with open(KEY_FILE, encoding="utf-8") as f:
            k = f.read().strip()
    except OSError:
        return None
    return k or None


def precios_openrouter(modelo, timeout=30):
    """($/token in, $/token out) from the public /models endpoint, or None."""
    try:
        with urllib.request.urlopen(f"{API}/models", timeout=timeout) as r:
            data = json.load(r)["data"]
    except Exception:
        return None
    for m in data:
        if m.get("id") == modelo:
            pr = m.get("pricing") or {}
            try:
                return float(pr["prompt"]), float(pr["completion"])
            except (KeyError, TypeError, ValueError):
                return None
    return None


class ClienteOpenRouter:
    """Callable(model, messages, max_tokens) -> (text, usage). usage may contain 'cost'."""

    def __init__(self, clave, timeout=180):
        self.clave = clave
        self.timeout = timeout

    def _limpio(self, s):
        return str(s).replace(self.clave, "***")

    def __call__(self, modelo, mensajes, max_tokens):
        body = {"model": modelo, "messages": mensajes, "max_tokens": max_tokens, "temperature": 0,
                "usage": {"include": True},
                # Only providers that do not store or train on prompts; fails instead of falling back.
                "provider": {"data_collection": "deny", "allow_fallbacks": True}}
        req = urllib.request.Request(
            f"{API}/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + self.clave, "Content-Type": "application/json",
                     "X-Title": "iamasters-os revision-cruzada"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            cuerpo = e.read()[:300].decode("utf-8", "replace")
            if e.code in (401, 402, 403):
                raise Abort(self._limpio(f"OpenRouter {e.code}: {cuerpo}"))
            raise RuntimeError(self._limpio(f"OpenRouter {e.code}: {cuerpo}"))
        except Exception as e:
            raise RuntimeError(self._limpio(f"red: {e}"))
        if "error" in d:
            raise RuntimeError(self._limpio(f"OpenRouter: {d['error']}"))
        texto = d["choices"][0]["message"].get("content") or ""
        return texto, d.get("usage") or {}


# ---------------------------------------------------------------- run

def nombre_repo(root):
    try:
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        top = ""
    return os.path.basename(top or root)


def commit_de(root):
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        sucio = subprocess.run(["git", "-C", root, "status", "--porcelain", "--", "."],
                               capture_output=True, text=True, timeout=30).stdout.strip()
        return (r.stdout.strip() or None), bool(sucio)
    except Exception:
        return None, None


def _leer_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _guardar_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def escribir_coste(path, estado):
    lineas = [f"modelo: {estado['modelo']}", f"tope: {estado['tope']:.2f} $",
              f"tarifa: {estado['fuente_tarifa']}", ""]
    por = {}
    for c in estado["costes"].values():
        f = por.setdefault(c["fichero"], {"in": 0, "out": 0, "usd": 0.0, "estimado": False})
        f["in"] += c["in"]
        f["out"] += c["out"]
        f["usd"] += c["usd"]
        f["estimado"] |= c["estimado"]
    lineas.append(f"{'fichero':60} {'tok_in':>9} {'tok_out':>8} {'dólares':>10}")
    for fic in sorted(por):
        f = por[fic]
        lineas.append(f"{fic:60} {f['in']:>9} {f['out']:>8} {f['usd']:>10.4f}{'  (estimado)' if f['estimado'] else ''}")
    tin = sum(f["in"] for f in por.values())
    tout = sum(f["out"] for f in por.values())
    est = any(f["estimado"] for f in por.values())
    lineas += ["", f"{'TOTAL':60} {tin:>9} {tout:>8} {estado['gastado']:>10.4f}{'  (estimado)' if est else ''}",
               f"trozos hechos: {len(estado['hechos'])} de {estado['total']}",
               f"fallos guardados: {estado['fallos']}"]
    if estado.get("parado"):
        lineas.append(f"PARADO: {estado['parado']}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas) + "\n")


def seco(args, trozos, textos, sistema, precios, fuente, carpeta, log):
    tin = 0
    por = {}
    for t in trozos:
        n = tokens_de(sistema) + tokens_de(mensaje_usuario(t, textos))
        tin += n
        por.setdefault(t["fichero"], [0, 0])
        por[t["fichero"]][0] += 1
        por[t["fichero"]][1] += n
    out_tipico = 800   # assumption for a typical answer, worst case is --max-salida
    lineas = [f"modo seco (no se ha llamado al modelo) · {args.repo}",
              f"modelo: {args.modelo}", f"tarifa: {fuente}",
              f"ficheros: {len(por)} · trozos: {len(trozos)} · tokens de entrada estimados: {tin}",
              f"(estimación por caracteres: {CHARS_PER_TOKEN} car./token)", ""]
    for fic in sorted(por):
        lineas.append(f"  {fic}: {por[fic][0]} trozo(s), ~{por[fic][1]} tokens")
    if precios:
        pin, pout = precios
        tip = tin * pin + len(trozos) * out_tipico * pout
        peor = tin * pin + len(trozos) * args.max_salida * pout
        lineas += ["", f"coste estimado: {tip:.4f} $ (salida típica {out_tipico} tok/trozo), "
                       f"techo {peor:.4f} $ (salida {args.max_salida} tok/trozo)",
                   f"tope pedido: {args.tope:.2f} $ -> {'cabe' if peor <= args.tope else 'el techo pasa del tope; parará al llegar'}"]
    else:
        lineas += ["", "coste: sin tarifa (OpenRouter no respondió y no se pasó --tarifa-entrada/--tarifa-salida)"]
    os.makedirs(carpeta, exist_ok=True)
    with open(os.path.join(carpeta, "seco.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    log("\n".join(lineas))
    return 0


def ejecutar(argv, cliente=None, precios_fn=precios_openrouter, clave_fn=leer_clave, log=print, dormir=time.sleep):
    args = parse_args(argv)
    try:
        sistema = SISTEMA.format(lista=leer_lista(args.lista))
    except (OSError, Abort) as e:
        log(f"ERROR: {e}")
        return 3
    nombre = args.nombre or nombre_repo(args.repo)
    if not re.fullmatch(r"[A-Za-z0-9._-]+", nombre):
        log(f"ERROR: nombre de repo no válido para carpeta: {nombre}")
        return 2
    base = os.path.join(args.salida, nombre)
    fecha = args.fecha or dt.date.today().isoformat()
    if args.reanudar and not args.fecha:
        cands = sorted(d for d in (os.listdir(base) if os.path.isdir(base) else [])
                       if os.path.isfile(os.path.join(base, d, "estado.json")))
        abiertos = [d for d in cands if not _leer_json(os.path.join(base, d, "estado.json"))["completo"]]
        if not abiertos:
            log(f"ERROR: no hay pase sin terminar en {base}")
            return 3
        fecha = abiertos[-1]
    carpeta = os.path.join(base, fecha)

    ficheros = recoger_ficheros(args.repo, args.ext, args.excluir)
    if not ficheros:
        log(f"ERROR: ningún fichero {','.join(args.ext)} en {args.repo}")
        return 3
    trozos, textos = construir_trozos(args.repo, ficheros, args.presupuesto)

    precios = precios_fn(args.modelo)
    if precios:
        fuente = f"OpenRouter /models ({precios[0] * 1e6:.3f} $/M entrada, {precios[1] * 1e6:.3f} $/M salida); el coste real sale de usage.cost"
    elif args.tarifa_entrada is not None:
        precios = (args.tarifa_entrada / 1e6, args.tarifa_salida / 1e6)
        fuente = f"ESTIMADA por argumento ({args.tarifa_entrada} $/M entrada, {args.tarifa_salida} $/M salida)"
    else:
        fuente = None

    if args.seco:
        return seco(args, trozos, textos, sistema, precios, fuente or "ninguna", carpeta, log)

    if not precios:
        log("ERROR: sin precio del modelo no puedo vigilar el tope. Pasa --tarifa-entrada y --tarifa-salida.")
        return 3
    clave = clave_fn()
    if not clave:
        log(f"ERROR: no hay clave de OpenRouter (OPENROUTER_API_KEY ni {KEY_FILE}). No se llama a nada.")
        return 3
    if cliente is None:
        cliente = ClienteOpenRouter(clave)

    estado_path = os.path.join(carpeta, "estado.json")
    hall_path = os.path.join(carpeta, "hallazgos.jsonl")
    fallos_path = os.path.join(carpeta, "fallos.jsonl")
    descartes_path = os.path.join(carpeta, "descartados.jsonl")
    coste_path = os.path.join(carpeta, "coste.txt")
    commit, sucio = commit_de(args.repo)
    if args.reanudar:
        if not os.path.isfile(estado_path):
            log(f"ERROR: no hay estado.json en {carpeta}")
            return 3
        with open(estado_path, encoding="utf-8") as f:
            estado = json.load(f)
        for k in ("repo", "modelo", "ext"):
            if estado[k] != getattr(args, k):
                log(f"ERROR: --{k} no coincide con el pase guardado ({estado[k]})")
                return 2
        if estado["completo"]:
            log("Ese pase ya está completo.")
            return 0
        estado["tope"] = args.tope
        estado["parado"] = None
        hechos = set(estado["hechos"])
        # drop findings/failures of chunks that never got marked done (crash between write and mark)
        for p in (hall_path, fallos_path, descartes_path):
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as f:
                    keep = [l for l in f if l.strip() and json.loads(l)["trozo"]["id"] in hechos]
                with open(p, "w", encoding="utf-8") as f:
                    f.writelines(keep)
        if commit and estado.get("commit") and commit != estado["commit"]:
            log(f"AVISO: el repo ha cambiado de commit ({estado['commit'][:8]} -> {commit[:8]}); los trozos cambiados se revisan de nuevo")
    else:
        if os.path.exists(estado_path):
            log(f"ERROR: ya hay un pase en {carpeta}. Usa --reanudar o --fecha distinta.")
            return 3
        os.makedirs(carpeta, exist_ok=True)
        estado = {"repo": args.repo, "nombre": nombre, "fecha": fecha, "modelo": args.modelo, "ext": args.ext,
                  "commit": commit, "cambios_sin_commit": sucio, "tope": args.tope, "fuente_tarifa": fuente,
                  "total": len(trozos), "hechos": [], "costes": {}, "gastado": 0.0, "fallos": 0,
                  "completo": False, "parado": None, "iniciado": dt.datetime.now().isoformat(timespec="seconds")}
        _guardar_json(estado_path, estado)
        hechos = set()

    estado["total"] = len(trozos)
    pin, pout = precios
    pendientes = [t for t in trozos if t["id"] not in hechos]
    log(f"{len(pendientes)} trozos pendientes de {len(trozos)} · gastado {estado['gastado']:.4f} $ de {args.tope:.2f} $")

    for t in pendientes:
        user = mensaje_usuario(t, textos)
        tin_est = tokens_de(sistema) + tokens_de(user)
        peor = 2 * (tin_est * pin + args.max_salida * pout)   # two attempts at most
        if estado["gastado"] + peor > args.tope:
            estado["parado"] = (f"tope: {estado['gastado']:.4f} $ gastados, el siguiente trozo ({t['id']}) "
                                f"podría costar hasta {peor:.4f} $. Reanudar con --reanudar y un --tope mayor.")
            break
        mensajes = [{"role": "system", "content": sistema}, {"role": "user", "content": user}]
        resultado, error = None, None
        tok_in = tok_out = 0
        usd = 0.0
        estimado = False
        for intento in (1, 2):
            try:
                texto, usage = cliente(args.modelo, mensajes, args.max_salida)
            except Abort as e:
                estado["parado"] = f"error fatal de OpenRouter en {t['id']}: {e}"
                _guardar_json(estado_path, estado)
                escribir_coste(coste_path, estado)
                log(f"ERROR: {estado['parado']}")
                return 4
            except RuntimeError as e:
                error = str(e)
                if intento == 1:
                    dormir(5)
                continue
            ti = int(usage.get("prompt_tokens") or 0)
            to = int(usage.get("completion_tokens") or 0)
            tok_in += ti
            tok_out += to
            if isinstance(usage.get("cost"), (int, float)):
                usd += float(usage["cost"])
            else:
                usd += (ti or tin_est) * pin + (to or args.max_salida) * pout
                estimado = True
            try:
                resultado = validar_salida(texto)
                break
            except ValueError as e:
                error = f"salida rechazada: {e}"
                mensajes = mensajes[:2] + [
                    {"role": "assistant", "content": texto[:4000]},
                    {"role": "user", "content": f"Tu respuesta no es válida ({e}). Devuelve solo el array JSON con los campos pedidos, o []."}]
        trozo_ref = {"id": t["id"], "fichero": t["fichero"], "desde": t["desde"], "hasta": t["hasta"],
                     "imports": t["imports"], "commit": estado.get("commit")}
        if resultado is None:
            with open(fallos_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"trozo": trozo_ref, "error": error}, ensure_ascii=False) + "\n")
            estado["fallos"] += 1
        else:
            resultado, descartados = filtrar_por_prueba(resultado, t["codigo"])
            if descartados:
                with open(descartes_path, "a", encoding="utf-8") as f:
                    for h in descartados:
                        f.write(json.dumps({**h, "modelo": args.modelo, "trozo": trozo_ref}, ensure_ascii=False) + "\n")
            with open(hall_path, "a", encoding="utf-8") as f:
                for h in resultado:
                    f.write(json.dumps({**h, "modelo": args.modelo, "trozo": trozo_ref}, ensure_ascii=False) + "\n")
        # mark done only after the results are on disk
        estado["costes"][t["id"]] = {"fichero": t["fichero"], "in": tok_in, "out": tok_out, "usd": usd, "estimado": estimado}
        estado["gastado"] += usd
        estado["hechos"].append(t["id"])
        _guardar_json(estado_path, estado)
        escribir_coste(coste_path, estado)
        log(f"  {t['id'][:70]}: {len(resultado) if resultado is not None else 'FALLO'} · {usd:.4f} $")
    else:
        estado["completo"] = True
        estado["terminado"] = dt.datetime.now().isoformat(timespec="seconds")

    _guardar_json(estado_path, estado)
    escribir_coste(coste_path, estado)
    if estado["parado"]:
        log(f"PARADO: {estado['parado']}")
        return 5
    log(f"Hecho: {len(estado['hechos'])} trozos, {estado['fallos']} fallos, {estado['gastado']:.4f} $ · {carpeta}")
    return 0


def main():
    try:
        sys.exit(ejecutar(sys.argv[1:]))
    except Abort as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
