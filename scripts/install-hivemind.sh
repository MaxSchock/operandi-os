#!/bin/bash
# Project Hivemind setup phase. Invoked by install.sh after setup_os_layer.
# Responsibilities:
#   A) ALWAYS: render .mcp.json from .mcp.json.template (resolves absolute paths
#      to this machine). This is what makes the repo portable across users.
#   B) IF HIVEMIND_ENABLE=1: team setup — per-user env file (~/.claude/hivemind.env),
#      Python deps, pre-commit activation, SSH key bootstrap, summary Stop hook,
#      client repo clones, and update the install state machine.
#
# Safe to run repeatedly. Never hard-fails the installer (shared infra may not
# exist yet); it records progress in the state machine instead.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$HOME/.claude/skills/_install-state.json"
GLOBAL_SETTINGS="$HOME/.claude/settings.json"
ENV_FILE="$HOME/.claude/hivemind.env"
FORGEJO_HOST="${HIVEMIND_FORGEJO_HOST:-git.kisult.com}"
FORGEJO_SSH_PORT="${HIVEMIND_FORGEJO_SSH_PORT:-2222}"
FORGEJO_ORG="${HIVEMIND_FORGEJO_ORG:-KIsult}"

info() { echo ">>      $*"; }
ok()   { echo "[OK]    $*"; }
warn() { echo "[WARN]  $*"; }

# ---- A. Render .mcp.json (always) -----------------------------------------
# The rendered file carries NO user-specific values (credentials live in
# ~/.claude/hivemind.env, sourced by the hivemind-kb launcher), so overwriting
# it on every run is safe by construction.
render_mcp() {
    local tmpl="$REPO_ROOT/.mcp.json.template" out="$REPO_ROOT/.mcp.json"
    [ -f "$tmpl" ] || { warn ".mcp.json.template missing; skipping render."; return; }
    local rendered
    rendered="$(sed -e "s#__REPO_ROOT__#$REPO_ROOT#g" -e "s#__HOME__#$HOME#g" "$tmpl")"
    if [ "${HIVEMIND_ENABLE:-0}" != "1" ]; then
        # Solo/non-team install: drop the hivemind-kb block to avoid a failing
        # MCP server with no DSN. Uses python3 (a prereq).
        rendered="$(printf '%s' "$rendered" | python3 -c '
import json,sys
d=json.load(sys.stdin)
d.get("mcpServers",{}).pop("hivemind-kb",None)
print(json.dumps(d,indent=2,ensure_ascii=False))')"
    else
        # Team install: drop the evolution block (operator-machine tooling that
        # team members do not have and must not be pointed at).
        rendered="$(printf '%s' "$rendered" | python3 -c '
import json,sys
d=json.load(sys.stdin)
d.get("mcpServers",{}).pop("evolution",None)
print(json.dumps(d,indent=2,ensure_ascii=False))')"
    fi
    printf '%s\n' "$rendered" > "$out"
    ok "Rendered .mcp.json for this machine."
}

# ---- state helper ----------------------------------------------------------
set_hivemind_state() { # $1=status  $2=check_key(optional)  $3=true/false
    [ -f "$STATE_FILE" ] || return 0
    python3 - "$STATE_FILE" "$1" "${2:-}" "${3:-}" <<'PY'
import json,sys,datetime
f,status,key,val=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
try:
    d=json.load(open(f))
except Exception:
    sys.exit(0)
ph=d.get("phases",{}).get("hivemind-setup")
if ph is None: sys.exit(0)
if status: ph["status"]=status
ph["validatedAt"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
if key:
    ph.setdefault("checks",{})[key]= (val=="true")
d["lastUpdatedAt"]=ph["validatedAt"]
json.dump(d,open(f,"w"),indent=2,ensure_ascii=False)
PY
}

# ---- B. team setup ---------------------------------------------------------

# Per-user env file: single source of truth for the EOD pipeline and the
# hivemind-kb MCP launcher. Values (DSN + API keys) are handed to each employee
# by the admin (Max); this never invents or prints them.
ensure_env_file() {
    if [ -f "$ENV_FILE" ]; then
        chmod 600 "$ENV_FILE"
    else
        if [ -t 0 ]; then
            echo ""
            echo "  Dein Admin (Max) hat dir die Hivemind-Zugangsdaten geschickt."
            echo "  Füge sie hier ein (gespeichert in $ENV_FILE, nur für dich lesbar):"
            printf "  HIVEMIND_USER_ID (dein Kürzel, z.B. vorname.nachname): "
            read -r _uid
            printf "  HIVEMIND_DB_DSN (Verbindungs-String von Max): "
            read -r _dsn
            printf "  HIVEMIND_CLIENTS (deine Kunden, mit Leerzeichen, z.B. 'suritec jaeger'): "
            read -r _clients
            printf "  ANTHROPIC_API_KEY (KIsult-Key von Max): "
            read -rs _akey; echo ""
            printf "  OPENAI_API_KEY (KIsult-Key von Max): "
            read -rs _okey; echo ""
            umask 077
            cat > "$ENV_FILE" <<EOF
# Project Hivemind — per-user config. Handed out by the admin. chmod 600.
HIVEMIND_USER_ID="${_uid}"
HIVEMIND_DB_DSN="${_dsn}"
HIVEMIND_CLIENTS="${_clients}"
ANTHROPIC_API_KEY="${_akey}"
OPENAI_API_KEY="${_okey}"
EOF
            ok "Escrito $ENV_FILE"
        else
            umask 077
            cat > "$ENV_FILE" <<'EOF'
# Project Hivemind — per-user config. Rellena estos valores con los que te dio
# tu admin (Max) y vuelve a ejecutar: bash scripts/install.sh --resume
HIVEMIND_USER_ID=""
HIVEMIND_DB_DSN=""
HIVEMIND_CLIENTS=""
ANTHROPIC_API_KEY=""
OPENAI_API_KEY=""
EOF
            warn "Creado $ENV_FILE con valores vacíos (sesión no interactiva). Rellénalo y reejecuta."
        fi
    fi
    # Load it for the rest of this run (never echo values).
    set -a; . "$ENV_FILE"; set +a
    if [ -z "${HIVEMIND_USER_ID:-}" ] || [ -z "${HIVEMIND_DB_DSN:-}" ]; then
        warn "hivemind.env incompleto (falta HIVEMIND_USER_ID o HIVEMIND_DB_DSN). El indexado quedará en outbox local hasta rellenarlo."
        return 1
    fi
    ok "hivemind.env presente y completo."
    return 0
}

install_python_deps() {
    info "Instalando dependencias Python (mcp, psycopg, openai, anthropic)…"
    local pkgs=("mcp" "psycopg[binary]" "openai" "anthropic")
    if python3 -m pip install --user --quiet --disable-pip-version-check "${pkgs[@]}" 2>/dev/null; then
        ok "Dependencias Python instaladas."
    # PEP 668 (Ubuntu 23.04+/Debian 12 marks the system env as externally managed).
    # User-site install is still the least invasive option for a non-technical machine.
    elif python3 -m pip install --user --quiet --disable-pip-version-check \
        --break-system-packages "${pkgs[@]}" 2>/dev/null; then
        ok "Dependencias Python instaladas (user site, PEP 668 override)."
    else
        warn "pip install falló (¿sin red o sin pip?). Instala a mano: python3 -m pip install --user --break-system-packages mcp 'psycopg[binary]' openai anthropic"
    fi
}

enable_precommit() {
    if git -C "$REPO_ROOT" config core.hooksPath .githooks 2>/dev/null; then
        ok "Pre-commit hook activado (core.hooksPath=.githooks)."
    else
        warn "No pude activar core.hooksPath (¿no es un repo git?)."
    fi
}

bootstrap_ssh_key() {
    local user="${HIVEMIND_USER_ID:-$USER}"
    local key="$HOME/.ssh/kisult_hivemind_${user}"
    if [ -f "$key" ]; then
        ok "SSH key present: $key"
    else
        info "Generating SSH key for Forgejo: $key"
        mkdir -p "$HOME/.ssh"; chmod 700 "$HOME/.ssh"
        ssh-keygen -t ed25519 -f "$key" -N "" -C "hivemind-${user}" >/dev/null 2>&1 \
            && ok "Created $key" || { warn "ssh-keygen failed."; set_hivemind_state in-progress ssh_key_present false; return; }
    fi
    set_hivemind_state in-progress ssh_key_present true
    echo ""
    echo "  >>> Envía esta clave PÚBLICA a tu admin para darte acceso en Forgejo:"
    echo "  ----------------------------------------------------------------"
    cat "${key}.pub" 2>/dev/null | sed 's/^/  /'
    echo "  ----------------------------------------------------------------"
    echo ""
}

test_forgejo() {
    local user="${HIVEMIND_USER_ID:-$USER}"
    local key="$HOME/.ssh/kisult_hivemind_${user}"
    if timeout 6 ssh -p "$FORGEJO_SSH_PORT" -i "$key" -o IdentitiesOnly=yes \
        -o StrictHostKeyChecking=accept-new -o BatchMode=yes \
        "git@${FORGEJO_HOST}" 2>&1 | grep -qiE "authenticated|forgejo|gitea|successfully"; then
        ok "Forgejo SSH reachable and key recognized."
        set_hivemind_state in-progress forgejo_reachable true
        return 0
    fi
    warn "Forgejo not reachable yet (or key not authorized). Pídele acceso a tu admin y reintenta con: bash scripts/install-hivemind.sh"
    set_hivemind_state in-progress forgejo_reachable false
    return 1
}

# Clone the client repos this employee is assigned to (HIVEMIND_CLIENTS from
# hivemind.env) into clients/<X>/ (gitignored). Idempotent: skips existing.
clone_client_repos() {
    local user="${HIVEMIND_USER_ID:-$USER}"
    local key="$HOME/.ssh/kisult_hivemind_${user}"
    local clients="${HIVEMIND_CLIENTS:-}"
    [ -n "$clients" ] || { info "HIVEMIND_CLIENTS vacío; no hay repos que clonar."; return 0; }
    local all_ok=true c dest
    for c in $clients; do
        dest="$REPO_ROOT/clients/$c"
        if [ -d "$dest/.git" ]; then
            ok "Repo client-$c ya clonado."
        else
            info "Clonando client-$c…"
            if GIT_SSH_COMMAND="ssh -p $FORGEJO_SSH_PORT -i $key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
                git clone --quiet "git@${FORGEJO_HOST}:${FORGEJO_ORG}/client-${c}.git" "$dest" 2>/dev/null; then
                ok "Clonado clients/$c"
            else
                warn "No pude clonar client-$c (¿acceso aún no concedido?)."
                all_ok=false
                continue
            fi
        fi
        # Client repos get the same secret-blocking pre-commit as the OS repo.
        git -C "$dest" config core.hooksPath "$REPO_ROOT/.githooks" 2>/dev/null || true
    done
    if $all_ok; then
        set_hivemind_state in-progress repos_cloned true
    else
        set_hivemind_state in-progress repos_cloned false
    fi
}

register_summary_hook() {
    [ -f "$GLOBAL_SETTINGS" ] || { warn "Global settings.json not found; summary hook not registered."; return; }
    python3 - "$GLOBAL_SETTINGS" "$REPO_ROOT/scripts/chat-to-summary.sh" <<'PY'
import json,sys
f,cmd=sys.argv[1],sys.argv[2]
try:
    d=json.load(open(f))
except Exception:
    sys.exit(0)
hooks=d.setdefault("hooks",{})
stop=hooks.setdefault("Stop",[])
flat=json.dumps(stop)
if "chat-to-summary" not in flat:
    stop.append({"hooks":[{"type":"command","command":f"bash {cmd}","async":True,"timeout":60}]})
    json.dump(d,open(f,"w"),indent=2,ensure_ascii=False)
    print("registered")
PY
    ok "Summary Stop hook registered (idempotent)."
    set_hivemind_state in-progress summary_hook_registered true
}

# mcp_registered = the rendered .mcp.json exposes hivemind-kb AND the env file
# has a DSN for it to use. Checked for real, not inferred from the SSH key.
check_mcp_registered() {
    local out="$REPO_ROOT/.mcp.json"
    if [ -f "$out" ] && grep -q '"hivemind-kb"' "$out" \
        && [ -f "$ENV_FILE" ] && grep -qE '^HIVEMIND_DB_DSN="?.+' "$ENV_FILE" \
        && ! grep -qE '^HIVEMIND_DB_DSN=""' "$ENV_FILE"; then
        set_hivemind_state in-progress mcp_registered true
        return 0
    fi
    set_hivemind_state in-progress mcp_registered false
    return 1
}

# ---- run -------------------------------------------------------------------
render_mcp

if [ "${HIVEMIND_ENABLE:-0}" != "1" ]; then
    info "Hivemind team layer not enabled (HIVEMIND_ENABLE!=1). Solo install — fase hivemind-setup queda deferrable."
    set_hivemind_state deferred
    exit 0
fi

info "Configurando capa de equipo Project Hivemind…"
ensure_env_file || true
install_python_deps
enable_precommit
bootstrap_ssh_key
register_summary_hook
if test_forgejo; then
    clone_client_repos
fi
check_mcp_registered || true

if [ -f "$HOME/.ssh/kisult_hivemind_${HIVEMIND_USER_ID:-$USER}.pub" ] && check_mcp_registered; then
    ok "Hivemind base setup complete. Pendiente: que el admin autorice tu clave en Forgejo si aún no lo hizo."
else
    warn "Hivemind setup incompleto; reejecuta tras resolver lo marcado (bash scripts/install.sh --resume)."
fi
exit 0
