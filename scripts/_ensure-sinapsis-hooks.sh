#!/bin/bash
# ============================================================
#  _ensure-sinapsis-hooks.sh
#  Deep-merge IDEMPOTENTE de los hooks de Sinapsis en el
#  settings.json del operador, preservando permisos/config/hooks
#  previos. Re-ejecutar = no-op.
#
#  Lo usan:
#   - install.sh  → tras instalar Sinapsis (el instalador vendored
#     NO registra hooks si settings.json ya existía).
#   - update.sh   → para que /actualiza REPARE instalaciones viejas
#     cuyos hooks nunca se cablearon (motor de aprendizaje inerte).
#
#  Uso: _ensure-sinapsis-hooks.sh [TEMPLATE_JSON] [SETTINGS_JSON]
#   TEMPLATE_JSON  por defecto: ../vendor/sinapsis/core/settings.template.json
#   SETTINGS_JSON  por defecto: ~/.claude/settings.json
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="${1:-$REPO_ROOT/vendor/sinapsis/core/settings.template.json}"
SETTINGS="${2:-$HOME/.claude/settings.json}"

if [ ! -f "$TEMPLATE" ]; then
    echo "[ensure-hooks] no encontrado $TEMPLATE" >&2
    exit 2
fi
mkdir -p "$(dirname "$SETTINGS")"

# Windows / Git Bash (MSYS): cygpath -m para que node/python entiendan la ruta.
if [[ -n "$MSYSTEM" ]] && command -v cygpath >/dev/null 2>&1; then
    TEMPLATE="$(cygpath -m "$TEMPLATE")"
    SETTINGS="$(cygpath -m "$SETTINGS")"
fi

# Runtime JSON: en MSYS preferimos python (node malinterpreta rutas POSIX).
RT=""
if [[ -n "$MSYSTEM" ]]; then
    if command -v python3 >/dev/null 2>&1; then RT=python3
    elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "Python 3"; then RT=python
    elif command -v node >/dev/null 2>&1; then RT=node
    fi
elif command -v node >/dev/null 2>&1; then RT=node
elif command -v python3 >/dev/null 2>&1; then RT=python3
elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "Python 3"; then RT=python
fi
if [ -z "$RT" ]; then
    echo "[ensure-hooks] ni node ni Python 3 disponibles" >&2
    exit 3
fi

case "$RT" in
    node)
        node -e '
const fs = require("fs"), path = require("path");
const tplPath = process.argv[1], setPath = process.argv[2];
function strip(o){ if(Array.isArray(o)) return o.map(strip); if(o && typeof o==="object"){ const r={}; for(const [k,v] of Object.entries(o)){ if(k.startsWith("_")) continue; r[k]=strip(v);} return r;} return o; }
const tpl = strip(JSON.parse(fs.readFileSync(tplPath, "utf8")));
let cur = {};
if (fs.existsSync(setPath)) { try { cur = JSON.parse(fs.readFileSync(setPath, "utf8")); } catch(e){ console.error("settings.json existe pero no es JSON parseable"); process.exit(4); } }
cur.hooks = (cur.hooks && typeof cur.hooks === "object") ? cur.hooks : {};
const cmdOf = h => (h && typeof h === "object" && h.command) ? h.command : JSON.stringify(h);
for (const [event, groups] of Object.entries(tpl.hooks || {})) {
  if (!Array.isArray(cur.hooks[event])) cur.hooks[event] = [];
  for (const g of groups) {
    let dst = cur.hooks[event].find(x => (x.matcher || "") === (g.matcher || ""));
    if (!dst) { cur.hooks[event].push(JSON.parse(JSON.stringify(g))); continue; }
    if (!Array.isArray(dst.hooks)) dst.hooks = [];
    const seen = new Set(dst.hooks.map(cmdOf));
    for (const hk of (g.hooks || [])) { if (!seen.has(cmdOf(hk))) { dst.hooks.push(hk); seen.add(cmdOf(hk)); } }
  }
}
fs.mkdirSync(path.dirname(setPath), { recursive: true });
fs.writeFileSync(setPath, JSON.stringify(cur, null, 2) + "\n");
' "$TEMPLATE" "$SETTINGS"
        ;;
    python3|python)
        "$RT" - "$TEMPLATE" "$SETTINGS" <<'PYEOF'
import json, os, sys
tplPath, setPath = sys.argv[1], sys.argv[2]
def strip(o):
    if isinstance(o, list): return [strip(x) for x in o]
    if isinstance(o, dict): return {k: strip(v) for k, v in o.items() if not k.startswith('_')}
    return o
with open(tplPath) as fh:
    tpl = strip(json.load(fh))
cur = {}
if os.path.exists(setPath):
    try:
        with open(setPath) as fh:
            cur = json.load(fh)
    except Exception:
        sys.stderr.write('settings.json existe pero no es JSON parseable\n'); sys.exit(4)
if not isinstance(cur.get('hooks'), dict):
    cur['hooks'] = {}
def cmd_of(h):
    return h['command'] if isinstance(h, dict) and 'command' in h else json.dumps(h, sort_keys=True)
for event, groups in (tpl.get('hooks') or {}).items():
    if not isinstance(cur['hooks'].get(event), list):
        cur['hooks'][event] = []
    for g in groups:
        dst = next((x for x in cur['hooks'][event] if x.get('matcher', '') == g.get('matcher', '')), None)
        if dst is None:
            cur['hooks'][event].append(json.loads(json.dumps(g))); continue
        if not isinstance(dst.get('hooks'), list):
            dst['hooks'] = []
        seen = set(cmd_of(h) for h in dst['hooks'])
        for hk in g.get('hooks', []):
            if cmd_of(hk) not in seen:
                dst['hooks'].append(hk); seen.add(cmd_of(hk))
os.makedirs(os.path.dirname(setPath), exist_ok=True)
with open(setPath, 'w') as fh:
    json.dump(cur, fh, indent=2); fh.write('\n')
PYEOF
        ;;
esac
