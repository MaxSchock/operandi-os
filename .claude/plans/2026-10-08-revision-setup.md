# Revisión a conciencia del setup de Claude Code

Estado: terminado 08-10-2026. Las siete fases están hechas. Lo que sigue vive fuera de este plan y está en `_abiertos.md`: fusionar la rama `pocock-skills` de Linus (tras el OK de Max a canary-0810) y elegir candidato de la revisión de arquitectura. La rutina de los lunes mide a partir de ahora.

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
- **Para la fase 3 (bloqueo falso):** `.githooks/pre-commit` paró el commit por `content-engine/.env.example` y `mcp-builder/reference/evaluation.md`, que solo cambiaban de ruta y solo llevan claves de ejemplo. Vuelve a escanear entero cualquier fichero renombrado y no reconoce marcadores de ejemplo en `.env.example`. Se usó su excepción documentada tras comprobar los valores. Commit 3b53789, sin subir al fork.
- **Ruido para fases 1 y 4:** `check-skills-depth.sh` falla por 15 carpetas en `.claude/worktrees/` (copias viejas de agentes con skills anidadas) y por un `.venv` dentro de `clients/falkenlead/.claude/skills/geo`; `.claude/skills/marketing/` sigue existiendo porque otra sesión tiene ahí a medias `marketing-google-ads-auditor` (sin `SKILL.md`; cuando lo tenga debe ir a `.claude/skills/marketing-google-ads-auditor/`, y el plan `2026-10-08-google-ads-docs-skill-auditoria.md` aún dice la ruta anidada). `.claude/settings.local.json` guarda dos permisos con rutas viejas, inofensivos.

**0b. Sinapsis.** Corre la 4.1; el original va por la 4.10.0 (19-08). Leído el changelog 4.6.2 a 4.10.0: casi todo son instaladores, registro multi-sistema y Plexus (capa de equipo, luego retirada). Dos arreglos sí afectan al motor que corre aquí: (1) 4.6.2, las rebajas por caducidad de instincts se perdían cuando no había coincidencia, así que un instinct nunca baja y el índice solo crece; (2) 4.9.0, el aprendiz marcaba como error cualquier salida que contuviera «error» o «failed», y de ahí salen propuestas falsas (hay 117 sin revisar). Decisión de Max del CLAUDE.md global: no subir de versión para conservar los datos de la 4.1. Propuesta compatible: no subir, pero portar esos dos arreglos a `_instinct-activator.sh` y `observe_v3.py` tras comparar con la 4.10 (son dos ficheros de código, los datos no se tocan). Lo decide Max.

*Mirado el 08-10. Hallazgos de la 0b:*

- **Sinapsis está abandonado.** El autor archivó el repositorio el 21-08-2026 en la v4.10.0: «Claude Code now has persistent memory of its own [...] Running Sinapsis alongside it added more noise than signal, so I stopped using it». El aviso enumera seis defectos sin arreglar (issue 36): instincts irrelevantes inyectados en cada llamada, sin deduplicar por sesión, passive rules de «una vez por sesión» que saltan en cada uso de herramienta, y el resumen diario entero inyectado sea cual sea el proyecto. La medición de la fase 0 los confirma uno a uno aquí.
- **El arreglo de caducidad (4.6.2) falta en local**, comprobado comparando `_instinct-activator.sh`: las rebajas solo se guardan cuando hay coincidencia. El registro lo delata: 12.023 anotaciones «DECAYED» en cuatro semanas sobre los mismos 3 instincts.
- **No se porta nada todavía.** Portar ese arreglo hace que el motor empiece a escribir rebajas en `_instincts-index.json` (fichero que este plan no toca) para mantener vivo un sistema que su autor ha dado por muerto. La pregunta ya no es «¿porto dos arreglos?» sino «¿siguen encendidos los activadores de Sinapsis?». Decisión de Max, con propuesta en la fase 2.

*Decidido por Max el 08-10: apagar. Hecho:* quitados de `~/.claude/settings.json` los cinco hooks de Sinapsis (observador antes y después, `_project-context.sh`, `_passive-activator.sh`, `_instinct-activator.sh`). Datos intactos en `~/.claude/skills/`. Vuelta atrás: `~/.claude/backups/os-repo-copias-20261008/settings.json.antes-apagar-sinapsis-20261008`. No se portó ningún arreglo: ya no hace falta. En la comunidad de IA Masters no hay sustituto oficial ni respuesta de Ángel al hilo del 19-09 que lo pregunta; el OS original sigue describiéndose con Sinapsis pero no tiene commits desde el 19-08.

**0. Medir con datos (solo lectura).** Fuente: los 137 transcripts de la carpeta del proyecto (1,3 GB; el activador no lleva registro propio, pero su salida queda en el transcript como aviso del hook), `_instinct.log` (3,2 MB) para instincts, `_session-learner.log` para propuestas. Últimas 4 semanas. Sale una tabla: qué reglas, instincts, passive rules, hooks y skills se activan, cuántas veces, cuáles nunca; qué reglas se incumplen pese a activarse (cruzando con las reincidencias); cuánto tarda la cadena de 11 hooks por comando de terminal. Todo lo demás depende de esta tabla.

*Hecho el 08-10. La medición es ya un script: `scripts/medir-setup.py` (3 s, solo lectura), informe en `docs/medicion-setup/2026-10-08.md`. Ventana de 28 días: 133 sesiones, 4.203 mensajes de Max, 33.652 llamadas a herramientas (26.887 de terminal). Hallazgos:*

- **Texto que los hooks meten en contexto en 4 semanas: unos 11 MB.** Activador de reglas 4,4 MB; passive rules 4,1 MB; instincts 1,9 MB; resumen diario (`_project-context.sh`) 0,9 MB. Es más que todos los ficheros fijos juntos multiplicados por las 133 sesiones (61 KB x 133 = 8 MB).
- **Instincts: 44 de 52 no han saltado ni una vez.** Tres concentran el 99 % de 10.467 activaciones y son genéricos («no escribas secretos», «no uses corchetes de relleno», «commits convencionales»). Los 30 de n8n, Docker y Supabase, que son los que nacieron de fallos reales, no saltan.
- **Passive rules: una sola regla, «sin em-dashes», saltó 6.883 veces** (una de cada cuatro órdenes de terminal). Ya está en el CLAUDE.md global.
- **Reglas del activador: 307 vigentes (no 197), 78 sin activarse nunca** (6 irrompibles). Cada mensaje de Max con reglas recibe 3,5 de media. Las más repetidas saltan por disparadores demasiado anchos: `feedback-linus-forma-de-trabajo` 578 veces en 58 sesiones, `reference-unipile-enviar-como-max` 452.
- **22 reglas con 3 o más reincidencias.** Dos grupos distintos: (a) las que saltan mucho y se incumplen igual (`never_assume_global_rule` 298 activaciones y 36 reincidencias; `mensajes-en-voz-de-max` 158 y 14; `answer_the_literal_question_first` 160 y 8): más texto no las arregla, van a guard; (b) las que reinciden y **no saltan nunca** (`review_thoroughly_no_shortcuts` 49 reincidencias y 0 activaciones; `no-delegar-a-max` 9 y 0; `usar-codex-para-cualquier-desarrollo` 7 y 0; `no-responder-de-memoria` 6 y 0): les faltan disparadores, o la conducta no depende de lo que escribe Max y un activador por palabras no puede cazarla.
- **Hooks cortados por tiempo:** `_project-context.sh` 111 veces (p95 de 7,4 s con tope de 3 s), `_instinct-activator.sh` 46, `_passive-activator.sh` 30, los cuatro guards de envío 16-17 cada uno. `rtk` falló 13 veces por no estar en la ruta. Un guard que se corta por tiempo no ha comprobado nada.
- **Guards que bloquean de verdad: solo `guard-respuesta` (7 bloqueos).** Los demás solo dejaron constancia de permisos concedidos.
- **Skills: de las 33 del OS, una sola se usó en 4 semanas** (`content-engine`, una vez), y eso contando que no cargaban. Lo que de verdad se usa son tres comandos: `/session-end` (80), `/start-here` (17), `/eod` (2). La medición de skills se repite dentro de 2 semanas, ya con las skills cargando; hasta entonces no se desinstala ninguna por «no usada».
- **Límite de la fuente:** un hook que termina bien sin escribir nada no deja rastro; el tiempo real de la cadena de 11 hooks por orden se mide aparte en la fase 3.

**1. Instrucciones fijas.** CLAUDE.md global y del repo, MEMORY.md (pasa del tope), working-memory (pasa del tope), `context/`. Contradicciones, datos caducados (Sinapsis 4.6.1, rutas) e instrucciones que no cambian nada. Qué se carga siempre y qué solo cuando toca. El ritual de arranque: o lo ejecuta un hook o se recorta a lo que de verdad se usa. Limpieza: las 133 copias `.bak` y `backups/` de Linus salen del repo a `~/.claude/backups/`.

*Hecho el 08-10 (parte del repo):*

- `CLAUDE.md` del repo de 18,1 a 14,8 KB: aplicados los cambios del original, registro de skills reducido a lo que la lista de la sesión no enseña ya, y corregido «Sinapsis v4.6.1» (corre la 4.1).
- 133 copias de working-memory, 114 del ledger, la carpeta `backups/` (122 ficheros de Linus y del VPS) y 3 copias de hooks trasladadas a `~/.claude/backups/os-repo-copias-20261008/`. `.gitignore` ignora `*.bak-*`, `*.backup-*` y `/backups/`. Quedan 136 copias dentro de `clients/` y `projects/`, sin tocar. Las copias las hacen las sesiones a mano (regla 1), no un hook: volverán, y la rutina semanal avisa cuando pasen de 20.
- El arranque de sesión recuerda ahora los planes sin terminar: `salud-os.py` lista los de `.claude/plans/` cuyo `Estado:` no empiece por terminado, cerrado o descartado, más los de `.claude/plans/_abiertos.md` (13 planes de otras rutas, inventariados el 08-10 contra session-logs). Sin caché: sale en cada sesión.
- Regla nueva `feedback-planes-se-terminan-hasta-la-ultima-fase` (irrompible), pedida por Max el 08-10.
- **Pendiente de Max:** el `CLAUDE.md` global (26 KB) y su «lectura obligatoria al inicio» (clients.private.md, consulta de errores n8n, cinco ficheros de `context/`), que no se cumple y nada lo detecta. MEMORY.md está en su tope (17,0 KB) y working-memory lo pasa (3,7 de 2,5 KB).

*Decidido por Max el 08-10 y hecho:* la «lectura obligatoria» del `CLAUDE.md` global pasa a «Arranque de sesión»: el hook `salud-os.py` inyecta la memoria de trabajo, los planes abiertos y los avisos; `clients.private.md` y los errores de n8n se leen cuando toca y con `/start-here`. Mismo cambio en el `CLAUDE.md` del repo, que además marca Sinapsis como apagado. Copia del global en `~/.claude/backups/os-repo-copias-20261008/CLAUDE.global.md.antes-20261008`.

**2. Reglas.** Con la tabla de la fase 0: fusionar duplicadas, archivar las que no se activan, revisar una a una las 67 irrompibles. Las que acumulan reincidencias pasan a comprobación automática que bloquea, en vez de texto. Un único sistema entre activador, instincts y passive rules; arreglar el indexador para que refresque reglas editadas. Las 117 propuestas de instinct: revisar tras portar el arreglo de 0b, porque parte serán falsas.

*Hecho el 08-10 (lo que no depende de la decisión sobre Sinapsis):*

- **Dónde viven de verdad las reincidencias.** Las cuatro reglas más incumplidas ya son comprobaciones de `guard-respuesta.py` desde el 31-08; sus contadores (49, 36, 24, 8) son en buena parte anteriores. Las reglas de conducta («no digas que no puedes», «revisa a fondo», «no preguntes si sigues») no dependen de lo que escribe Max, así que un activador por palabras del mensaje no puede cazarlas: su sitio es el guard que mira la respuesta.
- **Dos comprobaciones nuevas en `guard-respuesta.py`:** (5) pedir permiso o aparcar trabajo («¿sigo?», «avísame», «queda para otra sesión») cuando la frase no habla de un envío, borrado o producción; (6) encargar a Max una comprobación. Probadas con 10 casos y contra 1.239 respuestas reales de dos semanas: la 5 habría saltado 59 veces (4,8 %), la 6 cuatro. Los ejemplos son incumplimientos de verdad («¿Sigo con GBS o cambias el orden?», «Avísame»).
- **El indexador refresca las reglas editadas** (guarda la fecha del fichero por entrada) y retira las que ya no existen. De paso arreglada la llamada desde `destilador.py`, que se habría roto con el cambio.
- **Poda con datos: `~/.claude/hooks/podar-reglas.py`.** Archiva en `memory/_archivadas/` las reglas con más de 60 días y cero activaciones en 60 días, nunca irrompibles. Hoy lista 17 y no aplica: el activador existe desde el 27-08 y no hay 60 días de datos hasta el 27-10. La fecha de creación sale del primer commit en `~/sinapsis-state` cuando el fichero no la trae (la del disco no vale: el cambio de portátil las igualó).
- **Lo útil de Sinapsis ya está en el activador:** 63 instincts y passive rules técnicos volcados en cinco reglas `reference-gotchas-*` (n8n, Docker y servidor, Supabase y Postgres, APIs externas y LLM, WSL y entorno). Probado: saltan con mensajes de cada tema. Los 20 restantes son de conducta y ya están en el `CLAUDE.md` global.
- **Pendiente de Max:** apagar los cinco hooks de Sinapsis (observe pre y post, `_project-context.sh`, `_passive-activator.sh`, `_instinct-activator.sh`). Ahorra unos 7 MB de texto inyectado al mes y 187 cortes por tiempo. Los datos no se tocan y se revierte desde la copia de `settings.json`. Con eso queda un solo sistema de reglas. Pendientes también: revisar una a una las 50 irrompibles y las 6 que no saltan nunca.

*Cierre de la fase 2 (08-10):*

- **Un solo sistema:** activador más guards. Sinapsis apagado.
- **El activador ya no repite la regla entera.** La primera vez en la sesión sale completa; si vuelve a tocar en los 45 minutos o 12 activaciones siguientes, sale solo su titular. Era el mayor gasto que quedaba: 9.138 activaciones en cuatro semanas, hasta 10 veces la misma regla por sesión. Por eso no se han estrechado los disparadores anchos (Linus, Unipile): con la repetición resuelta ya no cuestan.
- **Las 50 irrompibles, revisadas una a una.** Dos duplicadas fusionadas en el índice (`feedback_unipile_for_personal_gmail` en `reference-unipile-enviar-como-max`; `feedback-cuentas-reales-de-cliente-en-su-propia-instancia` en `feedback-cuenta-de-una-persona-en-su-propia-instancia`), con sus disparadores pasados a la que queda. Las 5 que no saltaron en cuatro semanas son de situaciones raras y graves (secretos en pantalla, tomas de vídeo con coste, bugs en producción): se quedan. Una está caducada en su texto y la decide Max: `feedback-un-agente-pesado-a-la-vez-en-el-pc` habla del PC de 8 GB y el ThinkPad da 16 GB a WSL desde el 27-09.
- **Las 117 propuestas de instinct** no se revisan: salían del observador de Sinapsis, ya apagado, y parte eran falsas por el fallo que el propio autor documentó. Siguen en `_instinct-proposals.json`.

**3. Hooks.** Orden, tiempo medido, bloqueos falsos, los que ya no hacen nada, copias `.bak` sueltas en `~/.claude/hooks/`.

*Hecho el 08-10:*

- La cadena de 11 hooks por orden de terminal tarda 0,24 s en frío (medido, 5 pasadas). El tiempo no es el problema; lo es el texto inyectado y los cortes cuando la máquina va cargada.
- Tope de los cuatro guards de envío y borrado subido de 5 a 20 s en `settings.json`: se cortaban 16-17 veces cada uno en cuatro semanas, y un guard cortado deja pasar la orden sin mirarla.
- Filtro de secretos previo al commit (`.githooks/pre-commit`): ya no vuelve a escanear ficheros que solo cambian de ruta. Probado que sigue bloqueando una clave nueva.
- Las 3 copias `.bak` de `~/.claude/hooks/` trasladadas a la carpeta de copias.

**4. Skills y plugins.** Con las skills ya cargando: duplicados entre el OS y el plugin de Anthropic, las que la fase 0 dice que no se usan, choques de nombre. Aquí entra mattpocock/skills (análisis del 08-10: revisión de arquitectura, depuración, glosario, revisión en dos ejes, retro, prototipo, preguntas de producto, trozos con test primero; renombrar `code-review` al copiar).

*Hecho el 08-10:*

- `mcp-builder` y `skill-creator` archivadas en `.claude/skills/_archived/`: eran copia del 19-05 de las del plugin de Anthropic, que ya carga las suyas. `canvas-design` se queda porque los scripts de la propuesta de Intelart leen sus fuentes (ruta arreglada).
- `/backup` existe dos veces con sentidos distintos (el de Sinapsis exporta su estado; el del OS copia todos los datos). Se resuelve con la decisión sobre Sinapsis.
- No se desinstala ninguna skill por «no usada»: hasta hoy no cargaban. Se vuelve a medir el 22-10 con la rutina semanal.
- mattpocock/skills entra con la fase 5.

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

*Hecho el 08-10:*

- 1. `scripts/medir-setup.py` (informe en `docs/medicion-setup/` y datos en `~/.claude/session-env/medicion-setup-<dias>d.json`).
- 2. `podar-reglas.py` e indexador que refresca. Falta la caducidad de instincts, que depende de la decisión sobre Sinapsis.
- 3. `salud-os.py` ya listaba las reincidentes; las de conducta van a `guard-respuesta.py` (ver fase 2).
- 4. `salud-os.py` compara contra el original (`upstream`) usando `.claude/.original-aplicado`, con un fetch al día como mucho.
- 5. `scripts/mantenimiento-setup.sh` en cron, lunes 08:30: mide, poda, reindexa, mira el original y deja una nota que `salud-os.py` enseña en la sesión siguiente. Lo que exige juicio lo hace esa sesión. No arranca un Claude por su cuenta: es la parte determinista.
- 6. La nota de mantenimiento dice qué hacer y se borra al terminar.

*Fase 5, decidida por Max el 08-10 (rama aparte, sin desplegar):* rama `pocock-skills` en `~/max-assistent-pocock` (desde `origin/main`, commit ec6a1084), con once skills en `.claude/skills/`: `improve-codebase-architecture`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `prototype`, `retro`, `tdd`, `writing-for-agents` tal cual; `revision-dos-ejes` (era `code-review`, se suma a Codex); `grilling` limitada a preguntas de producto; `trozos-con-test-primero` escrita a partir de `implement-spec`. Origen y licencia en `ORIGEN-mattpocock.md`. No toca `canary-0810` ni código. Se fusiona en main cuando Max dé el OK a `canary-0810`. Primera pasada de arquitectura sobre `real-backend.ts` hecha con la skill, en solo lectura y leyendo las 11.730 líneas (no 10.600): informe en `docs/arquitectura/revision-2026-10-08.md` y `.html` de esa rama (commit df8a2e74) y copia en Descargas. Datos: una sola clase de 9.462 líneas con 90 métodos públicos y 134 privados; 110 de 165 commits desde el 08-09 son arreglos; no hay `GLOSSARY.md` ni `docs/adr/` y la historia de los incidentes vive en 3.313 líneas de comentario. Siete candidatos; el primero, «de la acción propuesta a la tarjeta que espera» (32 arreglos de 42 commits en sus rangos, con una función de 380 líneas en el centro). La skill pide que Max elija candidato antes de proponer interfaces. Plantilla para los demás productos: `scripts/instalar-cadena-revision.sh <repo>` copia las once skills sin pisar las que ya existan.


**Comprobación final (08-10-2026), contra la tabla del inicio:**

| Pieza | Antes | Después |
|---|---|---|
| Texto fijo por sesión | ~61 KB (global 26, repo 17, MEMORY 17) | 58,5 KB (global 27,4; repo 14,1; MEMORY 17,0) más 6,7 KB que ahora inyecta el arranque (memoria de trabajo y planes abiertos, que antes había que acordarse de leer) |
| Texto inyectado por hooks en 4 semanas | ~11 MB | Sinapsis fuera (unos 6,9 MB menos); el activador deja de repetir reglas enteras. Cifra real: informe del lunes 13-10 |
| Reglas | 341 en el índice | 345 (310 vigentes): +5 de gotchas, +1 de planes, 2 fusionadas, 2 retiradas por no existir. 17 listas para archivar el 27-10 |
| Sistemas de reglas | 3 | 1 |
| Hooks | 23 órdenes, 11 antes de cada orden de terminal | 18 y 7 |
| Skills del OS | 34, ninguna cargaba | 32 cargando, 2 duplicadas archivadas |
| Lectura obligatoria al arrancar | ~10 ficheros, no se cumplía | la hace el hook |
| Copias sueltas en el repo | 133 `.bak` y `backups/` | fuera, en `~/.claude/backups/os-repo-copias-20261008/` |

No se cumplió «menos texto fijo»: se queda igual. Lo que baja de verdad es lo que se inyecta por orden y por mensaje, que era veinte veces mayor. La rutina de los lunes compara a partir de ahora.

## Reglas del trabajo

- Orden: 0a, 0b, 0, y después 1 a 6. La 0a es bloqueante; las demás no empiezan sin la tabla de la 0.
- Fases 0 a 4: primero hallazgos con su prueba, después cambios. Copia con fecha antes de cada cambio.
- Lo que cambie cómo se comporta Claude con clientes o envíos (guards, irrompibles) y lo que contradiga una decisión escrita de Max (Sinapsis 4.1, lectura obligatoria) lo decide Max viendo la lista; lo demás se ejecuta y se reporta.
- Modelo por fase: juicio (0, 1, 2, 4) con el modelo alto; mecánico (aplanado, mediciones de tiempo, limpieza de ficheros) con Sonnet en subagente con `model` explícito.
- Al cerrar cada fase: hallazgos aquí, commit, línea en el ledger.
