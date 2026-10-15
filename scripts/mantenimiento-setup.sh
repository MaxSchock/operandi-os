#!/usr/bin/env bash
# Weekly setup maintenance (phase 6 of the 2026-10-08 setup review).
# Deterministic part only: measure, prune rules with evidence, reindex, check the
# original repo. Leaves a short note that salud-os.py shows at the next session
# start; judgement calls (turning repeat offenders into guards, reviewing instinct
# proposals) stay with that session. Writes only to memory, rules and docs.
set -uo pipefail
REPO=/home/max/iamasters-os
NOTA="$HOME/.claude/session-env/mantenimiento-pendiente.txt"
LOG="$HOME/.claude/session-env/mantenimiento-setup.log"
cd "$REPO" || exit 1
{
  echo "== $(date '+%F %T')"
  python3 scripts/medir-setup.py --dias 60
  INFORME=$(python3 scripts/medir-setup.py)
  CORR=$(python3 scripts/medir-correcciones.py 2>&1 | grep -m1 "turnos de Max son correcciones")
  PODA=$(python3 "$HOME/.claude/hooks/podar-reglas.py" --aplicar 2>&1)
  # Cambios al sistema registrados en docs/cambios-medidos.jsonl: mide los vencidos y deja la tabla en el informe.
  CAMBIOS=$(python3 scripts/cambios-medidos.py check 2>&1)
  if [ -f "$INFORME" ] && ! grep -q "^## Cambios medidos abiertos" "$INFORME"; then
    python3 scripts/cambios-medidos.py tabla >> "$INFORME" 2>&1
  fi
  python3 "$HOME/.claude/hooks/indexar-reglas.py"
  git fetch --quiet upstream 2>/dev/null
  NUEVOS=$(git rev-list --count "$(cat .claude/.original-aplicado 2>/dev/null)..upstream/main" 2>/dev/null || echo 0)
  COPIAS=$(git status --short --ignored 2>/dev/null | grep -cE '\.bak-|\.backup-')
  {
    echo "Mantenimiento del setup del $(date +%F). Informe: ${INFORME#$REPO/}"
    echo "- Poda de reglas: $(echo "$PODA" | head -1)$(echo "$PODA" | grep -c '^archivadas' | sed 's/^1$/ (aplicada)/;s/^0$//')"
    python3 - <<'PY'
import json, os
d = json.load(open(os.path.expanduser("~/.claude/session-env/medicion-setup-28d.json")))
print(f"- Texto metido por hooks en 28 dias: {sum(d['kb_hooks'].values())/1024:.1f} MB "
      f"({', '.join(f'{k} {v} KB' for k, v in sorted(d['kb_hooks'].items(), key=lambda x: -x[1])[:3])})")
t = d.get("timeouts", {})
if t:
    print(f"- Hooks cortados por tiempo: {', '.join(f'{k} {v}' for k, v in sorted(t.items(), key=lambda x: -x[1])[:4])}")
usadas = set(d["skills"]) | set(d["comandos"])
print(f"- Skills y comandos usados: {len(usadas)} ({', '.join(sorted(usadas)[:8])})")
PY
    [ -n "$CORR" ] && echo "- Correcciones de Max esta semana (Jev): ${CORR#- }"
    [ -n "$CAMBIOS" ] && [ "$CAMBIOS" != "ninguna revision vencida" ] && echo "- Cambios medidos con revision vencida: informe docs/medicion-setup/cambios-$(date +%F).md (cierra cada uno con scripts/cambios-medidos.py close)."
    [ "${NUEVOS:-0}" -gt 0 ] && echo "- El OS original tiene $NUEVOS commits nuevos."
    [ "${COPIAS:-0}" -gt 20 ] && echo "- Hay $COPIAS copias .bak sueltas en el repo: moverlas a ~/.claude/backups/."
    echo "Lee el informe, compara con el anterior de docs/medicion-setup/ y actua sobre lo que haya empeorado. Borra esta nota al terminar: $NOTA"
  } > "$NOTA"
  cat "$NOTA"
} >> "$LOG" 2>&1
