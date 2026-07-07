#!/bin/bash
# ============================================================
#  iAmasters OS — Install Gate (SessionStart hook)
#  Bloquea respuestas del agente si la instalación está incompleta.
#
#  Output: JSON con additionalContext en stdout (formato Claude Code hooks).
#  Comportamiento:
#    - Si OS no instalado (no hay state) → inyecta mensaje "instalar primero"
#    - Si OS instalado parcial → inyecta mensaje "ejecuta /install --resume"
#    - Si OS completo → no hace nada (sale 0 sin output)
#
#  Este hook se registra en ~/.claude/settings.json en la sección
#  "hooks.SessionStart". Lo instala scripts/install.sh.
# ============================================================

set +e  # Nunca queremos que un hook roto bloquee la sesión

STATE_FILE="$HOME/.claude/skills/_install-state.json"

# Windows / Git Bash (MSYS): $STATE_FILE es /c/Users/... y node lo interpreta
# como C:\c\Users\... (inexistente) al interpolarlo dentro del string del heredoc.
# cygpath -m lo traduce a C:/Users/... (mixed), que node sí entiende.
# Sin esto, el hook caía al catch en CADA sesión con un falso "state corrupted".
if [[ -n "$MSYSTEM" ]] && command -v cygpath >/dev/null 2>&1; then
    WIN_STATE_FILE="$(cygpath -m "$STATE_FILE")"
else
    WIN_STATE_FILE="$STATE_FILE"
fi

# Si no tenemos node, no podemos parsear el state. Salimos silencioso.
# (Si node no está, Sinapsis tampoco funciona, así que el OS está roto de todos modos.)
if ! command -v node >/dev/null 2>&1; then
    exit 0
fi

# Caso 1: state file NO existe → OS no instalado en absoluto
if [ ! -f "$STATE_FILE" ]; then
    # Solo inyectamos el aviso si estamos dentro de un repo iamasters-os
    # (detectado por presencia de vendor/sinapsis/ + CLAUDE.md con mención)
    if [ -d "$PWD/vendor/sinapsis" ] && [ -f "$PWD/CLAUDE.md" ] && grep -q "iAmasters OS" "$PWD/CLAUDE.md" 2>/dev/null; then
        cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[INSTALL GATE] iAmasters OS detectado en este repo pero NO instalado (no existe ~/.claude/skills/_install-state.json).\n\nAntes de responder al usuario:\n1. Indícale claramente: 'iAmasters OS no está instalado. Necesito que ejecutes en terminal:\\n\\n   bash scripts/install.sh\\n\\nCuando termine, vuelve aquí y lo retomamos.'\n2. NO intentes crear archivos manualmente para simular la instalación.\n3. NO reportes que instalaste nada hasta que el state file exista y todas las fases required estén en 'done'.\n4. Si el usuario insiste en avanzar sin instalar, recuérdale que el sistema no funcionará correctamente."}}
EOF
    fi
    exit 0
fi

# Caso 2: state file existe → evaluamos completitud
node <<NODE_EOF
try {
  const fs = require('fs');
  const s = JSON.parse(fs.readFileSync('$WIN_STATE_FILE', 'utf8'));

  const phases = s.phases || {};
  const required = Object.entries(phases).filter(([k, v]) => v.required === true);
  const pending = required.filter(([k, v]) => v.status !== 'done');

  // Todo OK: no inyectamos nada
  if (pending.length === 0) {
    process.exit(0);
  }

  // Hay fases pendientes/fallidas: construir mensaje
  const total = required.length;
  const done = total - pending.length;
  const failed = pending.filter(([k, v]) => v.status === 'failed');
  const inProgress = pending.filter(([k, v]) => v.status === 'in-progress');
  const pendingOnly = pending.filter(([k, v]) => v.status === 'pending');

  let context = '[INSTALL GATE] iAmasters OS installation INCOMPLETE.\n';
  context += 'Required phases: ' + done + '/' + total + ' done.\n\n';

  if (failed.length > 0) {
    context += 'FAILED phases (requires fix):\n';
    failed.forEach(([k, v]) => {
      context += '  - ' + k + ' (owner: ' + (v.owner || '?') + ')\n';
    });
    context += '\n';
    if (s.errors && s.errors.length > 0) {
      const lastErr = s.errors[s.errors.length - 1];
      context += 'Last error: ' + lastErr.message + '\n\n';
    }
  }

  if (inProgress.length > 0) {
    context += 'IN-PROGRESS phases (resume from here):\n';
    inProgress.forEach(([k, v]) => {
      context += '  - ' + k + ' (owner: ' + (v.owner || '?') + ')';
      if (v.filesCreated && v.filesCreated.length > 0) {
        context += ' [partial: ' + v.filesCreated.length + ' files created]';
      }
      context += '\n';
    });
    context += '\n';
  }

  if (pendingOnly.length > 0) {
    context += 'PENDING phases:\n';
    pendingOnly.forEach(([k, v]) => {
      context += '  - ' + k + ' (owner: ' + (v.owner || '?') + ')\n';
    });
    context += '\n';
  }

  context += 'BEFORE responding to the user, you MUST:\n';
  context += '1. Acknowledge to the user that installation is incomplete (' + done + '/' + total + ' phases).\n';
  context += '2. Read ~/.claude/skills/_install-state.json with the Read tool to see exact state.\n';
  context += '3. Execute /install --resume to continue from where it stopped.\n';
  context += '4. If the FIRST pending phase is "context-files" or "operator-state", invoke the meta-onboarding-wizard skill directly.\n';
  context += '5. If the FIRST pending phase is "welcome-completed", invoke welcome-quick-win.\n';
  context += '6. NEVER report installation as complete unless the state file confirms all required phases are "done".\n';
  context += '7. NEVER create installation files manually to simulate progress — only the wizard and welcome-quick-win can mark phases done.\n\n';
  context += 'If the user says "stop" or "no quiero seguir":\n';
  context += '- Mark pausedBy="user" in the state file and pausedAtPhase=<current>.\n';
  context += '- Remind them they can resume anytime with /install --resume.\n';
  context += '- Do NOT pretend the installation is complete.\n';

  const out = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: context
    }
  };
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
} catch (e) {
  // State corrupto: avisamos al modelo en vez de crashar silencioso
  const out = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: '[INSTALL GATE] ~/.claude/skills/_install-state.json exists but is corrupted (' + e.message + '). Tell the user to run: bash scripts/install.sh --force-reinstall'
    }
  };
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
}
NODE_EOF

exit 0
