# iAmasters OS — CLAUDE.md (project root)

> Sistema operativo agéntico para operadores de IA.
> Sinapsis (engine) + capa OS (brand context, agent context, skills curadas, multi-cliente). En esta máquina corre Sinapsis 4.1; la 4.6.1 de `vendor/sinapsis/` es solo para instalaciones nuevas.

---

## ⛔ INSTALLATION GATE — LEER ANTES QUE NADA

Antes de responder al primer mensaje del usuario en este repo, **debes** comprobar si la instalación está completa.

**Fuente de verdad**: `~/.claude/skills/_install-state.json` (state machine persistente, v0.6+).

**Comprobación obligatoria** (en este orden):

1. **¿Existe el state file?**
   - Si NO existe → la instalación técnica nunca corrió. **Ofrécete a instalarlo tú** (es lo más cómodo: el usuario no suele usar terminal):
     > "iAmasters OS aún no está instalado. Te lo instalo yo ahora mismo (Sinapsis + capa OS, ~30s). ¿Le doy?"
     - Con su OK, ejecuta `bash scripts/install.sh` con la tool `Bash` (ya está permitido en `.claude/settings.json`, no pide permiso). En Windows corre igual vía Git Bash, que Claude Code ya requiere; si `bash` no está disponible, pídele instalar Git Bash.
     - Parsea la salida estructurada (`[OK]`/`[SKIP]`/`[WARN]`/`[ERROR]`). Si hay `[ERROR]`, diagnostica y explícalo en castellano.
     - Cuando termine bien, continúa con `/install` para las fases conversacionales.
   - NO crees archivos manualmente para simular instalación. NO marques nada como instalado a mano — de eso se encarga `install.sh`.

2. **Si existe, ¿todas las fases `required: true` están en `status: "done"`?**
   - Si NO → la instalación está incompleta. Invoca el comando `/install` (o el wizard directamente, según la fase pendiente).
   - **NO respondas a otras peticiones del usuario hasta cerrar la instalación.**

3. **El hook SessionStart (`_install-gate.sh`) ya inyecta este aviso automáticamente cuando aplica.** Esta sección es tu *backup* por si el hook falla, no la fuente principal.

**Lo que NUNCA haces durante una instalación incompleta**:
- ❌ Reportar "todo instalado" cuando el state dice lo contrario
- ❌ Crear archivos `.json` o `.md` manualmente para "completar" fases
- ❌ Marcar fases como `done` sin que la validación profunda lo confirme
- ❌ Avanzar a tareas del usuario si quedan fases `required` sin completar

**Si el usuario dice "para" / "ya no quiero seguir":**
- Marca `pausedBy: "user"` en el state con la fase actual
- Despídete: "Cuando vuelvas, `/install --resume` retoma desde aquí. Lo guardado está guardado."
- NO insistas. NO reportes la instalación como completa.

**Si dudas del estado**: ejecuta `/install-status` para ver el dashboard sin tocar nada.

---

## Session Entry — EXECUTE ON FIRST MESSAGE OF EVERY SESSION

(Una vez que el INSTALLATION GATE de arriba ha pasado.)

### Paths absolutos (relativos a este repo)
- **Skills del OS**: `.claude/skills/`
- **Commands del OS**: `.claude/commands/`
- **Brand context**: `brand-context/` (voice, positioning, ICP, assets)
- **Agent context sectorizado**: `context/` (working-memory.md, me.md, work.md, team.md, current-priorities.md, goals.md, decisions-log.md, learnings.md, soul.md)
- **Proyectos**: `projects/` (`projects/briefs/<nombre>/`, `projects/welcome/`, `projects/seis-sombreros/`, `projects/metodo-ias/`, `projects/visual/`)
- **Clientes**: `clients/<nombre>/` (con `clients/_templates/` para nuevos)
- **Docs operativos**: `docs/`
- **Scripts del installer**: `scripts/install.sh`, `scripts/_install-gate.sh`, `scripts/_install-state.template.json`
- **Vendored**: `vendor/sinapsis/` (engine), `vendor/cognito/` (Sistema Operativo de Pensamiento de Luis Pitik), `vendor/arnes/` (skill opt-in para arrancar proyectos software, concepto fs-scaffold de Fernando Montero)

### Paths Sinapsis (engine global del operador)
- **Skills root global**: `~/.claude/skills/` (Sinapsis instalado por install.sh)
- **Operator state**: `~/.claude/skills/_operator-state.json`
- **Install state (v0.6+)**: `~/.claude/skills/_install-state.json` ← fuente de verdad de la instalación
- **Install gate hook**: `~/.claude/skills/_install-gate.sh` (SessionStart hook)
- **Instincts**: `~/.claude/skills/_instincts-index.json`
- **Daily summaries**: `~/.claude/skills/_daily-summaries/`
- **Catalog**: `~/.claude/skills/_catalog.json`

### Arranque (post-gate)

El hook de arranque (`~/.claude/hooks/salud-os.py`) ya pone delante la memoria de trabajo (`context/working-memory.md`), los planes sin terminar y los avisos de mantenimiento. No hay más lectura obligatoria en el primer mensaje.

- Si hay planes abiertos, recuérdaselos al operador con la fase en la que están y lo que falta de su parte, y sigue ejecutando el que toque hasta la última fase.
- El ritual completo (canales, sesiones abiertas, errores de n8n, resumen de ayer, `context/` sectorizado, `decisions-log.md`, briefs con `status: active`) lo hace `/start-here` cuando el operador lo pide.

---

## Actualizar el OS

Cuando el usuario diga **"actualízate"**, **"actualiza el OS"**, **"actualízate a la última versión"**, **"tráete los cambios nuevos"**, **"ponme la última versión de iAmasters OS"** o **"update"** → ejecuta el comando `/actualiza`:

```bash
git pull --ff-only
bash scripts/update.sh
```

`update.sh` preserva SIEMPRE lo del operador (skills propias, `brand-context/`, `context/`, `projects/`, `clients/`, `loops/`); solo actualiza el código del OS, las skills curadas y Sinapsis vendored. Si `git pull` falla por cambios locales, NO fuerces: explica qué tiene modificado y pregunta. Al terminar, resume lo nuevo desde el `CHANGELOG.md`.

Cuando lo lanzas tú (sin terminal del usuario), `update.sh` detecta que no hay TTY y entra en modo no-interactivo: nunca pregunta, mantiene la versión local ante cualquier conflicto y lista al final los "Pendientes de decisión". Resuélvelos conversacionalmente con el usuario (enséñale qué cambia cada archivo y aplica lo que decida con `git checkout origin/<branch> -- <archivo>`).

**Si tras actualizar algo se rompe** → `/restaura` (rollback completo al estado anterior: código + datos). Cada update deja backup automático en `.backup/`.

---

## Sobre el sistema

### Sinapsis (engine de memoria)
El repo lo trae vendored en `vendor/sinapsis/` para instalaciones nuevas. **En esta máquina está apagado desde el 08-10-2026** (su autor lo abandonó el 21-08-2026): sus hooks no corren y sus datos siguen intactos en `~/.claude/skills/`. Las reglas viven en el activador (`~/.claude/hooks/activador-reglas.py`, memoria en `~/.claude/projects/-home-max-iamasters-os/memory/`) y en los guards. Siguen en uso `/eod`, `/dream` y `/session-end`.

### Capa OS (este repo)
Lo que aporta este repo encima de Sinapsis:

**Brand Context (`brand-context/`)** — estática:
- Voice profile + 3 registros (A formal / B divulgativo / C cercano)
- Positioning, ICP, brand assets

**Agent Context (`context/`)** — dinámica:
- `working-memory.md` — **scratchpad de trabajo** (hilos activos / notas de entorno / decisiones pendientes). Se inyecta al inicio y se mantiene al cierre. Tope ~2.500 car.
- `soul.md` — personalidad del agente (cómo respondes)
- `me.md`, `work.md`, `team.md`, `current-priorities.md`, `goals.md`
- `learnings.md`, `decisions-log.md`

**Memoria de trabajo (memo manual)**: cuando el operador diga *"recuerda esto"*, *"apunta que"*, *"nota que"* o *"para la próxima"*, escribe el ítem en la sección que corresponda de `context/working-memory.md` (Hilos activos / Notas de entorno / Decisiones pendientes), con dedup y respetando el tope. Visible de inmediato en esta sesión; en sesiones futuras se carga al inicio.

**Skills curadas** — modelo Core + Biblioteca: 17 core en `.claude/skills/` (siempre cargadas) + 20 en `skills-library/` instalables con `/skills` (ver registry abajo).

**Niveles de proyecto**:
1. **Single task** — pregunta directa. Output a `projects/<skill-name>/<fecha>-<titulo>/`.
2. **Planned project** — scoping conversation. Output a `projects/briefs/<nombre>/`.
3. **GSD project** — multi-fase. `.planning/` en cliente o raíz.

**Multi-cliente**:
- `clients/<nombre>/` con su propio brand-context, context, projects
- Templates en `clients/_templates/` para 4 verticales

---

## Skills registry (v0.11.2)

Modelo **Core + Biblioteca**. Todas las skills instaladas viven a UN nivel, en `.claude/skills/<nombre>/SKILL.md` (es lo único que Claude Code indexa; anidadas por categoría no cargan). Las instaladas ya aparecen con su descripción en la lista de skills de cada sesión: no se repiten aquí.

- **Core (17)**: las necesita el OS. Sistema: `meta-skill-creator`, `meta-onboarding-wizard`, `meta-deep-dive`, `meta-start-here`, `meta-wrap-up`, `welcome-quick-win`, `decisions-log`, `health-check`, `find-skills`, `recuerda`. Marca y motor: `marketing-brand-voice`, `marketing-positioning`, `marketing-icp`, `automation-loop-engine`, `tool-firecrawl-scraper`, `tool-humanizer`, `tool-output-verifier`.
- **Propias del operador (5)**: no vienen del original, sobreviven a `/actualiza` y no se quitan con `/skills remove`: `content-engine`, `canvas-design`, `frontend-design`, `video-escena-por-escena`, `marketing-google-ads-auditor`. `mcp-builder` y `skill-creator` se archivaron el 08-10-2026 en `.claude/skills/_archived/` por ser copia de las del plugin de Anthropic (`anthropic-skills:mcp-builder`, `anthropic-skills:skill-creator`), que es la que se usa.
- **Biblioteca** en `skills-library/` (cero coste de contexto hasta instalarlas). Instalar: `bash scripts/skills.sh add <nombre>` · quitar: `remove` · catálogo en vivo: `bash scripts/skills.sh list`. No instaladas hoy (10): `arnes`, `cognito`, `marketing-meta-ads-analyzer`, `strategy-investigacion-profunda`, `strategy-stack-recommender`, `tool-quality-gate`, `tool-seguridad-ia`, `tool-transcribe-social`, `tool-web-legal-audit`, `tool-web-security-audit`.

**Routing por intención**: si el usuario pide algo que resuelve una skill de la biblioteca que no tiene instalada, NO digas que no puedes: ofrece instalarla ("Eso lo hace la skill `<nombre>`. ¿La instalo?").

### Plugins Anthropic (instalación vía marketplace)

| Skill | Cómo activar |
|---|---|
| `docx`, `xlsx`, `pdf`, `pptx` | `/plugin install anthropic-skills` |

### Slash commands

`/instala` · `/install` · `/install-status` · `/start-here` · `/wrap-up` · `/doctor` · `/actualiza` · `/restaura` · `/backup` · `/skills` · `/add-client` · `/install-skill` · `/install-mcp` · `/aprende` · `/deep-dive` · `/recuerda` · `/loops` · `/evalua-loop`

`/instala` es el punto de entrada **sin terminal**: se dispara con "instala esto" / "install this" y ejecuta el installer por ti (Mac y Windows con Git Bash). `/install` e `/install-status` gestionan/consultan la instalación por fases una vez arrancada.

### Capa 2 — skills externas

Ver [`docs/skills-recommended.md`](docs/skills-recommended.md) para skills de terceros instalables vía `/install-skill <github-url>` (con validación previa). Las skills curadas del OS viven en la biblioteca (`/skills`), no aquí.

---

## Niveles de proyecto — heartbeat

Al iniciar cada sesión (post-gate), comprueba `projects/briefs/*/brief.md`:
- Si hay `status: active`, recuérdale qué dejó abierto.
- Si hay un `.planning/` en raíz o cliente, indica que hay un GSD en marcha.
- Si terminó algo (`status: done`), pregunta si archivamos.

---

## Personalizar skills sin perder updates — SKILL.local.md

Si el operador quiere cambiar el comportamiento de una skill curada ("a partir de ahora esta skill siempre X"), NO edites su `SKILL.md` (un update lo pisaría o generaría conflicto). En su lugar:

1. Crea/edita `SKILL.local.md` junto al `SKILL.md` de esa skill.
2. Formato: lista de reglas fechadas, append-only:
   ```markdown
   ## Reglas del operador
   - 2026-06-12: siempre incluir CTA al final de los emails
   ```
3. **Al invocar cualquier skill**: si existe `SKILL.local.md` en su carpeta, léelo DESPUÉS del `SKILL.md`. Sus reglas mandan sobre lo que diga la skill base.

`SKILL.local.md` está gitignored: sobrevive a `/actualiza` sin conflictos y nunca se sube al repo.

---

## Cómo registrar skills nuevas (auto)

Cuando se añade una skill nueva en `.claude/skills/<nombre>/`:
- `/start-here` la detecta y registra en catalog
- `/wrap-up` actualiza el registry de este CLAUDE.md
- El comando `/install-skill <github-url>` la valida antes de añadirla

---

## Permisos (recordatorio)

`.claude/settings.json` viene con permisos seguros por defecto:
- ✅ Read files, dev server, git operations, edit files dentro del repo
- ❌ Install packages globalmente, delete files, leer `.env`

Si necesitas más permisos: `claude --dangerously-skip-permissions` (puntual) o edita `settings.json`.

---

## Idioma

- **Operativa con el usuario**: castellano por defecto
- **Comentarios técnicos en código**: inglés
- **Commits**: conventional commits en inglés
- **Outputs entregables al cliente**: idioma del cliente (detectar en brand-context)

---

## Convenciones del repo

- Carpetas en kebab-case (`brand-context`, `clients`, `projects`)
- Archivos markdown en kebab-case
- Skills en kebab-case con prefijo de categoría: `marketing-brand-voice`, `tool-humanizer`, etc.
- Outputs por fecha: `YYYY-MM-DD-titulo-corto/`
- Variables de entorno en `.env`

---

## Cuándo NO usar el OS

Casos donde mejor abre Claude Code en otro lado:
- Editar el código de tu propia app
- Bug puntual sin necesidad de brand context
- Sesión exploratoria que no quieres que ensucie tu memory

Para casos donde sí:
- Crear contenido (LinkedIn, X, blog, email, video script)
- Trabajar con un cliente (entras en `clients/<nombre>/`)
- Análisis estratégico
- Generar deliverables con voice consistente

---

## Soporte y comunidad

- Issues: https://github.com/iamasters-academy/iamasters-os/issues
- Sinapsis upstream: https://github.com/Luispitik/sinapsis
- Schema doc del install gate: [`docs/install-state-schema.md`](docs/install-state-schema.md)
