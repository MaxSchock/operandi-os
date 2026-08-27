# Cierre: qué se ha construido y qué queda

Fecha: 27-08-2026. Backup previo completo en `~/.claude/backups/auditoria-memoria-20260827-194031`.

## Lo que había y lo que hay

| | Antes | Ahora |
|---|---|---|
| Correcciones de Max que el sistema leía | 0 | todas (destilador sobre el transcript) |
| Reglas que podían activarse solas | 2 de fábrica | 110 con disparadores propios |
| Fragmentos en el índice de memoria | 61, de 3 ficheros | **3.978, de 568** |
| Contexto fijo en cada sesión | 74 KB (~20.000 tokens) | **54,4 KB (~14.700 tokens)** |
| Punto de inyección | `PreToolUse` (tarde) | `UserPromptSubmit` (antes de razonar) |
| Acciones peligrosas con bloqueo técnico | solo email | email + borrado + envío + cruce de entidades |
| Aviso de mantenimiento del OS | `/doctor` a mano | automático, y solo cuando hay algo |

## Piezas instaladas

Todas en `~/.claude/hooks/`, todas probadas contra casos reales de la auditoría.

**`activador-reglas.py`** (UserPromptSubmit) — busca entre las 110 reglas las que casan con lo que pide Max y las pone delante antes de que yo razone. Tres señales: disparadores escritos en su vocabulario, ficha de entidad del cliente nombrado, y titulares de una línea cuando solo hay sospecha. Registra cada activación.

**`guard-borrado.py`** (PreToolUse) — bloquea `rm`, `DELETE`, `DROP`, `TRUNCATE`, `push --force`, DELETE por HTTP y borrados en almacenamiento salvo que haya copia previa en la sesión o consentimiento explícito. Deja pasar temporales, caché y artefactos de build.

**`guard-envio-externo.py`** (PreToolUse) — bloquea WhatsApp, LinkedIn y correo por Unipile si no se ha leído antes el hilo real, y corta en seco cualquier comando que mezcle dos entidades.

**`session-ledger.py`** (PostToolUse) — diario de acciones por sesión. Es lo que permite a los gates preguntar "¿leíste el hilo?" o "¿hiciste la copia?". Nunca escribe credenciales.

**`destilador.py`** (Stop + SessionStart) — el eslabón que faltaba. Al cerrar marca la sesión; al arrancar la siguiente, lee lo que dijo Max, extrae las correcciones y o sube el contador de una regla existente o escribe una nueva con su nivel y sus disparadores. Las reglas nuevas nacen en estado `prueba`.

**`salud-os.py`** (SessionStart) — vigila versión del repo, hooks rotos, índice desincronizado, reglas caducadas o reincidentes, destilaciones atascadas y ficheros de contexto pasados de tamaño. Habla una vez y calla seis horas.

## Verificación hecha

| Prueba | Resultado |
|---|---|
| Replay: 10 prompts reales de incidentes donde fallé | **10/10** traen la regla que faltó |
| Falsos positivos sobre 7 mensajes triviales | 1/7, y son tres titulares de una línea |
| Gate de borrado, 6 casos (3 reales de la auditoría) | 6/6 |
| Gate de envío, 6 casos (incluido el cruce del 24-06) | 6/6 |
| Reconstrucción del índice | 3.970 fragmentos en 6 s |
| Todos los hooks compilan y `settings.json` es válido | sí |

El replay se hizo con los incidentes clasificados como evitables por inyección o por recall, que son 148 de los 596.

## Podado, con copia previa

- **Contradicción de seguridad resuelta**: `docker-swarm-deploy-gotchas` recomendaba literalmente `set -a; source .env` mientras `never-source-env-bash` (nacida de una contraseña de Contabo expuesta en claro) lo prohíbe. Las dos se disparaban con el mismo comando. Reescrita con la solución segura (`env_file:`) que ya estaba documentada en memoria desde el 25-06 y nunca había llegado a la regla activa.
- Instinto decaído `pm2-restart-update-env-overwrites-process-env`: retirado (ensuciaba el log en cada comando).
- 127 propuestas de instinto: vaciadas. Eran secuencias de herramientas, ninguna venía de algo que dijera Max.
- `_session-learner.sh`: retirado del hook Stop. El fichero se conserva. Llevaba meses escribiendo "no patterns" porque buscaba patrones donde no estaba la señal.

## Lo que quedaba abierto, cerrado el mismo día

Max: *"no entiendo qué quieres de mí"*. Tenía razón: le devolví tres decisiones que podía tomar yo,
justo después de pedirme que quiere olvidarse del setup. Resueltas:

- **weasyprint**: probado empíricamente. No está en el sistema, pero funciona en venv efímero.
  El CLAUDE.md decía que no funcionaba en WSL; ahora dice las dos cosas y cuándo usar cada una.
- **Versión de Sinapsis**: el fichero de Max **tenía razón** y el auditor se equivocó. Lo instalado
  en `~/.claude/` es 4.1; lo vendored en el repo es 4.6.1. No era un error, era una ambigüedad que
  ya despistó a un lector: aclarada en el texto.
- **Número de skills**: decía 26, son 33 instaladas + 20 en biblioteca. Corregido.
- **Recorte del contexto fijo**: hecho, de 74 KB a **54,4 KB** (~20.000 → ~14.700 tokens).

### Cómo se hizo el recorte sin perder nada

Las secciones "Paths y credenciales" (8,5 KB) y "Stack técnico" (6,4 KB) eran referencia pura. Se
convirtieron en 10 reglas con disparadores, se indexaron, y **solo se quitaron del CLAUDE.md después
de comprobar con replay que se recuperan solas**. Primer intento: 6/10 — insuficiente, así que se
ponderaron los disparadores por especificidad ("ocr" o "unipile" discriminan tanto como una frase) y
se afinaron dos reglas. Segundo intento: 10/10.

Además, los 59 punteros a reglas de `MEMORY.md` (9 KB) sobraban: el activador ya trae esas reglas.
Se verificó que las 59 estaban en el índice antes de retirarlas. `MEMORY.md` vuelve a ser el estado
vivo de los proyectos, no el catálogo de normas.

**Verificación final tras el recorte: 12/12 activaciones correctas, 0 falsos positivos sobre 7
mensajes triviales.** Copia de todo lo tocado en el backup.

## Lo que falta para cerrar el bucle del todo

1. **Primera destilación real**: el destilador se estrena con la siguiente sesión que cierres. Conviene mirar su log (`~/.claude/session-env/destilador/destilador.log`) al día siguiente para ver qué regla saca.
2. **Auto-ajuste de nivel**: el contador de reincidencias ya existe y `salud-os.py` avisa cuando una regla reincide 3 veces. Falta que el ascenso a gate sea automático en vez de avisado.
3. **Skills que se crean solas**: diseñado (umbral de 3 repeticiones del mismo procedimiento), no implementado. Es lo siguiente en la lista.
4. **Medición real**: el número que importa es la reincidencia dentro de dos semanas, comparada con los 5,5 incidentes al día de la línea base.
