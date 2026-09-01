# Current priorities

> Qué tengo activo ahora. Cambia frecuentemente — actualizar cuando convenga.

## Optimización del setup Claude Code 2026-06-12/13 (DONE)

Auditoría completa + repaso de coherencia de los MD. Lo cerrado:
- **WSL-first**: `CLAUDE.md`, `clients.private.md` y credenciales n8n como archivos reales en WSL, symlinks inversos en `/mnt/c`.
- **n8n vía REST** (sin n8n-mcp): skill `automation-n8n-builder` v2.0.0 + `docs/tech-stack-decision.md` (árbol de decisión + backlog de salidas de n8n).
- **Memoria**: MEMORY.md compactado, drafts de instincts procesados (`/evolve`), settings.json sin permisos fantasma, logs Sinapsis rotados.
- **Respaldo con historial**: repo privado `MaxSchock/sinapsis-state` (snapshot en hook Stop) + rsync al VPS como secundario.

## Migración global 2026-05-21 (DONE)

Consolidé toda la infraestructura Claude en estructura limpia siguiendo el orden iAmasters OS:
- **CLAUDE.md global** consolidado (identidad, comunicación, autonomía, stack, paths críticos, secretos, gotchas).
- **`clients/<empresa>/`** para Operandi, KIsult, Falkenlead, con sub-clientes anidados.
- **n8n-audits** migrado de Windows a `clients/operandi/_shared/n8n-audits/`.
- **Memoria limpia**: solo `MEMORY.md` como índice de dónde vive cada cosa ahora.
- **6 instincts nuevos** en Sinapsis para gotchas n8n (PUT settings, langchain prefix, sheets read, executeWorkflow loop, skip-branch self-heal, backfill traps).
- **Backups** completos en `~/.claude/backups/memory-pre-migration-20260521-091057/`.

## En operación continua

### Daily digest a las 09:00 CEST
n8n envía digest diario consolidado de comerciales/operaciones. Desde 2026-05-15 va solo a Max, no a clientes (v4 Max-only activo, v3 desactivado). Sección comercial primero.

### Inbox de errores n8n
Tabla `n8n_errors_inbox` en Supabase `xepotlbqlwmriwievyvc`. Mirroriza cada error de workflow. Al inicio de cada sesión Claude revisa unresolved.

### Modelo operativo Strategist (Operandi)
- Tier 1+2: autonomía total, sin pedir permiso.
- Tier 3: approval por WhatsApp.
- Toda decisión comercial pasa siempre por Zayd (`32472545977`).
- Cliente final solo recibe si `notify_client_enabled` por cliente.

## Construcción de stack agéntico

### Capas avanzadas de Claude Code
Siguiendo el curso de Next Gen AI Institute. Status:
- ✓ CLAUDE.md global + por proyecto (iamasters-os).
- ✓ Skills/comandos personalizados (vía iAmasters OS, 27 skills core + 1 opcional).
- ✓ Hooks (Sinapsis + OS + snapshot de memoria a git en el Stop).
- ✓ MCPs conectados (verificado 2026-07-20): **config** → `posthog` (global `~/.claude.json`, HTTP), `evolution` (WhatsApp, project `.mcp.json`, stdio, instancia "Max Privat" open); **conectores claude.ai** (OAuth cuenta personal, viven en sesión) → Supabase, Gmail, Google Calendar, Google Drive, Miro (team con boards Operandi). Disponibles SIN autenticar: Microsoft 365, Claude MCP Test. Nota: los conectores claude.ai se autentican por separado en Claude Code (`/mcp`), NO se heredan de claude.ai web. Pendiente: Vercel. **n8n-mcp descartado** (se opera vía REST).
- ✓ Versionado git en uso: repos personales `MaxSchock/*` + `sinapsis-state` (memoria).
- ✓ Subagentes para tareas paralelas (auditoría de esta sesión usó 3 en paralelo).
- Projects en claude.ai uno por iniciativa interna (pendiente).

### iAmasters OS instalado 2026-05-16
Sinapsis v4.1 + capa OS. Working dir canónico desde 2026-05-21.

## Memoria externa — Obsidian segundo cerebro (live desde 2026-06-03)

- **App**: Obsidian v1.12.7 Linux AppImage en `~/Applications/Obsidian.AppImage` + desktop entry WSLg.
- **Vault**: `~/iamasters-os/_wiki/` como **sub-repo git independiente** (no trackeado por el repo principal, está en su `.gitignore`).
- **Patrón Karpathy** (wiki vivo, no RAG): páginas madre sintetizadas + wikilinks bidireccionales. 3 capas (fuentes inmutables in-place / wiki vivo en `_wiki/` / schema humano en `_wiki/_schema.md`).
- **Plugins comunidad instalados**: `obsidian-git` (auto-commit + auto-push), `dataview`, `templater-obsidian`. Smart Connections opt-in (pendiente API key OpenAI).
- **Auto-commit**: cada 15 min, mensaje `wiki: auto-save <fecha>`. **Auto-push**: cada 15 min tras commit, a `git@github.com:MaxSchock/iamasters-vault.git` (privado).
- **Historial de chats al vault**: 46 sesiones JSONL convertidas a `_wiki/raw/chat-history/*.md`. Hook `Stop` en `~/.claude/settings.json` añade nuevas sesiones automáticamente.
- **MCP de Obsidian**: NO instalado (el patrón no lo necesita; Claude Code edita los `.md` directamente vía filesystem).
- **Cómo usar**: 3 prompts canónicos en `_wiki/_prompts.md` (Ingest, Query, Lint).

## Pendientes operativos

### Inbox sin contexto (revisar con Max)
- 2026-06-05 — Reel IG [DZJFulnphNt](https://www.instagram.com/reel/DZJFulnphNt/) de gigaqian (27K plays). Anuncia **Hermes Desktop** (Nous Research, Electron+React) + truco **NVIDIA NIM** para free API calls a modelos frontier. Transcript completo en `/tmp/ig-reel-transcript.txt`. **Decisión pendiente**: ¿probar pipeline NIM+Hermes como sandbox para prototipar agentes antes de strategist, o descartar? No veo migración del stack productivo (n8n + strategist + Claude API).

### Operandi
- Revisar el 2026-05-22 si Belgo Step 4 repite `missing_attendee_provider_id` para decidir si añadir IF guard targeted.
- Backfill de 38 filas históricas de Kaps Step 3 1st-degree (pendiente decisión Max).
- Step 2 backlog liquidation Helexia 333 prospects ~15 días al ritmo actual.
- helexia recovery: 3 prospects en "DONE without message" state (Lieven Pieters, Philippe Jans, Astrid Van Langenhoven).

### Compliance Gmail OAuth (2026-05-16)
1. Verificar DPA disponible con cuenta Claude actual.
2. Article 30 record con Anthropic.
3. Privacy policy update (Falkenlead, KIsult, Operandi).
4. Revisar contrato ULB para subprocesadores.

### Limpieza migración (pendiente confirmación Max)
- Huérfanos Windows `~/.claude/projects/-mnt-c-Users-PC*`: backup tar.gz hecho 2026-06-12 (`orphan-windows-projects-*.tar.gz`), borrado **denegado por Max**, sigue en disco si se quiere recuperar.
- `clients/pierre/` confirmado **Operandi** (movido a `clients/operandi/clients/pierre/`). Resuelto.
- Decidir si migrar permisos universales de project `settings.local.json` a global `settings.json`.
