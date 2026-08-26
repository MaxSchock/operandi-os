---
name: meta-start-here
description: Ritual de inicio de sesión para iAmasters OS. Carga el contexto necesario (operator-state, user.md, daily summary, learnings, proyectos abiertos), recapitula al operador qué dejó pendiente, y propone tarea del día. Se invoca al primer turno de cada sesión, automáticamente o por /start-here.
---

# meta-start-here

## Cuándo se invoca

- Primer mensaje de cualquier sesión (Claude lee `CLAUDE.md` y detecta esta skill como ritual de entrada)
- Usuario invoca `/start-here` explícitamente (slash command)
- Otra skill detecta deriva (ej: `meta-onboarding-wizard` finaliza y deriva aquí)

## Process

### Paso 1 · Detectar estado del repo

Lee en orden:

1. `~/.claude/skills/_operator-state.json`
   - ¿Existe? ¿`needsOnboarding: true`? → derivar a `meta-onboarding-wizard`
   - ¿`deepDiveCompleted: false` y han pasado >12h desde `onboardingDate`? → marcar flag interno `suggestDeepDive: true` (no derivar — solo recordar en el saludo, ver Paso 4)
2. `context/me.md` (o `context/user.md` legacy)
   - ¿Está vacío o sin rellenar? → derivar a `meta-onboarding-wizard`
3. `brand-context/voice/voice-profile.md`
   - ¿No existe o vacío? → sugerir ejecutar `marketing-brand-voice`

### Paso 2 · Cargar continuidad

Lee `context/working-memory.md` (scratchpad de trabajo) **primero** — es tu foto del estado actual:
- Si no existe → créalo con la cabecera de reglas y las 3 secciones vacías (Hilos activos / Notas de entorno / Decisiones pendientes). Es el bootstrap.
- Si existe → úsalo como base del saludo: qué hilos están abiertos, qué decisiones esperan al operador.

Consulta `public.n8n_errors_inbox` en Supabase (project `xepotlbqlwmriwievyvc`):

```sql
SELECT id, client, workflow_name, step_name, error_message, occurred_at
FROM public.n8n_errors_inbox
WHERE resolved_at IS NULL
ORDER BY occurred_at DESC LIMIT 20;
```

Es el canal por el que los sistemas desatendidos llegan a un humano, y va **antes** del saludo: si algo lleva roto toda la noche, eso es la noticia del día, no lo que quedó pendiente ayer. Resumir agrupado por cliente/workflow.

Las alertas que dicen que un proveedor externo ha cambiado bajo nuestros pies (rutas retiradas, credenciales caducadas, respuestas con otra forma) van primero: son las que rompen sistemas enteros en silencio.

Un proveedor no avisa de lo que rompe. Sus newsletters cuentan lo que añade, y una comprobación que dependa de leer sus correos da luz verde mientras la integración lleva días caída. La señal fiable es siempre lo que responde su API, sondeada por nosotros. Si un sistema depende de un tercero y no tiene una comprobación propia que lo vigile, ese es el hueco, y merece nombrarse en el saludo.

Lee `synapsis/daily-summaries/<TODAY>.md` o `<YESTERDAY>.md`:
- Si hay → resumir el "For tomorrow" en una línea
- Si no → primera sesión del día

Lee `context/learnings.md` (si > 200 chars):
- Identificar la última lección añadida

Lee `synapsis/projects.json` (Sinapsis):
- Filtrar proyectos con `status: active`
- Listar máximo 3 más recientes

Lee `projects/briefs/*/brief.md`:
- Filtrar los que tengan YAML frontmatter `status: active` o `phase: in-progress`

### Paso 2.4 · Repaso de canales (OBLIGATORIO, antes del saludo)

El saludo no vale con working-memory + inbox n8n + daily summaries. Desde el último EOD se repasan
TODOS los canales, en paralelo (4 subagentes) y sin atajos:

1. **WhatsApp** (BD `evolution` en VpsFigura, tabla `Message`): todos los chats de trabajo, texto
   completo, audios descargados y transcritos (Gemini en ki-prod-01; Whisper si Gemini falla).
2. **Buzón + Drive KIsult** (OAuth `accounts/kisult.json`): recibidos, enviados, borradores, docs
   "Notizen von Gemini" íntegros, calendario.
3. **Buzón + Drive Operandi** (OAuth `token-operandi.json`): ídem.
4. **Falkenlead** max@ y administracion@ por IMAP (`~/.config/falkenlead/`).
5. **Personal** por Unipile desde el VPS (`GET /api/v1/emails?account_id=fEIV_1UOTu-REknkpb_ZVA`).

Las reuniones de Max se detectan por sus transcripts, no porque él las mencione; cada una va al
ledger (`docs/horas-ledger.csv`, tipo reunion). Salida: "espera respuesta de Max" por canal y
señales de facturación al radar (paso 2.5). Origen: Max lo exigió el 17-08 y lo reclamó de nuevo el
22-08 al darle un saludo sin repaso. Memoria: `feedback-arrancar-sesion-con-repaso-de-canales`.

### Paso 2.5 · Radar de facturación (al repasar canales)

El repaso de bandejas y WhatsApp es donde aparecen, sueltas y sin avisar, las cosas que luego
hacen falta al facturar. Cuando se lea un canal (WhatsApp vía BD `evolution`, buzones KIsult /
Operandi / Falkenlead / personal), se anota **en el momento** lo que sea señal de facturación,
porque a fin de mes ya nadie se acuerda de en qué chat estaba.

Qué cuenta como señal, con lo que hay que capturar de cada una:

| Señal | Qué se apunta |
|---|---|
| Autorización a facturar ("puedes facturar", "Rechnung stellen", "mándame la factura") | quién, qué concepto, qué hito o porcentaje, fecha del mensaje |
| Confirmación de pago ("haben überwiesen", "te lo transferí", "pagado") | quién, qué factura dice haber pagado, fecha. **Es un dicho, no un hecho**: se verifica contra el banco antes de dar nada por cobrado |
| Datos fiscales del cliente (razón social, dirección, VAT/USt-IdNr, a quién se emite) | el dato exacto y quién lo dio. Un cambio aquí obliga a rehacer facturas ya emitidas |
| Hitos y forma de pago (50/50, a fin de mes por horas, vencimientos) | el acuerdo literal y de qué proyecto |
| Gasto nuevo mencionado (proveedor, suscripción, compra) | proveedor y periodo, para buscar luego la factura en los buzones |
| Peticiones del asesor (Guille, `guillermo@articoasesores.es`) | qué pide y para qué trimestre |

Se escriben en `clients/falkenlead/facturacion-radar.md` (append-only, una línea por señal, con
fecha y fuente citada para poder volver al mensaje original). Max factura todo desde Falkenlead,
también lo de Operandi y KIsult, por eso el radar es único y vive ahí.

En el saludo: si hay entradas del radar sin resolver, **una línea** al final ("Pendiente de
facturar: X de Jonas desde el 04-08"). No se convierte el saludo en un informe contable; el
detalle está en el archivo.

Reglas duras de este paso:
- Nunca dar por cobrada una factura porque alguien lo diga en un chat. La fuente de verdad es el
  extracto bancario (`clients/falkenlead/scripts/enablebanking.py tx`).
- **A KIsult se factura por porcentaje del proyecto, nunca por horas.** Si un mensaje habla de
  "Zeiten"/horas, la señal a anotar es el hito o el porcentaje, no un número de horas facturables.
  Las horas del ledger son control interno (contrastar esfuerzo real contra lo presupuestado).
- Nunca emitir ni enviar nada desde el ritual. El radar solo anota.

### Paso 3 · Sincronizar skills detectadas

Comprueba si hay `.claude/.skills-pending.json` (creado por hook `skill-change-detector.sh`):
- Si sí → actualizar `synapsis/skills-catalog.json` con las skills nuevas
- Limpiar el flag

### Paso 4 · Saludo contextual

Construir saludo según contexto detectado:

**Si hay daily summary de ayer:**
> "Hola {{nombre}}. Ayer cerraste con: {{summary}}.
> Para hoy proponías: {{for-tomorrow}}.
> ¿Sigues con eso, o cambiamos?"

**Si hay proyecto activo pero no daily summary:**
> "Hola {{nombre}}. Tienes el proyecto **{{nombre-proyecto}}** abierto en fase {{fase}}.
> ¿Continúas con él o vamos a otra cosa?"

**Si no hay nada activo:**
> "Hola {{nombre}}. ¿En qué te ayudo hoy?
>
> [1] Crear contenido (skills marketing-*)
> [2] Trabajar con un cliente (`/add-client` o `cd clients/<x>`)
> [3] Análisis estratégico (skills strategy-*)
> [4] Tarea libre — dime qué necesitas"

### Paso 4.5 · Recordatorio de deep-dive (si aplica)

Si en Paso 1 quedó `suggestDeepDive: true`, añade al final del saludo (no antes — el saludo principal va primero):

```
PD: aún no has completado el deep-dive del onboarding. El sistema te
conoce superficialmente. Cuando tengas 25 minutos, ejecuta `/deep-dive`
y refinamos.
```

Este recordatorio se muestra **cada vez** que el operador arranca, hasta que `deepDiveCompleted: true`. No es intrusivo (solo 1 línea), pero recuerda.

Si el operador ya completó la deep-dive (`deepDiveCompleted: true`), no menciones nada.

### Paso 5 · Si hay pending tasks de Sinapsis

Sinapsis puede tener instincts en draft pendientes de promote. Si en `~/.claude/skills/_instincts-index.json` hay 5+ drafts con `occurrences >= 3`:
- Mencionar al final del saludo: "(Tienes 5 instincts listos para revisar con `/analyze-session` cuando quieras)"

### Paso 6 · No hacer más

Importante: este ritual NO ejecuta tareas. Solo carga contexto y propone.
- Si el usuario respondió a la pregunta planteada → continúa con la tarea concreta (otra skill u acción directa).
- Si no → espera input.

## Outputs

- Mensaje al usuario con resumen + propuesta
- Update interno: `synapsis/skills-catalog.json` si hubo skill changes pending

## Skills que llama

- **`meta-onboarding-wizard`** — si detecta primer arranque
- **`marketing-brand-voice`** — opcionalmente si falta voice profile

## Skills que sugiere (sin invocar automáticamente)

- **`meta-deep-dive`** — si el operador completó el wizard inicial pero no la deep-dive (mostrado como PD al final del saludo, recordatorio diario hasta que se complete)

## Edge cases

- **No hay `.claude/skills/`**: el repo está corrupto o no instalado bien. Avisa al usuario y sugiere `bash scripts/install.sh`.
- **`operator-state.json` corrupto (JSON mal formado)**: recuperar de backup en `~/.claude/_backup_*` o derivar a re-onboarding.
- **Daily summary de hace 5+ días**: mejor empezar limpio que arrastrar contexto stale. Saludar como nueva sesión.

## Examples

**Caso 1 · Continuidad cálida:**
```
Operador: (abre Claude Code en lunes)
Skill: "Hola Marta. Viernes cerraste con el blog post de Stripe billing (status: pending review).
        Para hoy proponías: 'pasarlo por output-verifier y publicar'.
        ¿Sigues con eso?"
```

**Caso 2 · Sin actividad reciente:**
```
Operador: (abre tras 5 días sin abrir)
Skill: "Hola Marta. Hace tiempo. ¿En qué te ayudo hoy?
        [1] Crear contenido
        [2] Trabajar con un cliente (tienes 3: Acme, ContoSL, NorthStar)
        [3] Análisis estratégico
        [4] Tarea libre"
```

**Caso 3 · Primer arranque tras instalación:**
```
Skill: → detecta needsOnboarding: true
       → deriva a meta-onboarding-wizard
       (no muestra saludo propio)
```
