#!/usr/bin/env python3
"""Deterministic checks for the 15-point list of
docs/revision-cruzada/patrones-de-error-2026-10-14.md (section D). No model, no network.

Only the points that can be expressed as grep, AST or structural checks are implemented:
p03 (partial), p04, p06, p07, p10, p11, p12, p14 (partial), p15 (partial, "revisar" only).
Points 1, 2, 5, 8, 9, 13 and the rest of 3 and 15 need judgement: they are listed in the
report as targeted work for an Opus agent, never simulated here.

Usage: see README.md. The scanned repo is never modified; with --ref the files are read
from `git archive <ref>` into a temporary directory, so the working tree and branch of the
repo stay untouched.

Each finding: {punto, comprobacion, fichero, linea, fragmento, regla, gravedad}.
Fragments are masked: anything that looks like a credential becomes "valor omitido".
A line containing "comprobar: ignore" (optionally followed by point ids) is skipped.
A `comprobar.ignore` file at the repo root lists globs (one per line, optional point list
after the glob, e.g. `scripts/legacy/* p07,p12`).
"""
import argparse
import ast
import bisect
import datetime as dt
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile

OS_ROOT = os.path.expanduser("~/iamasters-os")
DEFAULT_SALIDA = os.path.join(OS_ROOT, "docs/revision-cruzada")

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "coverage",
             "__pycache__", ".venv", "venv", ".turbo", ".cache"}
PY_EXTS = {".py"}
JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"}
SH_EXTS = {".sh", ".bash"}
YML_EXTS = {".yml", ".yaml"}
SQL_EXTS = {".sql"}
MAX_BYTES = 1_500_000
GRAVEDAD_ORDEN = {"alta": 0, "media": 1, "baja": 2, "revisar": 3}

# ---------------------------------------------------------------- shared patterns

SECRET_VALUE_RES = [
    re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-|ant-|or-v1-)?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])gh" + r"p_[A-Za-z0-9]{30,}"),  # split so the repo secret scan does not flag the pattern itself
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"xox[bpas]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_\-]{35}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{15,}\.eyJ[A-Za-z0-9_\-]{15,}\.[A-Za-z0-9_\-]{10,}"),
    re.compile(r"sb_secret_[A-Za-z0-9_\-]{10,}"),
    re.compile(r"(?<![A-Za-z0-9])AK" + r"IA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
LONG_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-+/=]{40,}")
LITERAL_ASSIGN_RE = re.compile(
    r"""(?i)\b([\w$]*(?:api_?key|secret|password|passwd|token|bearer)[\w$]*)\s*[:=]\s*(["'`])([^"'`\s]{16,})\2""")
PLACEHOLDER_RE = re.compile(r"(?i)(^https?://|^/|xxx|\*\*\*|your|example|changeme|placeholder|dummy|fake|"
                            r"test|sample|redacted|<|\$\{|process\.env|environ|none|null|todo)")

SECRET_WORD_RE = re.compile(r"(?i)(api_?key|apikey|secret|password|passwd|passwort|token|"
                            r"credential|private_?key|bearer)")
SECRET_IDENT_EXCLUDE = re.compile(
    r"(?i)(tokens|token_?(usd|cost|price)|max_?tokens|tokens?_?(count|used|usage|limit|len|length|budget|estimate|cost|per)|"
    r"(input|output|prompt|completion|total|cached|reasoning|n)_?tokens|tokeniz|"
    r"^(has|is|uses|needs|with|without)_?|_?(name|names|path|file|url|env|envvar|id|ids|field|"
    r"fields|length|len|count|set|present|exists|configured|missing|ok|valid|type|kind|label|"
    r"prefix|hint|ref|refs|header_?name|expires?(_?at|_?in)?|expiry|age|status|error|err)$)")

TODAY_HINT_RE = re.compile(r"(?i)(today|\bhoy\b|heute|week|woche|semana|weekday|isocalendar|"
                           r"hour\s*=\s*0|%Y-%m-%d|midnight|mitternacht|medianoche|\.date\(\)|"
                           r"days\s*=|getDate\(|getDay\(|setHours\(\s*0|startOf|tag\b|dia\b|día)")
TZ_HINT_RE = re.compile(r"(?i)(timeZone|time_?zone|Europe/|ZoneInfo|pytz|\btz\b|tzinfo|zoned|Intl\.)")

PAGINATION_RE = re.compile(
    r"(?i)(offset|cursor|page_?token|pagetoken|next_?page|nextlink|has_?more|paginat|"
    r"\.range\(|start_?after|startafter|\bafter\b|links\.next|[\"']next[\"']|\.next\b(?!\()|"
    r"\bpage\s*(\+=|\+\+|=\s*page\s*\+)|\bskip\b|continuation|scroll_?id|truncat|"
    r"\bmore\b|\bremaining\b|keyset|last_?id|lastid|since_?id)")

IDENT_HINT_RE = re.compile(r"(?i)(phone|telefon|\btel\b|number|nummer|name|email|e_mail|mail|"
                           r"address|adress|thread|chat|jid|sender|absender|\bfrom\b|recipient|"
                           r"empf|folder|ordner|subject|betreff|contact|kontakt|owner|account|"
                           r"iban|person|kunde)")
IDENT_EXCLUDE_RE = re.compile(r"(?i)(url|href|path|pathname|mime|content_?type|ext\b|extension|"
                              r"route|line\b|filename|file_?name|hostname|host\b|domain|header)")
NUM_ID_RE = re.compile(r"(?i)(phone|telefon|\btel\b|number|nummer|jid|iban|id\b|digits)")

WEBHOOK_ROUTE_RE = re.compile(
    r"""(?i)(@\w+\.(post|api_route|route|put)\(\s*["'][^"']*webhook|"""
    r"""\.(post|all|put)\(\s*["'`][^"'`]*webhook|"""
    r"""export\s+(async\s+)?function\s+POST\b|export\s+const\s+POST\b)""")
ACCOUNT_RE = re.compile(r"(?i)(account_?id|accountid|\baccount\b|instance_?id|tenant_?id|"
                        r"x-account|owner_?id|client_?id|workspace_?id)")


def mask(text):
    for rx in SECRET_VALUE_RES:
        text = rx.sub("«valor omitido»", text)
    m = LITERAL_ASSIGN_RE.search(text)
    if m and not PLACEHOLDER_RE.search(m.group(3)):
        text = text.replace(m.group(3), "«valor omitido»")
    return LONG_TOKEN_RE.sub("«valor omitido»", text)


def is_test_path(rel):
    low = rel.lower()
    base = os.path.basename(low)
    parts = low.split("/")
    if any(p in ("test", "tests", "__tests__", "__mocks__", "e2e", "fixtures", "spec", "specs",
                 "bench", "scripts-e2e") for p in parts[:-1]):
        return True
    return bool(re.match(r"(fixtures?\.[cm]?[jt]sx?|fixtures?\.py|test_.*\.py|.*_test\.py|conftest\.py|.*\.(test|spec)\.[cm]?[jt]sx?)$",
                         base))


# ---------------------------------------------------------------- JS/TS tokenizer

REGEX_PREV = set("(,=:[!&|?{};+-*%<>~^")
REGEX_KEYWORDS = {"return", "typeof", "case", "do", "else", "in", "of", "yield", "await",
                  "void", "delete", "throw", "instanceof", "new"}


def js_views(src):
    """Return (no_comments, no_strings), both with the same length and line layout as src.
    no_strings also blanks string, template-text and regex-literal contents, but keeps the
    code inside template `${...}`. Heuristic: quotes end at newline, JSX text may confuse it
    for the rest of one line."""
    n = len(src)
    nc = list(src)
    ns = list(src)

    def blank(arr, a, b):
        for k in range(a, min(b, n)):
            if arr[k] != "\n":
                arr[k] = " "

    i = 0
    in_tpl = False
    tpl_stack = []
    last_sig = ""
    last_word_end = -1
    while i < n:
        c = src[i]
        if in_tpl:
            j = i
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "`" or (src[j] == "$" and j + 1 < n and src[j + 1] == "{"):
                    break
                j += 1
            blank(ns, i, j)
            if j >= n:
                break
            if src[j] == "`":
                in_tpl = False
                i = j + 1
                last_sig = "a"
            else:
                tpl_stack.append(0)
                in_tpl = False
                i = j + 2
                last_sig = "{"
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            j = n if j < 0 else j
            blank(nc, i, j)
            blank(ns, i, j)
            i = j
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(nc, i, j)
            blank(ns, i, j)
            i = j
            continue
        if c in "\"'":
            j = i + 1
            while j < n and src[j] != c and src[j] != "\n":
                if src[j] == "\\":
                    j += 1
                j += 1
            blank(ns, i + 1, j)
            i = j + 1
            last_sig = "a"
            continue
        if c == "`":
            in_tpl = True
            i += 1
            continue
        if c == "/":
            prev_word = ""
            if last_sig == "a" and last_word_end >= 0:
                k = last_word_end
                while k > 0 and (src[k - 1].isalnum() or src[k - 1] in "_$"):
                    k -= 1
                prev_word = src[k:last_word_end]
            if last_sig == "" or last_sig in REGEX_PREV or prev_word in REGEX_KEYWORDS:
                j = i + 1
                in_class = False
                while j < n and src[j] != "\n":
                    if src[j] == "\\":
                        j += 2
                        continue
                    if src[j] == "[":
                        in_class = True
                    elif src[j] == "]":
                        in_class = False
                    elif src[j] == "/" and not in_class:
                        break
                    j += 1
                blank(ns, i + 1, j)
                i = j + 1
                last_sig = "a"
                last_word_end = -1
                continue
        if c == "{" and tpl_stack:
            tpl_stack[-1] += 1
        elif c == "}" and tpl_stack:
            if tpl_stack[-1] == 0:
                tpl_stack.pop()
                in_tpl = True
                i += 1
                continue
            tpl_stack[-1] -= 1
        if c.isalnum() or c in "_$":
            last_sig = "a"
            last_word_end = i + 1
        elif not c.isspace():
            last_sig = c
        i += 1
    return "".join(nc), "".join(ns)


def match_close(text, open_idx):
    """Index of the bracket closing the one at open_idx (text must have strings blanked)."""
    pairs = {"(": ")", "{": "}", "[": "]"}
    opener = text[open_idx]
    closer = pairs[opener]
    depth = 0
    for k in range(open_idx, len(text)):
        ch = text[k]
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return k
    return len(text)


def split_top(text):
    """Split call arguments on top-level commas (strings must be blanked)."""
    out, depth, start = [], 0, 0
    for k, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append((start, k))
            start = k + 1
    out.append((start, len(text)))
    return [(a, b) for a, b in out if text[a:b].strip()]


# ---------------------------------------------------------------- source file

class Fuente:
    def __init__(self, rel, text):
        self.rel = rel
        self.text = text
        self.lines = text.split("\n")
        base = os.path.basename(rel)
        self.base = base
        self.ext = os.path.splitext(base)[1].lower()
        self.is_test = is_test_path(rel)
        self._nl = [k for k, ch in enumerate(text) if ch == "\n"]
        self._tree = False
        self._js = None
        self._parents = None

    @property
    def is_py(self):
        return self.ext in PY_EXTS

    @property
    def is_js(self):
        return self.ext in JS_EXTS

    @property
    def is_sh(self):
        return self.ext in SH_EXTS

    @property
    def is_yml(self):
        return self.ext in YML_EXTS

    @property
    def is_docker(self):
        return self.base.startswith("Dockerfile") or self.base.endswith(".dockerfile")

    @property
    def is_deploy(self):
        return (self.is_sh or self.is_yml or self.is_docker or self.base == "Makefile"
                or self.base.startswith(".env") or self.ext in {".env", ".conf", ".ini"})

    def line_of(self, offset):
        return bisect.bisect_left(self._nl, offset) + 1

    def line_text(self, line):
        return self.lines[line - 1] if 0 < line <= len(self.lines) else ""

    @property
    def tree(self):
        if self._tree is False:
            try:
                self._tree = ast.parse(self.text)
            except (SyntaxError, ValueError):
                self._tree = None
        return self._tree

    @property
    def parents(self):
        if self._parents is None:
            self._parents = {}
            if self.tree is not None:
                for node in ast.walk(self.tree):
                    for child in ast.iter_child_nodes(node):
                        self._parents[child] = node
        return self._parents

    def enclosing_func_src(self, node):
        cur = node
        while cur in self.parents:
            cur = self.parents[cur]
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return "\n".join(self.lines[cur.lineno - 1:(cur.end_lineno or cur.lineno)])
        return self.text

    @property
    def js(self):
        if self._js is None:
            self._js = js_views(self.text)
        return self._js

    def window(self, line, before=40, after=40, text=None):
        lines = (text or self.text).split("\n") if text else self.lines
        return "\n".join(lines[max(0, line - 1 - before):line + after])

    def hallazgo(self, punto, comprobacion, linea, regla, gravedad, fragmento=None):
        lt = self.line_text(linea)
        sup = re.search(r"comprobar:\s*ignore(.*)", lt)
        if sup:
            ids = re.findall(r"p\d\d", sup.group(1))
            if not ids or f"p{punto:02d}" in ids:
                return None
        frag = fragmento if fragmento is not None else lt.strip()
        frag = mask(frag)
        if len(frag) > 200:
            frag = frag[:197] + "..."
        return {"punto": punto, "comprobacion": comprobacion, "fichero": self.rel,
                "linea": linea, "fragmento": frag, "regla": regla, "gravedad": gravedad}


def _add(out, h):
    if h is not None:
        out.append(h)


def call_name(func):
    """Dotted name of a call target, e.g. 'requests.get', 'logger.info', 'print'."""
    parts = []
    cur = func
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    elif isinstance(cur, ast.Call):
        parts.append(call_name(cur.func) + "()")
    else:
        parts.append("?")
    return ".".join(reversed(parts))


def has_kw(call, *names):
    return any(k.arg in names for k in call.keywords) or any(k.arg is None for k in call.keywords)


def kw_value(call, name):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    return None


# ---------------------------------------------------------------- p04 errors nobody sees

SILENT_JS_VALUE = (r"(null|undefined|void\s+0|\[\s*\]|\{\s*\}|\(\s*\{\s*\}\s*\)|\(\s*\[\s*\]\s*\)|"
                   r"false|true|0|-1|\"\s*\"|'\s*'|`\s*`|\(\s*null\s*\))")
JS_CATCH_ARROW_RE = re.compile(r"^(async\s*)?(\(\s*[\w$]*\s*(:\s*[\w$]+)?\s*\)|[\w$]+)\s*=>\s*(" +
                               SILENT_JS_VALUE + r"|\{\s*return\s*" + SILENT_JS_VALUE +
                               r"?\s*;?\s*\})$")
JS_CATCH_BODY_RE = re.compile(r"^((return|continue|break)\s*" + SILENT_JS_VALUE + r"?\s*;?)?$")
JS_NOOP_RE = re.compile(r"^(noop|ignore|_?swallow|\(\)\s*=>\s*\{\s*\})$")


BEST_EFFORT_RE = re.compile(
    r"((\.|\b)(destroy|terminate|close|unlink|unlinkSync|rm|rmSync|rmdir|kill|abort|release|disconnect|"
    r"end|cancel|unref|removeListener|off|stop|quit|mkdir|cleanup|dispose|unsubscribe|"
    r"removeItem|revokeObjectURL|focus|blur|vibrate|play|pause|setItem)\s*\(|protokoll|\blog\w*\.|"
    r"logger|telemetr|metric|\btrack|JSON\.parse|new\s+URL|decodeURI|parseInt|parseFloat|"
    r"Number\(|BigInt\(|atob\(|btoa\(|structuredClone|localStorage|sessionStorage|"
    r"navigator\.|json\.loads|json\.load\(|os\.remove|os\.unlink|shutil\.rmtree|\.close\(\)|"
    r"\bint\(|\bfloat\(|fromisoformat|strptime|os\.kill|\.kill\(|\.terminate\(|\.unlink\(|"
    r"\.rmdir\(|\.remove\()")
ERROR_BODY_RE = re.compile(r"\.(json|text|formData|arrayBuffer|blob)\s*\(\s*\)\s*$")


def match_open_back(text, close_idx):
    """Index of the opener matching the closer at close_idx, scanning backwards."""
    pairs = {")": "(", "}": "{", "]": "["}
    closer = text[close_idx]
    opener = pairs[closer]
    depth = 0
    for k in range(close_idx, -1, -1):
        ch = text[k]
        if ch == closer:
            depth += 1
        elif ch == opener:
            depth -= 1
            if depth == 0:
                return k
    return -1


def receiver_start(ns, idx):
    """Walk back from idx over a member/call chain (a.b?.c(...)[0].d) and return its start."""
    k = idx - 1
    while k >= 0:
        ch = ns[k]
        if ch.isspace():
            k -= 1
        elif ch in ")]":
            o = match_open_back(ns, k)
            if o < 0:
                break
            k = o - 1
        elif ch.isalnum() or ch in "_$.?#!":
            k -= 1
        else:
            break
    return k + 1


def _py_names(node):
    if node is None:
        return set()
    if isinstance(node, ast.Tuple):
        out = set()
        for e in node.elts:
            out |= _py_names(e)
        return out
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, ast.Attribute):
        return {node.attr}
    return set()


def _py_silent_value(v):
    if v is None:
        return True
    if isinstance(v, ast.Constant):
        return True
    if isinstance(v, ast.Dict):
        keys = {k.value for k in v.keys if isinstance(k, ast.Constant)}
        if keys & {"error", "reason", "fehler", "detail"}:
            return False  # the failure is reported to the caller
        for k, val in zip(v.keys, v.values):
            if isinstance(k, ast.Constant) and k.value in ("ok", "success") and \
                    isinstance(val, ast.Constant) and val.value is False:
                return False
    if isinstance(v, (ast.List, ast.Dict, ast.Tuple, ast.Set)):
        return not any(True for _ in ast.iter_child_nodes(v)) or all(
            isinstance(e, ast.Constant) for e in ast.iter_child_nodes(v))
    if isinstance(v, ast.Name):
        return True
    return False


def _py_body_silent(body):
    for st in body:
        if any(isinstance(n, (ast.Call, ast.Raise, ast.Yield, ast.Await)) for n in ast.walk(st)):
            return False
        if isinstance(st, (ast.Pass, ast.Continue, ast.Break)):
            continue
        if isinstance(st, ast.Return) and _py_silent_value(st.value):
            continue
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant):
            continue
        if isinstance(st, (ast.Assign, ast.AnnAssign)) and _py_silent_value(st.value):
            continue
        return False
    return True


def _py_body_desc(body):
    st = body[0]
    if isinstance(st, ast.Return):
        return "return " + (ast.unparse(st.value) if st.value is not None else "None")
    return type(st).__name__.lower()


def p04_except_silencioso(f, ctx):
    out = []
    if f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.ExceptHandler):
                names = _py_names(node.type)
                broad = node.type is None or bool(names & {"Exception", "BaseException"})
                if broad and _py_body_silent(node.body):
                    tipo = "except:" if node.type is None else f"except {ast.unparse(node.type)}"
                    grav = "alta"
                    desc = _py_body_desc(node.body)
                    if desc in ("assign",):
                        grav = "media"
                    parent = f.parents.get(node)
                    if isinstance(parent, ast.Try) and len(parent.body) <= 3:
                        try_src = "\n".join(ast.unparse(st) for st in parent.body)
                        if BEST_EFFORT_RE.search(try_src):
                            grav = "baja"
                            desc += ", alrededor de limpieza o conversión"
                    if grav == "alta" and any(
                            "#" in f.line_text(n) for n in
                            range(node.lineno, (node.end_lineno or node.lineno) + 1)):
                        grav = "media"
                        desc += ", con comentario que lo justifica"
                    if f.is_test:
                        grav = "baja"
                    _add(out, f.hallazgo(
                        4, "p04_except_silencioso", node.lineno,
                        f"{tipo} que traga el error sin registro ni aviso "
                        f"({desc}): no distingue «no hay» de «no pude»", grav))
            elif isinstance(node, ast.With):
                for item in node.items:
                    ce = item.context_expr
                    if (isinstance(ce, ast.Call) and call_name(ce.func).endswith("suppress")
                            and any(_py_names(a) & {"Exception", "BaseException"} for a in ce.args)):
                        _add(out, f.hallazgo(4, "p04_except_silencioso", node.lineno,
                                             "suppress(Exception): todo error se pierde", "media"))
    elif f.is_js:
        nc, ns = f.js
        for m in re.finditer(r"(?<![.\w$])catch\b", ns):
            k = m.end()
            mm = re.compile(r"\s*(\([^)]*\))?\s*\{").match(ns, k)
            if not mm:
                continue
            ob = mm.end() - 1
            cb = match_close(ns, ob)
            body = ns[ob + 1:cb].strip()
            if JS_CATCH_BODY_RE.match(body):
                desc = "vacío" if not body else re.sub(r"\s+", " ", nc[ob + 1:cb].strip())[:40]
                grav = "alta"
                k2 = m.start() - 1
                while k2 >= 0 and ns[k2].isspace():
                    k2 -= 1
                if k2 >= 0 and ns[k2] == "}":
                    ob2 = match_open_back(ns, k2)
                    try_body = nc[ob2 + 1:k2] if ob2 >= 0 else ""
                    if len(try_body.strip()) < 300 and BEST_EFFORT_RE.search(try_body):
                        grav = "baja"
                        desc += ", alrededor de limpieza o conversión"
                if grav == "alta" and re.search(r"//|/\*", f.text[ob + 1:cb]):
                    grav = "media"
                    desc += ", con comentario que lo justifica"
                if f.is_test:
                    grav = "baja"
                _add(out, f.hallazgo(4, "p04_except_silencioso", f.line_of(m.start()),
                                     f"catch {desc}: el error se pierde sin registro", grav))
        for m in re.finditer(r"\.catch\s*\(", ns):
            ob = m.end() - 1
            cb = match_close(ns, ob)
            arg = ns[ob + 1:cb].strip()
            if JS_CATCH_ARROW_RE.match(arg) or JS_NOOP_RE.match(arg):
                short_arg = re.sub(r"\s+", " ", arg)[:40]
                start = receiver_start(ns, m.start()) - 1
                recv = nc[start + 1:m.start()]
                grav = "alta"
                extra = ""
                if ERROR_BODY_RE.search(ns[start + 1:m.start()]):
                    grav, extra = "baja", " (lectura del cuerpo de una respuesta)"
                elif BEST_EFFORT_RE.search(recv):
                    grav, extra = "baja", " (limpieza o registro de mejor esfuerzo)"
                if f.is_test:
                    grav = "baja"
                _add(out, f.hallazgo(4, "p04_except_silencioso", f.line_of(m.start()),
                                     f".catch({short_arg}): convierte el fallo "
                                     "en un valor vacío sin aviso" + extra, grav))
    elif f.is_sh or f.is_docker:
        for i, line in enumerate(f.lines, 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            if re.search(r"\|\|\s*true\b|\|\|\s*:\s*($|;)", s):
                _add(out, f.hallazgo(4, "p04_except_silencioso", i,
                                     "«|| true»: el fallo del comando no para ni avisa", "baja"))
            elif re.search(r"(2>\s*/dev/null|&>\s*/dev/null|>\s*/dev/null\s+2>&1)", s):
                _add(out, f.hallazgo(4, "p04_except_silencioso", i,
                                     "salida de error descartada a /dev/null", "baja"))
    return out


# ---------------------------------------------------------------- p06 deployment

def collect_env_defaults(fuentes):
    """Code-side defaults: {VAR: [(rel, line, default_repr)]} from os.environ.get/os.getenv
    with a default, and process.env.X ?? / || fallbacks."""
    found = {}
    for f in fuentes:
        if f.is_py and f.tree is not None:
            for node in ast.walk(f.tree):
                if (isinstance(node, ast.Call) and len(node.args) >= 2
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)):
                    name = call_name(node.func)
                    if name.endswith("environ.get") or name.endswith("getenv"):
                        parent = f.parents.get(node)
                        cast = (isinstance(parent, ast.Call)
                                and call_name(parent.func) in ("int", "float", "Decimal"))
                        found.setdefault(node.args[0].value, []).append(
                            (f.rel, node.lineno, ast.unparse(node.args[1]), cast))
        elif f.is_js:
            nc, _ = f.js
            # `||` already replaces "", only `??` lets an empty compose value through
            for m in re.finditer(r"(?:process\.env|\benv)(?:\.(\w+)|\[\s*[\"'](\w+)[\"']\s*\])"
                                 r"\s*\?\?\s*([^;,)\n]+)", nc):
                found.setdefault(m.group(1) or m.group(2), []).append(
                    (f.rel, f.line_of(m.start()), m.group(3).strip()[:40], "??"))
    return found


def _norm_default(v):
    return v.strip().strip("\"'")


def _joined_lines(f):
    """Yield (first_line_no, joined_text) with backslash continuations merged."""
    buf, start = [], None
    for i, line in enumerate(f.lines, 1):
        if start is None:
            start = i
        if line.rstrip().endswith("\\"):
            buf.append(line.rstrip()[:-1])
            continue
        buf.append(line)
        yield start, " ".join(buf)
        buf, start = [], None
    if buf:
        yield start, " ".join(buf)


def p06_despliegue(f, ctx):
    out = []
    defaults = ctx.get("env_defaults", {})
    if f.is_yml or f.base.startswith(".env") or f.ext == ".env":
        for i, line in enumerate(f.lines, 1):
            if line.strip().startswith("#"):
                continue
            for m in re.finditer(r"\$\{(\w+):?-([^}]*)\}", line):
                var, dflt = m.group(1), m.group(2)
                code = defaults.get(var, [])
                if dflt == "":
                    real = [c for c in code if _norm_default(c[2]) not in ("", "None")]
                    if real:
                        c0 = next((c for c in real if c[3]), real[0])
                        donde = f"{c0[0]}:{c0[1]}"
                        if c0[3] == "??":
                            regla = (f"${{{var}:-}} pasa cadena vacía si falta en .env y el «??» "
                                     f"de {donde} no la sustituye: se usa \"\" en vez de {c0[2]}")
                        elif c0[3]:
                            regla = (f"${{{var}:-}} pasa cadena vacía si falta en .env: el código "
                                     f"la convierte a número ({donde}, por defecto {c0[2]}) y "
                                     "revienta al arrancar")
                        else:
                            regla = (f"${{{var}:-}} pasa cadena vacía si falta en .env y pisa el "
                                     f"valor por defecto del código ({donde}, {c0[2]})")
                        _add(out, f.hallazgo(6, "p06_despliegue", i, regla,
                                             "alta" if c0[3] is True else "media"))
                    elif code:
                        continue
                    else:
                        _add(out, f.hallazgo(
                            6, "p06_despliegue", i,
                            f"${{{var}:-}} llega vacía si falta en .env; el código no declara "
                            "valor por defecto: comprobar que la trata", "baja"))
                elif code and all(_norm_default(c[2]) != _norm_default(dflt) for c in code) and \
                        any(_norm_default(c[2]) not in ("", "None", "null", "undefined") for c in code):
                    _add(out, f.hallazgo(
                        6, "p06_despliegue", i,
                        f"dos valores por defecto distintos para {var}: despliegue «{dflt}», "
                        f"código {code[0][2]} ({code[0][0]}:{code[0][1]})", "media"))
    if f.is_deploy or f.is_py or f.is_js:
        src_lines = _joined_lines(f) if (f.is_sh or f.is_yml or f.base == "Makefile") else \
            enumerate(f.lines, 1)
        for i, line in src_lines:
            s = line.strip()
            if s.startswith("#") or s.startswith("//"):
                continue
            if re.search(r"docker\s+service\s+update\b", s) and "--force" in s and "--image" not in s:
                printed = re.match(r"(echo|printf|log|print)\b", s) is not None
                _add(out, f.hallazgo(6, "p06_despliegue", i,
                                     "docker service update --force sin --image: reinicia la imagen "
                                     "que ya tenía, no la nueva" +
                                     (" (instrucción impresa para una persona)" if printed else ""),
                                     "media" if printed else "alta"))
            for m in re.finditer(r"(?<![@\w])([\w.\-/]+(?::\d+)?/?[\w.\-]+):latest\b", s):
                if f.is_py or f.is_js:
                    if not re.search(r"(image|docker|FROM|pull|tag)", s, re.I):
                        continue
                _add(out, f.hallazgo(6, "p06_despliegue", i,
                                     f"etiqueta :latest ({m.group(1)}): no fija qué versión corre",
                                     "media"))
                break
    if f.base == "_journal.json":
        try:
            data = json.loads(f.text)
        except ValueError:
            return out
        entries = data.get("entries", []) if isinstance(data, dict) else []
        seen = {}
        prev = None
        for e in entries:
            w = e.get("when")
            tag = e.get("tag", "?")
            line = next((k for k, l in enumerate(f.lines, 1) if str(w) in l), 1)
            if w in seen:
                _add(out, f.hallazgo(6, "p06_despliegue", line,
                                     f"migración {tag} repite when={w} de {seen[w]}: drizzle puede "
                                     "saltarse una", "alta", fragmento=f"{tag} when={w}"))
            elif prev is not None and w is not None and w < prev:
                _add(out, f.hallazgo(6, "p06_despliegue", line,
                                     f"migración {tag} con when anterior a la previa", "media",
                                     fragmento=f"{tag} when={w}"))
            if w is not None:
                seen.setdefault(w, tag)
                prev = w if prev is None else max(prev, w)
    return out


# ---------------------------------------------------------------- p07 unbounded work

PY_HTTP_MODULES = {"requests"}
PY_HTTP_VERBS = {"get", "post", "put", "patch", "delete", "head", "options", "request"}


def _py_loop_has_exit(loop):
    stack = list(loop.body)
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(n, (ast.Break, ast.Return, ast.Raise)):
            return True
        if isinstance(n, ast.Call) and call_name(n.func) in ("sys.exit", "exit", "os._exit"):
            return True
        if isinstance(n, (ast.While, ast.For, ast.AsyncFor)):
            # a break inside a nested loop does not leave this one; returns/raises still do
            for sub in ast.walk(n):
                if isinstance(sub, (ast.Return, ast.Raise)):
                    return True
            continue
        stack.extend(ast.iter_child_nodes(n))
    return False


def p07_sin_techo(f, ctx):
    out = []
    if f.is_test:
        return out
    if f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.Call):
                name = call_name(node.func)
                parts = name.split(".")
                if (len(parts) == 2 and parts[0] in PY_HTTP_MODULES and parts[1] in PY_HTTP_VERBS
                        and not has_kw(node, "timeout")):
                    _add(out, f.hallazgo(7, "p07_sin_techo", node.lineno,
                                         f"{name}() sin timeout: puede colgar el proceso", "media"))
                elif parts[-1] == "urlopen" and not has_kw(node, "timeout") and len(node.args) < 3:
                    _add(out, f.hallazgo(7, "p07_sin_techo", node.lineno,
                                         "urlopen() sin timeout: puede colgar el proceso", "media"))
                elif (name in ("subprocess.run", "subprocess.check_output", "subprocess.call",
                               "subprocess.check_call") and not has_kw(node, "timeout")
                      and not re.search(r"""["'](-m|--max-time|--connect-timeout|timeout)["']""",
                                        " ".join(ast.unparse(x) for x in node.args))):
                    _add(out, f.hallazgo(7, "p07_sin_techo", node.lineno,
                                         f"{name}() sin timeout", "baja"))
            elif (isinstance(node, ast.While) and isinstance(node.test, ast.Constant)
                  and node.test.value is True and not _py_loop_has_exit(node)):
                sleeps = any(isinstance(n, ast.Call) and call_name(n.func).endswith("sleep")
                             for n in ast.walk(node))
                _add(out, f.hallazgo(
                    7, "p07_sin_techo", node.lineno,
                    "while True sin break/return/raise" +
                    (" (con sleep: confirmar que es el bucle del demonio)" if sleeps
                     else ": bucle sin salida ni pausa"), "baja" if sleeps else "media"))
    elif f.is_js:
        nc, ns = f.js
        client = bool(re.search(r"^\s*[\"']use client[\"']", f.text, re.M))
        axios_default = bool(re.search(r"axios\.create\([^)]*timeout|axios\.defaults\.timeout",
                                       nc, re.S))
        for m in re.finditer(r"(?<![.\w$])fetch\s*\(", ns):
            ob = m.end() - 1
            cb = match_close(ns, ob)
            args = split_top(ns[ob + 1:cb])
            if not args:
                continue
            first_raw = nc[ob + 1 + args[0][0]:ob + 1 + args[0][1]].strip()
            if len(args) >= 2:
                second = ns[ob + 1 + args[1][0]:ob + 1 + args[1][1]].strip()
                if not second.startswith("{") or "signal" in second:
                    continue
            relative = bool(re.match(r"""^[`'"]/""", first_raw))
            grav = "baja" if (client or relative) else "media"
            _add(out, f.hallazgo(7, "p07_sin_techo", f.line_of(m.start()),
                                 "fetch() sin signal/timeout" +
                                 (" (cliente o ruta propia)" if grav == "baja" else
                                  ": la llamada puede colgar sin límite"), grav))
        if not axios_default:
            for m in re.finditer(r"(?<![.\w$])axios(\.(get|post|put|patch|delete|request))?\s*\(",
                                 ns):
                ob = m.end() - 1
                cb = match_close(ns, ob)
                if "timeout" not in ns[ob:cb]:
                    _add(out, f.hallazgo(7, "p07_sin_techo", f.line_of(m.start()),
                                         "axios sin timeout (por defecto, ninguno)", "media"))
        for m in re.finditer(r"\bwhile\s*\(\s*(true|1)\s*\)|\bfor\s*\(\s*;\s*;\s*\)", ns):
            k = ns.find("{", m.end())
            if k < 0:
                continue
            body = ns[k:match_close(ns, k)]
            if not re.search(r"\b(break|return|throw)\b|process\.exit", body):
                _add(out, f.hallazgo(7, "p07_sin_techo", f.line_of(m.start()),
                                     "bucle infinito sin break/return/throw", "media"))
    return out


# ---------------------------------------------------------------- p10 secrets in logs

LOG_FUNCS_PY = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
SAFE_WRAPPERS = re.compile(r"(?i)(^len$|^bool$|^type$|mask|redact|hash|sha|md5|^repr_safe|"
                           r"^is_?set|^present|^short|^tail|^fingerprint|^censor|^hide)")


def _is_secret_ident(name):
    if not SECRET_WORD_RE.search(name):
        return False
    return not SECRET_IDENT_EXCLUDE.search(name)


def _py_is_log_call(call):
    name = call_name(call.func)
    if name in ("print", "pprint", "pprint.pprint"):
        return True
    parts = name.split(".")
    return (len(parts) >= 2 and parts[-1] in LOG_FUNCS_PY
            and re.search(r"(?i)(log|logger|logging)", parts[-2]) is not None)


def _py_secret_args(f, call):
    hits = []
    whole_env = False
    stack = list(call.args) + [k.value for k in call.keywords]
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Call) and SAFE_WRAPPERS.search(call_name(n.func).split(".")[-1]):
            continue
        if isinstance(n, ast.Attribute) and n.attr == "environ":
            parent = f.parents.get(n)
            if not isinstance(parent, (ast.Subscript, ast.Attribute)):
                whole_env = True
            continue
        if isinstance(n, ast.Name) and _is_secret_ident(n.id):
            hits.append(n.id)
        elif isinstance(n, ast.Attribute) and _is_secret_ident(n.attr):
            hits.append(n.attr)
            continue
        elif (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
              and isinstance(n.slice.value, str) and _is_secret_ident(n.slice.value)):
            hits.append(n.slice.value)
            continue
        stack.extend(ast.iter_child_nodes(n))
    return hits, whole_env


JS_LOG_RE = re.compile(r"(?<![\w$])(console\.(log|info|warn|error|debug|trace|dir)|"
                       r"(logger|log|this\.log|this\.logger|ctx\.log|app\.log|req\.log|fastify\.log)"
                       r"\.(info|warn|error|debug|trace|fatal|log))\s*\(")


def p10_secretos(f, ctx):
    out = []
    # hard-coded credentials, any file type we scan
    for i, line in enumerate(f.lines, 1):
        for rx in SECRET_VALUE_RES:
            if rx.search(line):
                _add(out, f.hallazgo(10, "p10_secretos", i,
                                     "credencial escrita en el código" +
                                     (" (fichero de test: comprobar que es falsa)" if f.is_test
                                      else ""), "baja" if f.is_test else "alta",
                                     fragmento="valor omitido"))
                break
        else:
            m = LITERAL_ASSIGN_RE.search(line)
            if (m and not PLACEHOLDER_RE.search(m.group(3)) and not f.is_test
                    and re.search(r"\d", m.group(3)) and re.search(r"[A-Za-z]", m.group(3))
                    and not re.fullmatch(r"[a-z_.\-]+\d?", m.group(3))):
                if re.search(r"(?i)(url|uri|endpoint|path|host)$", m.group(1)):
                    continue
                _add(out, f.hallazgo(10, "p10_secretos", i,
                                     f"literal asignado a {m.group(1)}: posible credencial",
                                     "media", fragmento="valor omitido"))
    if f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.Call) and _py_is_log_call(node):
                hits, whole_env = _py_secret_args(f, node)
                if whole_env:
                    _add(out, f.hallazgo(10, "p10_secretos", node.lineno,
                                         "os.environ entero a un registro o a la salida", "alta"))
                elif hits:
                    _add(out, f.hallazgo(10, "p10_secretos", node.lineno,
                                         f"registro que imprime {', '.join(sorted(set(hits)))}",
                                         "baja" if f.is_test else "media"))
    elif f.is_js:
        nc, ns = f.js
        for m in JS_LOG_RE.finditer(ns):
            ob = m.end() - 1
            cb = match_close(ns, ob)
            args = ns[ob + 1:cb]
            if re.search(r"process\.env(?!\s*(\.|\[|\?\.))", args):
                _add(out, f.hallazgo(10, "p10_secretos", f.line_of(m.start()),
                                     "process.env entero a un registro", "alta"))
                continue
            hits = []
            for im in re.finditer(r"[A-Za-z_$][\w$]*", args):
                name = im.group(0)
                tail = args[im.end():im.end() + 12]
                head = args[max(0, im.start() - 8):im.start()]
                if re.match(r"\s*\.(length|size)\b", tail):
                    continue
                if re.search(r"(Boolean|mask|redact|hash|len)\s*\(\s*$", head):
                    continue
                if _is_secret_ident(name):
                    hits.append(name)
            if hits:
                _add(out, f.hallazgo(10, "p10_secretos", f.line_of(m.start()),
                                     f"registro que imprime {', '.join(sorted(set(hits)))}",
                                     "baja" if f.is_test else "media"))
    return out


# ---------------------------------------------------------------- p11 time zones

SCHEDULERS = {"BackgroundScheduler", "AsyncIOScheduler", "BlockingScheduler", "TornadoScheduler",
              "GeventScheduler"}


def _tz_is_utc(v):
    if v is None:
        return False
    s = ast.unparse(v).lower()
    return "utc" in s


def p11_zona_horaria(f, ctx):
    out = []
    if f.is_test:
        return out
    if f.is_py and f.tree is not None:
        sched_local = False
        configured = re.search(r"\.configure\([^)]*timezone", f.text) is not None
        calls = [n for n in ast.walk(f.tree) if isinstance(n, ast.Call)]
        for node in calls:
            short = call_name(node.func).split(".")[-1]
            if short in SCHEDULERS:
                tz = kw_value(node, "timezone")
                if tz is not None and not _tz_is_utc(tz):
                    sched_local = True
        for node in calls:
            name = call_name(node.func)
            short = name.split(".")[-1]
            if short in SCHEDULERS:
                tz = kw_value(node, "timezone")
                if tz is None and not configured and not has_kw(node, "timezone"):
                    _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                         f"{short}() sin timezone: toma la zona del contenedor",
                                         "alta"))
                elif _tz_is_utc(tz):
                    _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                         f"{short}(timezone=UTC): las horas de los trabajos se "
                                         "mueven una hora con el cambio de horario de Madrid",
                                         "media"))
            elif short == "CronTrigger" or (short == "from_crontab" and "CronTrigger" in name):
                tz = kw_value(node, "timezone")
                if (tz is None and not sched_local) or _tz_is_utc(tz):
                    _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                         "CronTrigger en UTC (o sin zona y heredando UTC/contenedor):"
                                         " la hora de Madrid cambia el 25-10 y el 29-03", "media"))
            elif short == "add_job":
                trig = node.args[1] if len(node.args) > 1 else kw_value(node, "trigger")
                if (isinstance(trig, ast.Constant) and trig.value == "cron"
                        and kw_value(node, "timezone") is None and not sched_local):
                    _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                         "add_job('cron') sin timezone y scheduler sin zona local",
                                         "media"))
            elif name.endswith("date.today"):
                _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                     "date.today(): «hoy» en la zona del contenedor", "media"))
            elif short in ("now", "utcnow") and name.split(".")[0] in ("datetime", "dt") and \
                    (short == "utcnow" or (not node.args and kw_value(node, "tz") is None)):
                line = f.line_text(node.lineno)
                if TODAY_HINT_RE.search(line) and not TZ_HINT_RE.search(line):
                    _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                         f"{name}() sin zona usado para un día o semana", "media"))
            elif name.startswith("schedule.every") and name.endswith(".at"):
                _add(out, f.hallazgo(11, "p11_zona_horaria", node.lineno,
                                     "schedule...at(): hora del contenedor", "media"))
    elif f.is_js:
        nc, ns = f.js
        for m in re.finditer(r"toISOString\(\)\s*\.\s*(slice|substring|substr)\(\s*0\s*,\s*10\s*\)|"
                             r"toISOString\(\)\s*\.\s*split\(\s*[\"'`]T", nc):
            line = f.line_of(m.start())
            near = "\n".join(f.lines[max(0, line - 6):line + 2])
            if re.search(r"setUTC|getUTC|T00:00:00(\.000)?Z|Date\.UTC\(", near):
                continue  # deliberate calendar arithmetic in UTC on a date string
            if not TZ_HINT_RE.search(f.line_text(line)):
                _add(out, f.hallazgo(11, "p11_zona_horaria", line,
                                     "fecha del día sacada de toISOString(): es el día en UTC, "
                                     "no en Madrid/Berlín (00:00 a 02:00 cae en el día anterior)",
                                     "media"))
        flagged = {h["linea"] for h in out}
        for m in re.finditer(r"new\s+Date\s*\(\s*\)", ns):
            line = f.line_of(m.start())
            lt = f.line_text(line)
            if line in flagged:
                continue
            if TODAY_HINT_RE.search(lt) and not TZ_HINT_RE.search(lt):
                flagged.add(line)
                _add(out, f.hallazgo(11, "p11_zona_horaria", line,
                                     "new Date() usado para un día o semana sin zona explícita",
                                     "media"))
        for m in re.finditer(r"(?<![\w$])(cron\.schedule|schedule\.scheduleJob|new\s+CronJob)\s*\(",
                             ns):
            ob = m.end() - 1
            cb = match_close(ns, ob)
            if not re.search(r"timezone|timeZone|Europe/", nc[ob:cb]):
                _add(out, f.hallazgo(11, "p11_zona_horaria", f.line_of(m.start()),
                                     "cron sin zona horaria: toma la del contenedor", "media"))
    return out


# ---------------------------------------------------------------- p12 caps that hide data

PY_LIMIT_KWS = {"limit", "max_results", "maxResults", "page_size", "pageSize", "per_page",
                "perPage", "top", "max_items"}
JS_LIMIT_RE = re.compile(r"(?<![\w$])(limit|maxResults|pageSize|per_page|perPage|max_items|top)"
                         r"\s*[:=]\s*(\d+)\b|\.limit\(\s*(\d+)\s*\)|\$top=(\d+)|"
                         r"\b(?:LIMIT|limit)\s+(\d+)\b|[?&](limit|per_page|pageSize|maxResults)="
                         r"(\d+)")
SLICE_DATA_EXCLUDE = re.compile(r"(?i)(text|content|body|str|msg|message|title|snippet|preview|"
                                r"summary|name|desc|line|subject|prompt|raw|html|hash|key|token|"
                                r"label|caption|excerpt|output|stdout|stderr|err|error|url|"
                                r"transcript|sha|digest|value|query|input|word|char)")


def _limit_value(groups):
    for g in groups:
        if g and g.isdigit():
            return int(g)
    return None


def p12_topes(f, ctx):
    out = []
    if f.is_test:
        return out
    if f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            n_val, what = None, None
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                m = re.search(r"(?i)\bLIMIT\s+(\d+)\b|\$top=(\d+)|[?&](?:limit|per_page|pageSize|"
                              r"maxResults)=(\d+)", node.value)
                if m:
                    n_val, what = _limit_value(m.groups()), m.group(0)
            elif isinstance(node, ast.keyword) and node.arg in PY_LIMIT_KWS and \
                    isinstance(node.value, ast.Constant) and isinstance(node.value.value, int) and \
                    not isinstance(node.value.value, bool):
                n_val, what = node.value.value, f"{node.arg}={node.value.value}"
            elif isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if (isinstance(k, ast.Constant) and k.value in
                            {"limit", "$top", "maxResults", "pageSize", "per_page", "page_size",
                             "top"} and isinstance(v, ast.Constant) and isinstance(v.value, int)):
                        n_val, what = v.value, f"{k.value}: {v.value}"
            if n_val is None or n_val < 2:
                continue
            lineno = getattr(node, "lineno", None) or getattr(node.value, "lineno", 1)
            scope = f.enclosing_func_src(node)
            if PAGINATION_RE.search(scope.replace(what, "")):
                continue
            _add(out, f.hallazgo(12, "p12_topes", lineno,
                                 f"tope fijo {what} sin paginación ni aviso en la función: "
                                 "si hay más, se pierden en silencio", "media"))
    elif f.is_js:
        nc, ns = f.js
        nc_lines = nc.split("\n")
        seen = set()
        for m in JS_LIMIT_RE.finditer(nc):
            n_val = _limit_value(m.groups())
            if n_val is None or n_val < 2:
                continue
            line = f.line_of(m.start())
            if line in seen:
                continue
            if re.match(r"\w+\s*=", m.group(0)) and re.match(
                    r"^\s*(export\s+)?(async\s+)?(function\s*\*?\s*)?[\w$]+\s*\(",
                    nc_lines[line - 1]):
                continue  # parameter default in a signature: the caller decides
            win = "\n".join(nc_lines[max(0, line - 41):line + 40]).replace(m.group(0), "")
            if PAGINATION_RE.search(win):
                continue
            seen.add(line)
            _add(out, f.hallazgo(12, "p12_topes", line,
                                 f"tope fijo «{m.group(0).strip()}» sin paginación ni aviso "
                                 "cerca (±40 líneas)", "media"))
        for m in re.finditer(r"([\w$.\]\)]+)\.slice\(\s*0\s*,\s*(\d+)\s*\)", ns):
            recv, n_val = m.group(1), int(m.group(2))
            line = f.line_of(m.start())
            if n_val < 2 or line in seen or SLICE_DATA_EXCLUDE.search(recv):
                continue
            win = "\n".join(nc_lines[max(0, line - 41):line + 40])
            if PAGINATION_RE.search(win):
                continue
            seen.add(line)
            _add(out, f.hallazgo(12, "p12_topes", line,
                                 f"{recv}.slice(0, {n_val}) recorta una lista sin avisar", "baja"))
    elif f.ext in SQL_EXTS:
        for i, line in enumerate(f.lines, 1):
            if line.strip().startswith("--"):
                continue
            m = re.search(r"(?i)\bLIMIT\s+(\d+)\b", line)
            if m and int(m.group(1)) > 1:
                _add(out, f.hallazgo(12, "p12_topes", i,
                                     f"LIMIT {m.group(1)} en SQL: ¿quién se entera si hay más?",
                                     "baja"))
    return out


# ---------------------------------------------------------------- p03 webhooks without account

FAIL_OPEN_RE = re.compile(
    r"(?i)\bif\s*\(?\s*(?:self\.|cfg\.|config\.|settings\.|s\.|env\.|process\.env\.)?"
    r"[\w.]*(?:secret|token|api_?key|password)[\w]*\s*(?:and|&&)\s*[\w.\[\]\"']+\s*!==?\s*")


def p03_webhook_sin_cuenta(f, ctx):
    out = []
    if f.is_test or not (f.is_py or f.is_js):
        return out
    text = f.js[0] if f.is_js else f.text
    for m in FAIL_OPEN_RE.finditer(text):
        _add(out, f.hallazgo(3, "p03_webhook_sin_cuenta", f.line_of(m.start()),
                             "la comprobación del secreto solo corre si la variable tiene valor: "
                             "con la variable vacía, cualquiera entra", "alta"))
    if f.is_js:
        comments = "".join(t for t, k in zip(f.text, text) if t != k)
    else:
        comments = "\n".join(l for l in f.lines if l.lstrip().startswith("#"))
    path_hook = "webhook" in f.rel.lower() or "webhook" in comments.lower()
    m = None
    for mm in WEBHOOK_ROUTE_RE.finditer(text):
        if "webhook" in mm.group(0).lower() or path_hook:
            m = mm
            break
    if m is None:
        return out
    if ACCOUNT_RE.search(text):
        return out
    _add(out, f.hallazgo(3, "p03_webhook_sin_cuenta", f.line_of(m.start()),
                         "webhook sin ninguna referencia a account_id/cuenta en el fichero: "
                         "comprobar que filtra la cuenta antes de actuar", "media"))
    return out


# ---------------------------------------------------------------- p14 tests (partial)

def p14_tests_parcial(f, ctx):
    out = []
    if not f.is_test:
        return out
    if f.is_js:
        _, ns = f.js
        for m in re.finditer(r"(?<![\w$.])(it|test|describe|suite)\.only\s*\(", ns):
            _add(out, f.hallazgo(14, "p14_tests_parcial", f.line_of(m.start()),
                                 f"{m.group(1)}.only: el resto de la suite no corre", "alta"))
        for m in re.finditer(r"(?<![\w$.])((it|test|describe|suite)\.skip|xit|xdescribe|"
                             r"(it|test)\.todo)\s*\(", ns):
            _add(out, f.hallazgo(14, "p14_tests_parcial", f.line_of(m.start()),
                                 f"{m.group(1)}: test que no corre", "baja"))
    elif f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for d in node.decorator_list:
                    target = d.func if isinstance(d, ast.Call) else d
                    name = call_name(target) if isinstance(target, (ast.Attribute, ast.Name)) else ""
                    if name.endswith("mark.skip") or name in ("unittest.skip", "skip"):
                        _add(out, f.hallazgo(14, "p14_tests_parcial", d.lineno,
                                             f"@{name}: test que no corre", "baja"))
    return out


# ---------------------------------------------------------------- p15 identity by text (partial)

def p15_identidad_texto(f, ctx):
    out = []
    if f.is_test:
        return out
    if f.is_js:
        nc, ns = f.js
        for m in re.finditer(r"([\w$][\w$.\]\[\)\(]*?)\.(endsWith|startsWith|includes)\s*\(", ns):
            chain, meth = m.group(1), m.group(2)
            ob = m.end() - 1
            cb = match_close(ns, ob)
            arg_nc = nc[ob + 1:cb].strip()
            arg_ns = ns[ob + 1:cb].strip()
            last = re.findall(r"[A-Za-z_$][\w$]*", chain)
            recv = ".".join(last[-2:]) if last else chain
            if IDENT_EXCLUDE_RE.search(recv) or re.match(r"""^["'`][./]|^["'`]https?:""", arg_nc):
                continue
            if meth == "includes" and re.search(r"s$|List$|Set$|Ids$|ids$|Array$", last[-1] if
                                                last else ""):
                continue
            if last and re.fullmatch(r"[A-Z][A-Z0-9_]+", last[-1]):
                continue  # constant list of known values
            if re.fullmatch(r"""["'`].{0,2}["'`]""", arg_nc):
                continue  # single-character test such as includes("@")
            if IDENT_HINT_RE.search(recv) or (IDENT_HINT_RE.search(arg_ns) and
                                              not arg_nc.startswith(("'", '"', "`"))):
                _add(out, f.hallazgo(15, "p15_identidad_texto", f.line_of(m.start()),
                                     f"{recv}.{meth}(...) sobre una identidad: revisar si dos "
                                     "personas, hilos o carpetas distintas pasarían como la misma",
                                     "revisar"))
        for m in re.finditer(r"([\w$][\w$.]*)\.slice\(\s*-\s*(\d+)\s*\)", ns):
            if NUM_ID_RE.search(m.group(1)) or IDENT_HINT_RE.search(m.group(1)):
                _add(out, f.hallazgo(15, "p15_identidad_texto", f.line_of(m.start()),
                                     f"{m.group(1)}.slice(-{m.group(2)}): identidad por los "
                                     "últimos dígitos", "revisar"))
    elif f.is_py and f.tree is not None:
        for node in ast.walk(f.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                    node.func.attr in ("endswith", "startswith"):
                recv = ast.unparse(node.func.value)
                arg = ast.unparse(node.args[0]) if node.args else ""
                if IDENT_EXCLUDE_RE.search(recv) or re.match(r"""^["'][./]""", arg):
                    continue
                if IDENT_HINT_RE.search(recv):
                    _add(out, f.hallazgo(15, "p15_identidad_texto", node.lineno,
                                         f"{recv[:40]}.{node.func.attr}(...) sobre una identidad: "
                                         "revisar", "revisar"))
            elif (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice)
                  and node.slice.upper is None and isinstance(node.slice.lower, ast.UnaryOp)
                  and isinstance(node.slice.lower.op, ast.USub)):
                recv = ast.unparse(node.value)
                if NUM_ID_RE.search(recv) or IDENT_HINT_RE.search(recv):
                    _add(out, f.hallazgo(15, "p15_identidad_texto", node.lineno,
                                         f"{recv[:40]}[{ast.unparse(node.slice)}]: identidad por "
                                         "los últimos caracteres", "revisar"))
            elif isinstance(node, ast.Compare) and any(isinstance(o, ast.In) for o in node.ops):
                right = node.comparators[0]
                if isinstance(right, ast.Call) and isinstance(right.func, ast.Attribute) and \
                        right.func.attr in ("lower", "casefold"):
                    recv = ast.unparse(right.func.value)
                    if IDENT_HINT_RE.search(recv) and not IDENT_EXCLUDE_RE.search(recv):
                        _add(out, f.hallazgo(15, "p15_identidad_texto", node.lineno,
                                             f"subcadena «in {recv[:40]}.lower()» sobre una "
                                             "identidad: revisar", "revisar"))
    return out


CHECKS = [p03_webhook_sin_cuenta, p04_except_silencioso, p06_despliegue, p07_sin_techo,
          p10_secretos, p11_zona_horaria, p12_topes, p14_tests_parcial, p15_identidad_texto]


# ---------------------------------------------------------------- walking

def load_ignore(root):
    rules = []
    path = os.path.join(root, "comprobar.ignore")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                pts = set(re.findall(r"p\d\d", " ".join(parts[1:]))) if len(parts) > 1 else None
                rules.append((parts[0], pts))
    return rules


def ignored(rel, punto, rules):
    for glob, pts in rules:
        hit = fnmatch.fnmatch(rel, glob) or (glob.endswith("/") and rel.startswith(glob)) or \
            rel.startswith(glob.rstrip("/") + "/")
        if hit and (pts is None or f"p{punto:02d}" in pts):
            return True
    return False


def wanted(base, ext):
    if base.endswith(".min.js") or base.endswith(".d.ts") or base.endswith(".map"):
        return False
    return (ext in PY_EXTS | JS_EXTS | SH_EXTS | YML_EXTS | SQL_EXTS or base == "_journal.json"
            or base.startswith("Dockerfile") or base == "Makefile"
            or base in (".env.example", ".env.sample", ".env.template"))


def walk(root, subdirs=None):
    fuentes, skipped = [], []
    starts = [os.path.join(root, s) for s in subdirs] if subdirs else [root]
    for start in starts:
        for dirpath, dirnames, filenames in os.walk(start):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                ext = os.path.splitext(fn)[1].lower()
                if not wanted(fn, ext):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                try:
                    if os.path.getsize(full) > MAX_BYTES:
                        skipped.append((rel, "demasiado grande"))
                        continue
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        fuentes.append(Fuente(rel, fh.read()))
                except OSError as exc:
                    skipped.append((rel, str(exc)))
    return fuentes, skipped


def run(root, subdirs=None, puntos=None):
    fuentes, skipped = walk(root, subdirs)
    rules = load_ignore(root)
    ctx = {"env_defaults": collect_env_defaults(fuentes)}
    hallazgos = []
    for f in fuentes:
        if f.is_py and f.tree is None:
            skipped.append((f.rel, "Python que no compila: sin análisis AST"))
        for chk in CHECKS:
            punto = int(chk.__name__[1:3])
            if puntos and punto not in puntos:
                continue
            for h in chk(f, ctx):
                if not ignored(f.rel, punto, rules):
                    hallazgos.append(h)
    uniq = {}
    for h in hallazgos:
        uniq.setdefault((h["punto"], h["comprobacion"], h["fichero"], h["linea"]), h)
    hallazgos = list(uniq.values())
    hallazgos.sort(key=lambda h: (GRAVEDAD_ORDEN[h["gravedad"]], h["punto"], h["fichero"],
                                  h["linea"]))
    return hallazgos, {"ficheros": len(fuentes), "omitidos": skipped}


def export_ref(repo, ref, dest):
    """Extract `git archive <ref>` of repo into dest without touching the repo."""
    data = subprocess.run(["git", "-C", repo, "archive", "--format=tar", ref],
                          check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        try:
            tf.extractall(dest, filter="data")
        except TypeError:
            tf.extractall(dest)
    commit = subprocess.run(["git", "-C", repo, "rev-parse", "--short", ref], check=True,
                            capture_output=True, text=True).stdout.strip()
    return commit


def resumen(hallazgos):
    por = {}
    for h in hallazgos:
        key = f"p{h['punto']:02d}"
        por.setdefault(key, {"alta": 0, "media": 0, "baja": 0, "revisar": 0})
        por[key][h["gravedad"]] += 1
    return dict(sorted(por.items()))


def parse_args(argv):
    p = argparse.ArgumentParser(description="Comprobaciones deterministas de los 15 puntos",
                                allow_abbrev=False)
    p.add_argument("repo", help="carpeta del repo (solo lectura)")
    p.add_argument("--nombre", help="nombre corto para la carpeta de salida")
    p.add_argument("--ref", help="leer esta rama o commit con git archive, sin tocar el repo")
    p.add_argument("--sub", action="append", default=[],
                   help="subcarpeta a revisar (repetible); por defecto todo el repo")
    p.add_argument("--puntos", help="solo estos puntos, p. ej. 4,6,11")
    p.add_argument("--salida", help="carpeta de salida (por defecto docs/revision-cruzada/"
                                    "<nombre>/<fecha>/)")
    p.add_argument("--fecha", default=dt.date.today().isoformat())
    p.add_argument("--seco", action="store_true", help="no escribe ficheros, solo el resumen")
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(sys.argv[1:] if argv is None else argv)
    repo = os.path.abspath(os.path.expanduser(a.repo))
    if not os.path.isdir(repo):
        print(f"no existe: {repo}", file=sys.stderr)
        return 3
    nombre = a.nombre or os.path.basename(repo.rstrip("/"))
    puntos = {int(x) for x in re.findall(r"\d+", a.puntos)} if a.puntos else None
    commit = None
    tmp = None
    root = repo
    if a.ref:
        tmp = tempfile.TemporaryDirectory(prefix="comprobar-")
        commit = export_ref(repo, a.ref, tmp.name)
        root = tmp.name
        if os.path.isfile(os.path.join(repo, "comprobar.ignore")) and \
                not os.path.isfile(os.path.join(root, "comprobar.ignore")):
            with open(os.path.join(repo, "comprobar.ignore"), encoding="utf-8") as src, \
                    open(os.path.join(root, "comprobar.ignore"), "w", encoding="utf-8") as dst:
                dst.write(src.read())
    else:
        try:
            commit = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                                    capture_output=True, text=True, check=True).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            commit = None
    try:
        hallazgos, meta = run(root, a.sub or None, puntos)
    finally:
        if tmp is not None:
            tmp.cleanup()
    res = {"repo": repo, "nombre": nombre, "ref": a.ref, "commit": commit, "fecha": a.fecha,
           "ficheros": meta["ficheros"], "omitidos": meta["omitidos"], "total": len(hallazgos),
           "por_punto": resumen(hallazgos)}
    if not a.seco:
        salida = a.salida or os.path.join(DEFAULT_SALIDA, nombre, a.fecha)
        os.makedirs(salida, exist_ok=True)
        with open(os.path.join(salida, "comprobaciones.jsonl"), "w", encoding="utf-8") as fh:
            for h in hallazgos:
                fh.write(json.dumps(h, ensure_ascii=False) + "\n")
        with open(os.path.join(salida, "comprobaciones-resumen.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
        res["salida"] = salida
    print(json.dumps({k: v for k, v in res.items() if k != "omitidos"} |
                     {"omitidos": len(meta["omitidos"])}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
