# Revisión a conciencia del setup de Claude Code

Estado: propuesto 08-10-2026, revisado el mismo día con datos (v2). Sin empezar. Una sesión por fase; cada fase deja aquí sus hallazgos, un commit y una línea en el ledger (`interno,iamasters-os`).

## Por qué

Punto de partida medido el 08-10:

| Pieza | Cifra |
|---|---|
| Texto que se carga en cada sesión | ~61 KB (CLAUDE.md global 26, CLAUDE.md del repo 17, MEMORY.md 17) más la lista de skills |
| Reglas en el índice del activador | 341 (67 «irrompibles», 33 fusionadas); MEMORY.md dice 197 |
| Sistemas de reglas en paralelo | 3: activador, instincts de Sinapsis (52) y passive rules (31), más 117 propuestas de instinct sin revisar |
| Hooks | 23 órdenes; 11 corren antes de cada comando de terminal |
| Skills | 34 del OS (ninguna cargada, ver 0a), 6 globales, 17+17 comandos, plugin de Anthropic; duplicadas: canvas-design, mcp-builder, skill-creator, code-review |
| Lectura obligatoria al arrancar | ~10 ficheros y una consulta a Supabase; en la sesión del 08-10 no se hizo y nada lo detectó |
| Basura en el repo | 133 copias `context/working-memory.md.bak-*` sin seguimiento; `backups/` de Linus dentro del repo del OS |

Síntomas: la regla «Codex antes de desplegar» lleva 7 reincidencias; el indexador de reglas no refresca las editadas (corregido a mano el 08-10 para una); el CLAUDE.md del repo dice Sinapsis 4.6.1 y corre la 4.1.

## Criterio de éxito

Restar, no añadir. Al terminar: menos texto cargado por sesión, menos reglas, un solo sistema de reglas, y las reglas que se incumplen convertidas en comprobaciones automáticas. Se mide antes y después con la tabla de arriba.

## Qué no se toca

Datos del operador: `clients/`, `context/` (salvo poda acordada), `brand-context/`, `projects/`, memoria y session-logs, ficheros de datos de Sinapsis (`_operator-state.json`, `_instincts-index.json`, `_passive-rules.json`, observaciones). Copia con fecha antes de cualquier cambio en lo demás.

## Fases

**0a. Ponerse al día con el original.** Comprobado el 08-10: local en v0.10.1 (12-06), original `iamasters-academy/iamasters-os` en v0.11.2 (19-08), ya traído con `git fetch upstream`.

- Lo que importa de verdad: la v0.11.0 arregla que Claude Code solo descubre skills a un nivel (`.claude/skills/<nombre>/`). Las 33 del OS están aquí a dos niveles y **ninguna aparece en la lista de skills de la sesión**, también las propias (content-engine, video-escena-por-escena, frontend-design, tool-humanizer, recuerda). Los comandos sí funcionan; lo que falla es que una skill se active sola cuando la tarea la pide.
- Trampa comprobada: `scripts/update.sh` (el local y el nuevo) lee el remoto `origin`, que aquí es el fork propio `MaxSchock/operandi-os`. `/actualiza` tal cual no trae nada. Hay que traerlo desde `upstream/main`: `git checkout upstream/main -- scripts/update.sh scripts/_flatten-skills.sh scripts/_ensure-sinapsis-hooks.sh scripts/skills.sh` y ejecutar `update.sh` con `origin` apuntando temporalmente a upstream, o aplicar el resto a mano.
- `scripts/_flatten-skills.sh` recorre toda SKILL.md anidada (incluidas las propias del operador), no borra nada, archiva en `_archived/` y rescata los `SKILL.local.md`. Vale para las 33.
- La diferencia local frente a upstream en `CLAUDE.md`, `scripts/` y `.claude/commands/` es de 39 ficheros (hay scripts propios como `wa-ibiza-sync.sh` y `wa-pull-media.py` dentro de `scripts/`). Esos conflictos los resuelve Max viendo la lista; los scripts propios se quedan.
- Al acabar: reiniciar Claude Code y comprobar que las 33 aparecen en la lista de skills. Si no, no se sigue.

*Hecho el 08-10 (12:05 a 12:35). Hallazgos:*

- **Las 33 cargan.** Aplanadas con `_flatten-skills.sh` (33 movidas, 0 archivadas, los dos `SKILL.local.md` de meta-start-here y meta-wrap-up viajaron con su carpeta). Claude Code las recogió en caliente: aparecieron en la lista de la misma sesión, sin reiniciar. Copia previa en `~/.claude/backups/skills-pre-flatten-20261008` (228 ficheros, idéntica); commit de partida en `~/.claude/backups/os-pre-0a-20261008.commit`.
- **`update.sh` no se ejecutó, a propósito.** Sin `.claude/.upstream-state` mide contra HEAD y trata como «seguro» todo lo que no sea skill o dato del operador: habría pisado `CLAUDE.md`, `install.sh`, `.gitignore`, `check-secrets.sh` y los comandos start-here y wrap-up con la versión del original, perdiendo lo que Max añadió. Además copia `clients/` (3,2 GB) a `.backup/` en cada pasada. `skills.sh sync` tampoco: borra y recopia cualquier skill instalada que difiera de la biblioteca.
- **Se aplicó a mano con fusión a tres bandas** contra el punto donde se separó el fork (7337ae9, v0.10.1). El original cambió 77 ficheros: 33 que Max no había tocado se trajeron tal cual (6 nuevos: `/instala`, `hooks/pre-commit`, `_flatten-skills.sh`, `_ensure-sinapsis-hooks.sh`, `check-skills-depth.sh`, `hooks/README.md`); 5 tocados por ambos se fusionaron sin choque (start-here, wrap-up, `.gitignore`, `check-secrets.sh`, `install.sh`); 8 ficheros de skills intactas recibieron el contenido nuevo (brand-voice, icp, positioning, meta-skill-creator x2, tool-output-verifier, copywriting, content-repurposing).
- **Único choque real: `health-check/SKILL.md`.** Max había añadido a la lista de «core» sus 4 skills propias con rutas anidadas; el original la reescribió a 17 core con rutas planas. Se tomó la del original (las rutas de Max ya no existían). `/doctor` ya no comprueba skill-creator, mcp-builder, canvas-design ni content-engine.
- **Pendiente de Max: `CLAUDE.md` del repo.** Fusiona sin choque (lo de Max +13 líneas se conserva; el original cambia 4 trozos: el gate ofrece instalar en vez de mandar a la terminal, añade `/instala`, y la ruta de skills nuevas pasa a `.claude/skills/<nombre>/`). No aplicado. El registro de skills del fichero sigue describiendo carpetas por categoría, que ya no existen.
- **Ruta rota fuera de alcance:** `clients/operandi/clients/intelart/proposal/generate-proposal.py` y `generate-proposal-en.py` leen las fuentes de `.claude/skills/visualization/canvas-design/canvas-fonts`; ahora están en `.claude/skills/canvas-design/canvas-fonts`. No tocado por ser `clients/`.
- **No ejecutado:** `_ensure-sinapsis-hooks.sh` (escribe en `~/.claude/settings.json`; va con la fase 0b o la 3). `.claude/.upstream-state` no se escribió: con `origin` en el fork, un `/actualiza` posterior mediría el original contra el fork y podría retirar ficheros recién traídos.
- **Sigue roto y pasa a la fase 6.4:** `/actualiza` y `salud-os.py` miran `origin` (el fork). Hasta arreglarlo, ponerse al día es repetir esta fusión a mano.
- **Ruido para fases 1 y 4:** `check-skills-depth.sh` falla por 15 carpetas en `.claude/worktrees/` (copias viejas de agentes con skills anidadas) y por un `.venv` dentro de `clients/falkenlead/.claude/skills/geo`; `.claude/skills/marketing/` sigue existiendo porque otra sesión tiene ahí a medias `marketing-google-ads-auditor` (sin `SKILL.md`; cuando lo tenga debe ir a `.claude/skills/marketing-google-ads-auditor/`, y el plan `2026-10-08-google-ads-docs-skill-auditoria.md` aún dice la ruta anidada). `.claude/settings.local.json` guarda dos permisos con rutas viejas, inofensivos.

**0b. Sinapsis.** Corre la 4.1; el original va por la 4.10.0 (19-08). Leído el changelog 4.6.2 a 4.10.0: casi todo son instaladores, registro multi-sistema y Plexus (capa de equipo, luego retirada). Dos arreglos sí afectan al motor que corre aquí: (1) 4.6.2, las rebajas por caducidad de instincts se perdían cuando no había coincidencia, así que un instinct nunca baja y el índice solo crece; (2) 4.9.0, el aprendiz marcaba como error cualquier salida que contuviera «error» o «failed», y de ahí salen propuestas falsas (hay 117 sin revisar). Decisión de Max del CLAUDE.md global: no subir de versión para conservar los datos de la 4.1. Propuesta compatible: no subir, pero portar esos dos arreglos a `_instinct-activator.sh` y `observe_v3.py` tras comparar con la 4.10 (son dos ficheros de código, los datos no se tocan). Lo decide Max.

**0. Medir con datos (solo lectura).** Fuente: los 137 transcripts de la carpeta del proyecto (1,3 GB; el activador no lleva registro propio, pero su salida queda en el transcript como aviso del hook), `_instinct.log` (3,2 MB) para instincts, `_session-learner.log` para propuestas. Últimas 4 semanas. Sale una tabla: qué reglas, instincts, passive rules, hooks y skills se activan, cuántas veces, cuáles nunca; qué reglas se incumplen pese a activarse (cruzando con las reincidencias); cuánto tarda la cadena de 11 hooks por comando de terminal. Todo lo demás depende de esta tabla.

**1. Instrucciones fijas.** CLAUDE.md global y del repo, MEMORY.md (pasa del tope), working-memory (pasa del tope), `context/`. Contradicciones, datos caducados (Sinapsis 4.6.1, rutas) e instrucciones que no cambian nada. Qué se carga siempre y qué solo cuando toca. El ritual de arranque: o lo ejecuta un hook o se recorta a lo que de verdad se usa. Limpieza: las 133 copias `.bak` y `backups/` de Linus salen del repo a `~/.claude/backups/`.

**2. Reglas.** Con la tabla de la fase 0: fusionar duplicadas, archivar las que no se activan, revisar una a una las 67 irrompibles. Las que acumulan reincidencias pasan a comprobación automática que bloquea, en vez de texto. Un único sistema entre activador, instincts y passive rules; arreglar el indexador para que refresque reglas editadas. Las 117 propuestas de instinct: revisar tras portar el arreglo de 0b, porque parte serán falsas.

**3. Hooks.** Orden, tiempo medido, bloqueos falsos, los que ya no hacen nada, copias `.bak` sueltas en `~/.claude/hooks/`.

**4. Skills y plugins.** Con las skills ya cargando: duplicados entre el OS y el plugin de Anthropic, las que la fase 0 dice que no se usan, choques de nombre. Aquí entra mattpocock/skills (análisis del 08-10: revisión de arquitectura, depuración, glosario, revisión en dos ejes, retro, prototipo, preguntas de producto, trozos con test primero; renombrar `code-review` al copiar).

**5. Flujo de desarrollo.** Instalar la cadena en Linus y dejarla como plantilla para los demás productos (dashboard Operandi, motor de vídeo, Suritec). Primera pasada: revisión de arquitectura sobre `real-backend.ts` (11.730 líneas, 36 % de los commits).

**6. Bucle de mejora (para no repetir esto a mano).** Objetivo de Max: el sistema evoluciona y mejora por su cuenta. Hoy evoluciona solo por acumulación, porque lo que debía podar no funciona (comprobado 08-10):
- El destilador promete «si no se activa en 60 días se archiva sola» pero no hay código que archive ni carpeta de archivadas: 0 reglas archivadas nunca.
- 16 reglas llevan 3 o más reincidencias y nada escala: el contador sube y ya.
- `salud-os.py` compara la versión del OS contra `origin` (el fork propio), así que el aviso de «OS por detrás del remoto» no ha podido saltar nunca.

Lo que se construye, por orden:
1. **La medición de la fase 0 es un script, no un análisis.** `medir-setup.py` saca la misma tabla a partir de los transcripts (activaciones por regla/instinct/hook/skill, incumplimientos, tiempo de hooks) y la deja en un fichero con fecha. Se ejecuta solo, cada semana.
2. **Poda con evidencia, automática.** Regla sin activación en 60 días pasa a `_archivadas/` (reversible) y sale del índice; el indexador refresca las editadas. Instincts: portar el arreglo de caducidad de Sinapsis 4.6.2 (fase 0b) para que bajen de nivel solos.
3. **Reincidencias escalan.** A la tercera reincidencia de una regla, `salud-os.py` la lista como «pendiente de convertir en guard» con la propuesta de comprobación; a la quinta, la sesión de mantenimiento la construye (hook que bloquea) y la regla de texto se retira. Texto que se incumple tres veces no se arregla con más texto.
4. **Vigilancia de fuera.** `salud-os.py` compara contra `upstream` (iamasters-os) y contra los tags de Sinapsis; avisa con la lista de cambios que afectan al motor que corre aquí. `/doctor` entra en la rutina para cazar roturas de estructura como la de las skills anidadas.
5. **Sesión de mantenimiento programada, no manual.** Una vez al mes, en cron (ThinkPad) o rutina cloud: lee la medición, aplica la poda con evidencia, escala reincidencias, revisa propuestas de instinct, comprueba upstream, y deja un informe de una pantalla con el diff. Permisos: escribe solo en memoria, reglas y hooks del OS; nada de clientes, envíos ni producción. Max lee el informe; no revisa el trabajo.
6. **Los avisos de `salud-os.py` tienen dueño.** Hoy dice «díselo a Max y ofrece resolverlo»; MEMORY.md y working-memory llevan semanas pasados de tope. Lo que es poda de ficheros propios lo ejecuta la rutina; a Max solo llega lo que toca producción o contradice una decisión suya.

Comprobación final: repetir la medición y comparar con la tabla del inicio; a partir de ahí la compara la rutina cada mes.

## Reglas del trabajo

- Orden: 0a, 0b, 0, y después 1 a 6. La 0a es bloqueante; las demás no empiezan sin la tabla de la 0.
- Fases 0 a 4: primero hallazgos con su prueba, después cambios. Copia con fecha antes de cada cambio.
- Lo que cambie cómo se comporta Claude con clientes o envíos (guards, irrompibles) y lo que contradiga una decisión escrita de Max (Sinapsis 4.1, lectura obligatoria) lo decide Max viendo la lista; lo demás se ejecuta y se reporta.
- Modelo por fase: juicio (0, 1, 2, 4) con el modelo alto; mecánico (aplanado, mediciones de tiempo, limpieza de ficheros) con Sonnet en subagente con `model` explícito.
- Al cerrar cada fase: hallazgos aquí, commit, línea en el ledger.
