# Los fallos que más se repiten en los desarrollos (agosto a octubre de 2026)

Hecho el 14-10-2026 por un agente de lectura (Opus) sobre: los «Why» de las ~60 reglas de memoria que hablan de código, las revisiones de Codex y propias de Linus, los 382 commits de arreglo de Linus desde agosto (40 % de 962), las secciones de fallos de 264 registros de sesión, y los gotchas y CLAUDE.md de Operandi (dashboard, strategist, video-engine, content-engine), Suritec y n8n. Las cifras son aproximadas; la columna de registros sale de un grep ruidoso.

## A. Clases de error por frecuencia

| # | Clase | Reglas | Fix Linus | Revisiones | Ejemplos | Proyectos |
|---|---|---|---|---|---|---|
| 1 | Identidad por texto aproximado (nombres, teléfonos, direcciones, hilos, claves truncadas) | 3 | ~30 | ~10 | `namenPassen` toma {max} ⊂ {max,mustermann}; `chatFuer` compara los últimos 9 dígitos; un barrido por nombre exacto dejó 14 nodos de n8n sin arreglar | Linus, n8n Operandi, Apify |
| 2 | Fallo silencioso (error tragado o leído como «no hay nada») | 8 | ~20 | ~10 | vídeo de Cardeleine sin voz 14 días (11 $); `SELECT … LIMIT 1` para el flujo sin avisar; el Tagesstart marca el día hecho antes de leer | todos |
| 3 | Se afirma un estado que no es real («enviado», «hecho») | 5 | ~24 | ~8 | `5e8ce5ca` «deja de decir enviado cuando no lo está»; dashboard 03-09: 12 escrituras con éxito sin filas cambiadas | Linus, dashboard, n8n (Sheets) |
| 4 | Concurrencia y escrituras no atómicas | 3 | ~15 | ~15 | compensación que restaura la tarjeta anterior cuando la nueva ya está aprobada; dos ejecuciones paralelas envían dos veces (Operandi 03-06) | Linus, n8n, dashboard |
| 5 | Duplicados e idempotencia | 4 | ~16 | ~8 | Tagesstart relanzado cada 60 s; «Hilf mir» duplicaba borradores al recargar; doble envío en «llamada primero» (30-09) | Linus, Operandi, content-engine |
| 6 | Despliegue o configuración que no llega al contenedor | 9 | ~13 | ~6 | deploy del video-engine que no reinicia; PG_DSN vacío en Suritec; migraciones Drizzle con `when` repetido | Linus, video-engine, Suritec, n8n |
| 7 | Salida del LLM usada sin validar | 5 | ~18 | ~3 | n8n sin `=`: 13 prospects quemados; asunto inventado por el modelo (`5aea4cc3`) | Linus, n8n, Hemmersbach, Apify |
| 8 | Tests que no prueban el camino real | 9 | ~14 | 2 | un test que rodea la puerta (`task.close`); «a test that only passed on the day it was written» (`359a42a7`) | Linus |
| 9 | Fechas, zonas horarias y cambio de hora | 4 | ~14 | ~6 | 02:30 del día del cambio pasa a 03:30; el día cambiaba a la medianoche del contenedor (`97c99616`); Chatwoot con un `AT TIME ZONE` da 4 h mal | Linus, Suritec, Evolution, n8n |
| 10 | Topes fijos que recortan sin avisar | 4 | ~11 | ~7 | 250 eventos sin paginar leídos como «libre»; 500 playbooks, 450 perdidos sin error | Linus, Evolution, MCP Drive, n8n |
| 11 | Funciones a medio cablear (prometidas, inalcanzables en producción) | 2 | ~11 | ~8 | webhook detrás del middleware, cinco controles que nunca corrieron; «la aprobación por voz NUNCA funcionó» (`254516ac`) | Linus |
| 12 | Envío al destinatario, hilo o canal equivocado | 3 | ~12 | ~4 | borrador dirigido al propio jefe (`37cabed3`); test E2E desde el dominio de otra entidad | Linus, Operandi, Hemmersbach |
| 13 | Intención o tipo decidido por palabras clave y listas cerradas | 3 | ~12 | ~3 | `VERWERFBARE_KINDS`; carpeta de borradores reconocida por el nombre | Linus |
| 14 | Secretos expuestos | 8 | ~6 | 2 | `erneuerung` en declaraciones de conector; `WA_ACCESS_TOKEN` por inspect; contraseña de Redis en `docker events` | Linus, Suritec, Goldspitze, VpsFigura |
| 15 | Autorización y aislamiento entre clientes | 3 | ~3 | ~12 | 21 tablas con SELECT/DELETE para `anon` sin RLS (03-09); rechazar y deshacer no miraban el dueño; `?from=` aceptaba cualquier URL | Dashboard, Supabase, Linus |
| 16 | Sin timeout ni presupuesto | 2 | ~3 | ~6 | compilaciones que tumbaron tres bases; ninguna llamada a proveedor con timeout; un mensaje de 100.000 caracteres = 65 h de latido | Linus, ki-prod-01, n8n |

## B. Cómo buscar cada clase

(1) búsqueda mecánica, (2) pregunta que el revisor se hace sobre cada fichero.

1. **Identidad por texto.** (1) `\.includes\(|startsWith\(|endsWith\(|\.slice\(-?\d+|\.substring\(0, *\d+\)`; Python `in .*\.lower\(\)`. (2) ¿Esta comparación decide que dos personas, mensajes, hilos o carpetas son lo mismo? Da un par distinto real que la pase.
2. **Fallo silencioso.** (1) `catch\s*(\(\w*\))?\s*\{\s*\}`, `\.catch\(\(\) *=> *(null|undefined|\[\]|\{\})\)`, `except…: pass|continue|return None`, `>/dev/null 2>&1`, `\|\| true`, `continueOnFail|alwaysOutputData`. Recuento del 14-10: 162 catch vacíos o con valor por defecto en Linus, 27 except silenciosos en operandi-services. (2) Si falla, ¿quién se entera, y en qué se distingue «no hay nada» de «no pude mirar»?
3. **Estado afirmado.** (1) literales `sent|done|erledigt|gesendet|enviado|ok: true` tras una llamada a proveedor o base. (2) ¿Se apoya en una prueba del efecto (filas, id del proveedor, relectura) o solo en que no lanzó?
4. **Concurrencia.** (1) dos o más `await .*\.(insert|update|delete|save|create|upsert)\(` fuera de `transaction(`; lectura seguida de update sin `WHERE estado=` ni `FOR UPDATE`. (2) Si muere entre N y N+1 o entra otra petición, ¿qué queda y quién lo repara?
5. **Duplicados.** (1) cada `send|publish|createDraft|sendMessage|/messages|chat.post` dentro de reintentos, crones, latidos o `setInterval`, sin clave de idempotencia ni `ON CONFLICT`. (2) Si corre dos veces, ¿qué sale dos veces?
6. **Despliegue.** (1) `${X:-}` en compose cruzado con `environ.get("X", default)` en código; `service update --force` sin `--image`; `:latest`; `when` repetidos en `_journal.json`. (2) Tras desplegar, ¿cómo sabe el guion que el contenedor corre este commit, estas variables y este esquema?
7. **Salida del LLM.** (1) `messages.create|chat.completions|responses.create|generateContent` cuyo resultado alimenta `to|recipient|date|amount|id|thread`. (2) ¿Qué campo se usa sin contrastar con la fuente?
8. **Tests.** (1) en `*.test.*`: `connector.execute(|undoInternalEffect(|executor.`, `as any|as unknown as`, `.skip|.only`, dobles con campos que la interfaz no declara. (2) ¿Entra por la misma puerta que producción? ¿Se pone rojo si quito el arreglo pieza a pieza?
9. **Fechas.** (1) `toISOString().slice|split`, `getUTC(Date|Day)`, `datetime.now()` sin zona, `utcnow()`, `date.today()`, `timezone="UTC"` junto a CEST/CET, `86400000`, un solo `AT TIME ZONE`. (2) ¿En qué zona está el «hoy»? ¿Qué pasa el 29-03, el 25-10 y entre 00:00 y 02:00 de Madrid o Berlín?
10. **Topes.** (1) `LIMIT \d+`, `limit: \d+`, `.slice(0, N)`, `[:N]`, `maxResults|pageSize|per_page|top=`. (2) Si hay más, ¿pagina, avisa o pierde el resto? ¿Siempre los más viejos?
11. **Medio cablear.** (1) exportaciones sin llamadas fuera de tests; acciones del prompt o manifiesto sin ejecutor; rutas tapadas por el middleware. (2) ¿Lo prometido tiene camino alcanzable hasta el efecto?
12. **Destinatario.** (1) origen de `to|chat_id|recipient|thread|inReplyTo`: si sale de `req.body` o del modelo, marcar. (2) ¿Puede acabar en el propio usuario, en un grupo, en un tercero citado o desde el dominio de otra entidad?
13. **Palabras clave.** (1) `new Set([...kind`, `kind === "`, `/\b(ja|nein|yes|no)\b/i`, nombres de carpeta con `endsWith`. (2) ¿Qué entrada válida nueva se queda fuera?
14. **Secretos.** (1) `sk-|at-|ghp\\_|xox[bp]-|AIza|eyJ|sb\\_secret\\_`, `console.log(.*(token|key|secret|pass)`, `print(os.environ`, `redis-cli -a`, cuerpos enteros en registros. (2) ¿Algún registro, error o prompt puede llevar una credencial o datos de otro cliente?
15. **Autorización.** (1) rutas sin sesión; `where id =` sin dueño; redirecciones; webhooks que confían en ids del cuerpo; tablas sin RLS. (2) ¿Quién puede llamar esto y sobre qué filas? ¿Rechazar y deshacer miran el dueño igual que aprobar?
16. **Sin techo.** (1) `fetch(` sin `signal`, `requests.` sin `timeout=`, bucles sobre entradas externas sin límite. (2) ¿Qué cota tiene en tiempo, memoria y llamadas con la peor entrada realista?

## C. Lecciones de un proyecto que no constan aplicadas en otros

1. **Zona horaria por trabajo** (Linus `97c99616`, regla de APScheduler): el strategist tiene `config.py:61` `digest_hour_utc = 8  # 09:00 CEST` y `main.py:30` `BackgroundScheduler(timezone="UTC")`. Desde el 25-10 el resumen sale a las 08:00 de Madrid y la franja de invitaciones (`INVITE_WINDOW_START_UTC=6`, `END=16`) se mueve una hora. El dashboard calcula el «hoy» en UTC: `app/(app)/calling/page.tsx:193` y `videos/page.tsx:68-71`.
2. **Variable vacía del compose pisa el valor por defecto** (video-engine, arreglado en `render.py:50-53`): el strategist tiene `docker-compose.yml:36` `INVITE_DAILY_CAP=${INVITE_DAILY_CAP:-}` y `config.py:111` `int(os.environ.get("INVITE_DAILY_CAP", "20"))`. Sin la variable en el `.env`, `int("")` revienta al arrancar. Sin comprobar en el VPS.
3. **Marcar «ya visto» antes de procesar** (Hemmersbach 24-08, 5 clientes sin respuesta): no se convirtió en regla; reapareció en Linus el 09-10 (`durchlauf.ts:132`, cursor guardado antes de procesar; `88a2cfaa` lo trata en parte).
4. **Bloqueo atómico antes de enviar** (Operandi 03-06): solo en los gotchas de Operandi; volvió en «llamada primero» (30-09) y en T8 (aprobar y corregir a la vez).
5. **Webhook sin `account_id`** (Unipile, 66 % de ejecuciones con cuenta ajena): Linus lo repitió el 31-08 (C-25).
6. **«Éxito» no es «guardado»** (Sheets 19-05): volvió en el dashboard 03-09 y en Linus `5e8ce5ca`.
7. **Revisión de Codex antes de desplegar** nació en Linus; no consta en `operandi-dashboardln/CLAUDE.md` ni existe CLAUDE.md en `operandi-services`. El 30-09 se desplegaron «llamada primero» y el motor de Cardeleine sin revisar; Codex encontró después 7 y 5 fallos reales.
8. **RLS en Supabase**: la brecha del 03-09 se contuvo quitando permisos; `clients/kisult/context/brief.md` sigue con «RLS OFF · Security advisory pendiente». No consta cambiar los privilegios por defecto: una tabla nueva volvería a quedar abierta. Sin comprobar en la base.
9. **Errores a una bandeja, no tragados** (Linus F-02, F-12): en operandi-services siguen 27 `except` silenciosos (`content-engine-daemon/app/pipeline/digest.py:58,102,135`, `learn.py:157,461,469`); `strategist/app/main.py:47` solo deja un warning si el resumen no se programa. video-engine y claude-debug tienen 0 tests; el dashboard 0 unitarios.
10. **La receta de `hasPrefix` para comprobar variables en Swarm no funciona** (`reference-docker-inspect-sin-hasprefix`, 14-09; confirmado otra vez el 14-10 en esta sesión). El CLAUDE.md global, en «Privacidad y secretos», sigue recomendándola. Lo que funciona: `docker service inspect <svc> --format '{{range .Spec.TaskTemplate.ContainerSpec.Env}}{{println .}}{{end}}' | cut -d= -f1 | grep -c '^VAR$'`.

## D. Lista para el revisor automático, por daño

1. **Un mensaje sale dos veces o a quien no toca.** Revisa cada punto que envía, publica o crea un borrador. Si puede correr dos veces sin clave de idempotencia, márcalo. Si el destinatario, el hilo o el chat salen del cuerpo de la petición, de la respuesta del modelo o del texto citado, márcalo.
2. **Se marca «hecho» antes de hacerlo y el fallo se pierde.** Busca cursores, hashes de «ya visto», marcadores del día o reclamos guardados antes de terminar el trabajo que protegen. Di qué se pierde si el proceso falla justo después.
3. **Datos accesibles por quien no debe.** Por cada ruta, webhook o consulta: sesión, filtro por dueño o cliente (también en rechazar y deshacer), redirecciones abiertas, ids del cuerpo, tablas sin RLS.
4. **Errores que nadie ve.** Cada catch o except que devuelve vacío, null u «ok», y cada salida silenciada: ¿distingue «no hay» de «no pude»? ¿Llega a un aviso?
5. **Escrituras a medias y carreras.** Dos o más escrituras fuera de transacción, o lectura y escritura sin condición de estado: ¿qué queda si muere en medio o entra otra petición?
6. **El despliegue no lleva lo que crees.** `${X:-}` con valor por defecto en código, `--force` sin `--image`, `latest`, migraciones con `when` repetido, guiones que no verifican commit y esquema dentro del contenedor.
7. **Trabajo sin techo.** Llamadas sin timeout, bucles sin límite, acumulación de disco, memoria o filas sin limpieza.
8. **El sistema dice algo que no ha pasado.** Por cada texto de éxito y cada capacidad prometida, la prueba del efecto que lo respalda.
9. **Se fía de lo que dice el modelo.** Cada campo del LLM que decide destinatario, fecha, importe, id o tarjeta, contrastado con la fuente.
10. **Claves en registros o en el prompt.** Patrones de credenciales, cuerpos enteros en registros, variables impresas, contraseñas como argumento, secretos que llegan al modelo.
11. **Horas y días en la zona equivocada.** Cada «hoy», «semana», «medianoche» o cron: zona, y qué pasa el 29-03, el 25-10 y de 00:00 a 02:00.
12. **Topes que esconden datos.** Cada `LIMIT`, `slice` o tamaño de página: ¿pagina, avisa o pierde? ¿Deja fuera a los más nuevos?
13. **Funciones prometidas pero muertas.** Exportaciones sin llamadas, acciones sin ejecutor, controles que el camino real se salta, rutas tapadas por el middleware.
14. **Tests verdes que no prueban.** ¿Entra por la puerta de producción? ¿Cada pieza del arreglo tiene un test que se pone rojo al quitarla?
15. **Identidad o intención por texto aproximado.** Subcadena, prefijo, últimos N dígitos, nombre de carpeta, lista de palabras, conjuntos cerrados de tipos: un caso real que pasaría como igual o quedaría fuera.
