---
name: automation-n8n-builder
description: Crea, valida y despliega workflows de n8n desde Claude Code vía la REST API de n8n (sin MCP). Úsala cuando el usuario diga "crea un workflow en n8n", "monta un n8n que haga X", "convierte esta idea en automatización", "diseña un flujo n8n", o describa una secuencia de pasos automatizables (recibir webhook → procesar → enviar a Slack, scheduler diario que lee de Google Sheets, etc.). Activable también con frases como "auto­matización", "n8n", "workflow", "trigger". NO uses esta skill para migrar workflows existentes de n8n a Claude · para eso usa automation-n8n-to-claude.
author: IA Masters Academy
version: 2.0.0
tags: [n8n, rest-api, automatizacion, workflow, builder, claude-code]
---

# automation-n8n-builder · Constructor de workflows n8n desde Claude

> Esta skill convierte una descripción en lenguaje natural ("quiero que cuando llegue un lead por formulario lo meta en Sheets y avise por Slack") en un workflow n8n funcional, validado y desplegado.

---

## Prerequisitos

Todo se opera vía la **REST API de n8n** (`/api/v1/...` con header `X-N8N-API-KEY`). No se usa ningún MCP de n8n; la REST cubre todo el ciclo (crear, editar, activar, ejecutar por webhook, leer ejecuciones).

1. **Credenciales por instancia** en `~/.config/n8n-cli/`:
   - Operandi (default): `~/.config/n8n-cli/api-key` + `api-url` (= `https://ssn8n.figura-studio.com`).
   - KIsult Hemmersbach: `~/.config/n8n-cli/kisult/hemmersbach/api-key` + `api-url`.
   - Otras instancias: misma convención `~/.config/n8n-cli/<empresa>/<cliente>/`.
2. **Verificar el host ANTES de cualquier POST/PUT.** Cada empresa tiene su n8n; un workflow de cliente KIsult nunca va al n8n de Operandi. Confirma con el usuario a qué instancia va si no es obvio por contexto.
3. **No existe "run now" en la API pública.** Para disparar un workflow desde fuera, usa un webhook trigger y haz POST a la URL de webhooks de la instancia (Operandi: `https://sswebhook.figura-studio.com/webhook/<path>`).

Si falta la API key de la instancia destino, pedirla antes de continuar (nunca pegarla en el chat; va a archivo chmod 600).

---

## Flujo de trabajo

### Paso 1 · Entender el caso de uso

Antes de tocar n8n, hacer 3-5 preguntas para clarificar:

- ¿Cuál es el **trigger**? (webhook, schedule, evento de app, manual…)
- ¿Qué **fuentes de datos** intervienen? (Google Sheets, Notion, base de datos, API…)
- ¿Qué **transformaciones** son necesarias? (filtrar, enriquecer, formatear…)
- ¿Cuál es el **destino**? (Slack, email, Notion, otra app…)
- ¿Hay **manejo de errores** necesario? (reintentos, notificaciones de fallo…)

Si la idea es vaga, proponer 2-3 versiones concretas y dejar al usuario elegir.

### Paso 2 · Diseño visual del flujo

Antes de tocar la API, mostrar al usuario un **diagrama en texto** del workflow propuesto:

```
[Webhook: form-submission]
    ↓
[Filter: si email contiene @empresa.com]
    ↓
[Sheets: append row con {nombre, email, fuente, fecha}]
    ↓
[Slack: notify #leads con "Nuevo lead: {nombre}"]
    ↓
[Error branch: si Slack falla, email a admin]
```

Pedir confirmación al usuario antes de construir.

### Paso 3 · Construir vía REST

Endpoints (base = contenido de `api-url`, header `X-N8N-API-KEY`):

- `POST /api/v1/workflows` · crear con el JSON completo (`name`, `nodes`, `connections`, `settings`). Se crea desactivado.
- `PUT /api/v1/workflows/{id}` · iterar sobre el workflow. Body estricto de 4 keys (ver "REST API safety" abajo).
- `GET /api/v1/workflows/{id}` · releer el estado actual antes de cada PUT.
- `POST /api/v1/workflows/{id}/activate` / `.../deactivate`.
- Para parámetros de nodos que no conoces de memoria: duplicar un nodo equivalente de un workflow existente de la misma instancia (GET + copiar el bloque del nodo) o consultar docs.n8n.io. No inventar `typeVersion`.

Construir el workflow incrementalmente (GET → modificar JSON → PUT), no de golpe. Tras cada iteración, mostrar progreso al usuario.

### Paso 4 · Validar antes de desplegar

No hay endpoint de validación en la API pública: la validación es tuya, sobre el JSON, antes del PUT. Revisar:

- Todos los nodos tienen credenciales asignadas (o aviso si faltan)
- Las conexiones entre nodos son coherentes
- Los expressions (`{{$json.field}}`) referencian campos que existen
- El trigger está configurado correctamente

Si hay errores → mostrarlos al usuario, proponer fixes, no desplegar todavía.

### Paso 5 · Test en modo prueba

Antes de activar:

- Si el trigger es webhook: activar, mandar un POST con payload de ejemplo a la URL de webhook, y leer el resultado con `GET /api/v1/executions?workflowId={id}&includeData=true`.
- Si el trigger es schedule: probar con un webhook trigger temporal en paralelo, o pedir al usuario un "Execute workflow" manual desde la UI.
- Revisar la ejecución nodo a nodo en la respuesta de executions. Si algún nodo falla, proponer fix o ajustar el diseño.
- Tests destructivos (DELETE, escrituras sobre datos reales) SIEMPRE sobre recursos `-claude-test` creados ad hoc, nunca sobre prod.

### Paso 6 · Activar y entregar

Una vez validado:

- Activar el workflow (`POST /api/v1/workflows/{id}/activate`)
- Devolver al usuario:
  - URL del workflow en el editor de la instancia
  - Resumen de qué hace y cuándo se dispara
  - Cómo monitorizar las ejecuciones (`GET /api/v1/executions?workflowId={id}`)
  - Si la instancia tiene error-workflow estándar (Operandi: `P7wPxAjFeTbElZvn` → `n8n_errors_inbox`), cablearlo en settings

---

## Patrones comunes

### Patrón 1 · Webhook → Procesar → Notificar

Para captación de leads, formularios, integraciones de CRM ligeras.

Nodos clave: `Webhook` (trigger) → `Code` / `Set` (transformar) → `Slack` / `Email` (notificar) → `Respond to Webhook` (200 OK).

### Patrón 2 · Schedule → Leer → Reportar

Para reportes diarios/semanales, recordatorios, backups.

Nodos clave: `Schedule Trigger` → `HTTP Request` / `Database` (leer datos) → `Code` (formatear) → `Slack` / `Email` (entregar).

### Patrón 3 · Evento de app → Enriquecer → Persistir

Para mantener bases de datos en sync, enriquecer leads con datos externos.

Nodos clave: `Trigger de app` (Notion, Airtable, etc.) → `HTTP Request` (Clearbit, BORME, etc.) → `Set` (componer) → `Sheets` / `Postgres` (escribir).

### Patrón 4 · Multi-canal con fallback

Para mensajería crítica que NO puede fallar.

Nodos clave: `IF` (rama principal) → `Try` (canal A: Slack) → `On error` (canal B: email) → `On error` (canal C: WhatsApp).

---

## Coordinación con otras skills

- **Si el usuario tiene un workflow ya en n8n y quiere migrar a Claude** → usar `automation-n8n-to-claude` en su lugar.
- **Si el usuario describe la automatización en términos de marketing** (envíos masivos, secuencias) → recomendar primero `marketing-email-sequence` para diseñar la secuencia, luego esta skill para construirla en n8n.
- **Si la automatización requiere scraping** → combinar con `tool-firecrawl-scraper` antes de meterlo en n8n (puede tener sentido hacerlo todo en Claude en lugar de n8n).

---

## Cuándo NO usar n8n

Antes de construir el workflow, pasar por el árbol de decisión de [`docs/tech-stack-decision.md`](../../../../docs/tech-stack-decision.md) (n8n vs servicio Python en VPS vs Claude Code + cron vs script puntual). Casos rápidos en los que conviene plantear alternativa:

- **El usuario quiere "una skill que haga X cada día"** → mejor un cron job + skill Claude directa (más simple, no requiere infra n8n).
- **El flujo es 100% texto** (resumir, reescribir, traducir) → Claude lo hace nativo, no necesita orquestador.
- **El usuario solo quiere conectar 2 SaaS conocidos** (Sheets ↔ Slack) → Zapier o Make pueden ser más rápidos de configurar.

Decir honestamente *"esto se puede montar en n8n, pero te recomendaría X porque…"* es parte del trabajo de la skill. No empujar n8n por inercia.

---

## Output esperado

Al cerrar:

- Workflow n8n desplegado y activo
- Documentación mínima del workflow en `projects/automations/<fecha>-<nombre>/README.md` con:
  - Diagrama del flujo
  - Trigger y schedule (si aplica)
  - Credenciales que requiere
  - Cómo testarlo
  - Cómo monitorizar

---

## REST API safety (al modificar workflows existentes)

Cuando usas la REST API de n8n para PATCH/PUT un workflow ya desplegado, dos reglas no negociables.

### Body PUT estricto

`PUT /api/v1/workflows/{id}` requiere un body con **exactamente** estas keys:

```json
{
  "name": "...",
  "nodes": [...],
  "connections": {...},
  "settings": {...}
}
```

Cualquier key extra (`active`, `id`, `createdAt`, `updatedAt`, `versionId`, `tags`) provoca 400 Bad Request. La instancia n8n acepta solamente esos 4 campos al actualizar. Si lees el workflow con GET primero (que incluye los campos extra), filtra antes de mandar el PUT:

```python
wf = get_workflow(id)
body = {k: wf[k] for k in ("name", "nodes", "connections", "settings")}
put_workflow(id, body)
```

### NUNCA cambiar el `type` de un trigger node

Cambiar el `type` de un trigger node (`scheduleTrigger` → `manualTrigger`, `webhook` → `scheduleTrigger`, etc.) rompe la automatización: la instancia desregistra el trigger anterior pero el nuevo queda en estado inconsistente. Síntomas: workflow activo pero nunca ejecuta, executions vacías, webhook URLs huérfanas.

Workflow correcto si tienes que migrar de un tipo a otro:

1. Crear un workflow NUEVO con el trigger deseado
2. Copiar los demás nodes y connections del workflow original
3. Activar el nuevo
4. Desactivar el viejo
5. Borrar el viejo solo cuando confirmas que el nuevo recibe ejecuciones reales

Nunca PATCH `nodes[0].type` directamente sobre un trigger en un workflow productivo.

---

## Known traps (gotchas confirmados por uso real)

Estos son traps reproducidos en workflows reales. Si construyes o editas un workflow vía REST/UI, asume que se aplican.

### Control de flujo y loops

**`splitInBatches` + `executeWorkflow` rompe el loop.** Cuando un sub-workflow se invoca dentro de un `splitInBatches`, el contador del loop se reinicia: corre 1 batch y para. Si necesitas iterar dentro de un sub-workflow, mete el loop dentro del sub-workflow o expande inline.

**Skip-branches en loops por external-state mismatch DEBEN escribir al tracker antes de volver al loop.** Si la rama "skip" del IF no actualiza el tracker (Sheets, Postgres, etc.) que detecta el mismatch, el loop reentra al mismo item infinitamente.

### Nodos concretos

**Google Sheets v4.5 READ no itera per input item** aunque `documentId` sea una expresión. Corre 1 vez evaluando con el primer item. Si necesitas leer N sheets distintos, usa un sub-workflow + executeWorkflow, o `HTTP Request` directo a Sheets API.

**Code node: `$json` es SIEMPRE el output del nodo inmediatamente anterior.** Si insertas un nodo intermedio (Set, IF, debug), las expresiones `$json.x` downstream se rompen silenciosamente porque apuntan al output del intermedio. Usa `$('Nombre del nodo').item.json.x` cuando quieras anclar a un nodo específico.

**n8n langchain `chainLlm` / `agent` vía REST con `{{ }}` en el prompt: el campo `text` DEBE empezar por `=`.** La UI auto-prefija el `=`, la REST no. Sin el prefix, el `{{ }}` se envía literal y rompe el chain.

**Postgres `executeQuery` con `queryReplacement`: NO uses `JSON.stringify` para inyectar SQL literals.** Produce `"value"` (comillas dobles = identificador) cuando querías `'value'` (comillas simples = string literal). Usa `$1, $2` con parámetros separados, o construye el SQL string manualmente con el quoting correcto.

### Imports y portabilidad

**Workflow JSON exportado de otra instancia: estructura + código sobreviven, NO transfiere:**
1. Credentials (los IDs son locales).
2. Google Sheets `documentId` (otro tenant Google).
3. Hostnames internos (`host.docker.internal`, otros containers del compose origen).

Al importar, audita estos 3 puntos y re-mapea antes de activar.

### Backfill workflows (4 traps recurrentes)

1. Webhook `responseMode=lastNode` aborta ~28s. Para backfills largos usa `onReceived` (responde antes de procesar).
2. Sheets v4.5 `appendOrUpdate` en `mappingMode=defineBelow` puede saltar filas sin error si los headers no matchean exactamente.
3. Code nodes que devuelven `[]` rompen el loop downstream silenciosamente. No es lo mismo que devolver `[{}]` o `[{empty: true}]`.
4. Nada valida orphan connections por ti (la REST acepta el JSON sin quejarse). Audita `connections` manualmente antes del PUT en workflows complejos.
