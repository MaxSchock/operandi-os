# Comprobaciones deterministas de los 15 puntos (15-10-2026)

Fase 4 nueva del plan `.claude/plans/2026-10-14-revision-cruzada-codigo.md`. Sin modelo y sin red: `scripts/revision-cruzada/comprobar.py` (solo biblioteca estándar; `ast` para Python, tokenizador propio para TypeScript/JavaScript que separa comentarios, cadenas y expresiones regulares) y `test_comprobar.py` (40 tests en verde). Los repos se leyeron en solo lectura: Linus, dashboard y operandi-services con `git archive main` en una carpeta temporal, sin tocar rama ni ficheros; Tojo en su carpeta. Hallazgos completos en `docs/revision-cruzada/<repo>/2026-10-15/comprobaciones.jsonl`.

Todo lo de abajo es señal de una comprobación, no fallo confirmado. Lo que vi en el código al ojear va marcado como «visto».

## Qué cubre cada comprobación

| Punto | Qué mira | Qué no mira |
|---|---|---|
| p03 parcial | Webhooks sin ninguna referencia a cuenta en el fichero; secreto que solo se comprueba si la variable tiene valor (`if cfg.token and x != cfg.token`) | Sesión y dueño en rutas normales, RLS, redirecciones |
| p04 | `except`/`catch` que devuelven vacío, null, 0, "" o nada sin registro; `.catch(() => null/[]/{}...)`; `suppress(Exception)`; `|| true` y `2>/dev/null` en shell. Baja a `media` si hay comentario que lo justifica y a `baja` si envuelve limpieza o conversión (`JSON.parse`, `close`, `terminate`...) | Si el llamador distingue «no hay» de «no pude» |
| p06 | `${X:-}` en compose o stack cuando el código tiene un valor por defecto (alta si el código lo pasa a número; media si lo lee con `??`, que no sustituye la cadena vacía); dos valores por defecto distintos; `service update --force` sin `--image`; `:latest`; `when` repetido en `_journal.json` | Si el despliegue verifica commit y esquema dentro del contenedor |
| p07 | `requests.*` y `urlopen` sin `timeout`; `subprocess.run` sin `timeout`; `fetch` sin `signal`; `axios` sin timeout; `while True` / `while (true)` sin salida | Acumulación de disco, memoria o filas |
| p10 | Credenciales escritas en el código (patrones `sk-`, `ghp\_`, `AIza`, JWT, `sb_secret_`...), literales asignados a variables de clave, registros que imprimen variables de clave o `os.environ`/`process.env` enteros | Secretos que llegan al prompt del modelo |
| p11 | Schedulers de APScheduler sin zona o en UTC, `CronTrigger`/`add_job('cron')` que heredan UTC, `date.today()`, `datetime.now()`/`new Date()` usados para día o semana, `toISOString().slice(0, 10)`, `cron.schedule` sin zona | Qué pasa exactamente el 25-10 y el 29-03 |
| p12 | `LIMIT n` (n>1), `limit=`, `.limit(n)`, `maxResults`, `$top`, `per_page` sin `offset`/`cursor`/`range`/`next`/`has_more` en la función (Python) o a ±40 líneas (TS); `.slice(0, n)` sobre listas | Si el recorte deja fuera a los más nuevos |
| p14 parcial | `.only` (alta), `.skip`/`xit`/`@pytest.mark.skip` (baja) en tests | Si el test entra por la puerta de producción |
| p15 parcial | `endsWith`/`startsWith`/`includes`/`slice(-N)`/`[-N:]`/`in x.lower()` sobre nombres, teléfonos, correos, hilos o carpetas. Solo «revisar» | Si dos identidades distintas pasan como la misma |

## Cifras por repo

| Repo (commit) | Ficheros | p03 | p04 | p06 | p07 | p10 | p11 | p12 | p14 | p15 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Linus `max-assistent` main (`2d5ddac2`) | 1.111 | 2 m | 245 a, 29 m, 298 b | 10 m, 59 b | 5 m, 80 b | 0 | 9 m | 13 m, 139 b | 0 | 20 r | 909 |
| `operandi-dashboardln` main (`7816f1f`) | 135 | 0 | 3 a, 7 m, 34 b | 0 | 7 m, 29 b | 1 b | 3 m | 28 m, 45 b | 0 | 0 | 157 |
| `operandi-services` main (`dab99a5`) | 249 | 25 a, 2 m | 20 a, 16 m, 22 b | 1 a, 11 m, 10 b | 13 b | 0 | 19 m | 28 m, 15 b | 0 | 1 r | 183 |
| Tojo (`clients/falkenlead/google-ads/tojo-store`) | 51 | 0 | 1 a | 0 | 1 m, 1 b | 0 | 1 m | 1 m | 0 | 1 r | 6 |

a = alta, m = media, b = baja, r = revisar. p10 no encontró ninguna credencial real escrita en el código de ningún repo.

En Linus, 255 de los 337 alta+media están en `apps/web`, y 108 de los 245 p04 alta en un solo fichero, `apps/web/src/lib/backend/real-backend.ts` (sobre todo `.catch(() => null)` y `.catch(() => [])` sobre lecturas de base). El recuento del 14-10 (162 catch vacíos o con valor por defecto) se queda corto.

**Motor de Rotary:** no tiene repo propio en local. Sus piezas son `services/content-engine-daemon/app/pipeline/share.py` y `briefs/operandi-rotary-madrid-yes.yaml` (dentro de operandi-services, ya revisados) y el receptor `wa-eventos` en VpsFigura (`/opt/wa-eventos/app.py`), que no está en local y no se revisó. **Tojo:** tampoco es un repo aparte; la fuente vive en el OS y la copia del cron (`/opt/tojo-feed` en VpsFigura) no se revisó.

## Los más graves por repo

### operandi-services

1. `services/strategist/app/main.py:330` y 23 rutas más (hasta `:745`): `if cfg.webhook_token and x_webhook_token != cfg.webhook_token`. Con `webhook_token: str = ""` por defecto (`app/config.py:36`) y `WEBHOOK_TOKEN=${WEBHOOK_TOKEN}` en el compose, si la variable falta, las rutas quedan abiertas sin autenticación (visto). Sin comprobar en el VPS si la variable está puesta. [p03, alta]
2. `services/strategist/app/main.py:818`: el webhook de Telegram, lo mismo con `telegram_webhook_secret` (visto). [p03, alta]
3. `services/strategist/docker-compose.yml:36`: `INVITE_DAILY_CAP=${INVITE_DAILY_CAP:-}` con `int(os.environ.get("INVITE_DAILY_CAP", "20"))`: revienta al arrancar si falta en `.env` (lección C2, reencontrada). [p06, alta]
4. `services/strategist/app/main.py:30`: `BackgroundScheduler(timezone="UTC")`; `:40` digest y `:281` «daily, UTC»: se mueven una hora el 25-10 (lección C1, reencontrada). [p11]
5. `services/content-engine-daemon/app/main.py:22`: `AsyncIOScheduler(timezone="UTC")` y los `CronTrigger` de `:46` a `:124`, todos en UTC. [p11]
6. `services/content-engine-daemon/app/clients/supabase.py:458`: el recuento de respuestas a comentarios devuelve 0 si la consulta falla (visto): un fallo de base se lee como «aún no he respondido». [p04, alta]
7. `services/content-engine-daemon/app/pipeline/digest.py:58` y `:102`: `except Exception: pass` (lección C9). [p04, alta]
8. `services/strategist/app/outreach/invite_dispatcher.py:181`: `except Exception: pass` en el envío de invitaciones. [p04, alta]
9. `services/strategist/app/outreach/apollo_find.py:72`: `date.today().replace(day=1)` decide el mes del cupo de Apollo en la zona del contenedor. [p11]
10. `services/*/docker-compose.yml:3` y `deploy.sh:7`: las cuatro imágenes propias en `:latest` (strategist, content-engine, video-engine, claude-debug), relacionado con «el despliegue no lleva lo que crees». [p06]

### operandi-dashboardln

1. `app/(app)/calling/page.tsx:193`: `const todayKey = new Date().toISOString().slice(0, 10)`: el «hoy» de llamadas en UTC (lección C1, reencontrada). [p11]
2. `app/(app)/videos/page.tsx:71` y `:118`: la semana se calcula en UTC (lección C1). [p11]
3. `app/(app)/admin/page.tsx:14` `.limit(50000)`, `app/(app)/dashboard/page.tsx:24/30/37` `.limit(10000/50000/20000)`: si el proyecto de Supabase tiene el tope de filas por defecto de la API, llegan menos filas de las pedidas y sin aviso. Sin comprobar en el proyecto. [p12]
4. `app/(app)/calling/page.tsx:125-139`: seis consultas con `.limit(800)` a `.limit(3000)` sin paginar. [p12]
5. `app/(app)/activity/page.tsx:48`: `lead_events` con `.limit(300)`. [p12]
6. `components/video-staged.tsx:139`: `fetch(...).catch(() => null)`: un fallo de red se lee como «sin datos». [p04, alta]
7. `app/api/admin/content-generate/[slug]/route.ts:100`, `dm-proposal/[id]/route.ts:95`, `override/[action]/route.ts:54`: llamadas del servidor al daemon y al strategist sin timeout. [p07]
8. `lib/calling-server.ts:42`: `fetch` del servidor sin timeout. [p07]
9. `lib/date-range.ts:101`: los días del rango se generan con `toISOString().slice(0, 10)`. [p11]
10. `lib/calling.ts:308`: `catch { return ""; }` en `localTime` con una zona no válida: impacto menor. [p04]

### Linus (`max-assistent`, main)

1. `apps/web/src/lib/backend/chat-lesen.ts:209-210`: `tel.endsWith(ziffern)` y `tel.slice(-9) === ziffern.slice(-9)`: identidad por los últimos 9 dígitos (es el `chatFuer` de la clase 1, reencontrado). [p15]
2. `apps/web/src/lib/backend/real-backend.ts:8201` y `:8203`: `klein.includes(name.toLowerCase())` con nombres de 3 letras y apellidos de 4: «Max» casa con «Maximal» (visto). [p15]
3. `apps/web/src/lib/backend/real-backend.ts:1743`, `:1751`, `:1778`: `cards.load(cardId).catch(() => null)`: un fallo de base se lee como «no hay tarjeta». Uno de los 108 del fichero. [p04, alta]
4. `apps/server/src/engine/agent-loop.ts:1094`: `namenPruefen(...).catch(() => null)`: el control del nombre del destinatario se queda sin veredicto si falla. [p04, alta]
5. `packages/domain/src/db/repositories/contacts.ts:113`: la transacción de reemplazo de contacto devuelve `false` ante cualquier error, igual que cuando pierde la carrera (visto). [p04, alta]
6. `deploy/stack.instance.yml:108` y `deploy/stack.demo.yml:145`: `MAX_PUSH_KONTAKT: "${MAX_PUSH_KONTAKT:-}"` con `env["MAX_PUSH_KONTAKT"] ?? "mailto:..."` (`apps/web/src/lib/backend/push.ts:73`): sin la variable, el contacto de las notificaciones es "" y no el valor por defecto (visto). [p06]
7. `apps/web/src/lib/agent/speicher.ts:411` y `:437`: el día del consumo por dispositivo del agente es el día en UTC: el contador diario cambia a las 02:00 de Berlín en verano. [p11]
8. `deploy/compose.yml:25` y `:55`: `ollama/ollama:latest` y `cloudflare/cloudflared:latest`; `deploy/stack.demo.yml:11` `faster-whisper-server:latest-cpu`. [p06]
9. `deploy/deploy.sh:215`: el guion imprime como instrucción `docker service update --force ${svc}_web` sin `--image`. [p06, media]
10. `apps/web/src/app/api/chat-eingang/[pfad]/route.ts:11` y `apps/web/src/app/api/telefon/talkpilot/[pfad]/route.ts:16`: webhooks sin referencia a cuenta en el fichero de la ruta; el filtro puede estar en `chat-eingang.ts` (a Opus, abajo). [p03]

### Tojo

1. `sincronizar_feed.py:132`: `hoy = datetime.date.today().isoformat()`: el «hoy» del cron en la zona del servidor. [p11]
2. `revision-2026-10-05/construir_filas.py:18`: `except Exception: return False`. [p04]
3. `revision-2026-09-29/pull_ads.py:12`: consulta de Google Ads con `LIMIT 1000` sin paginar. [p12]
4. `revision-2026-10-01/captura-devtools-cdp.py:9`: `urlopen` sin timeout (guion de una sola vez). [p07]
5. `revision-2026-10-05/crear-borrador.py:19`: remitente reconocido con `"seybold" in From.lower()`. [p15]

## Falsos positivos que vi y el ajuste

Ya corregidos en el guion (los recuentos de arriba son posteriores a cada corrección):
- p10: URLs con «sk-» en mitad de una ruta (`briefs/operandi-madeleine-scholl.yaml:229-235`) salían como claves: se exige que el patrón no vaya pegado a una letra o número. `TOKEN_URL = "https://..."` salía como literal de clave: se excluyen nombres acabados en URL, URI, path o host y valores que empiezan por `http`.
- p06: `${X:-}` en guiones de shell es el uso normal con `set -u`: solo se mira en compose, stack y `.env`. Los conmutadores `"${MAX_ARBEITER:-aus}"` frente a `env[...] ?? ""` salían como «dos valores distintos»: se ignora el valor vacío del código.
- p04: `return {"ok": False, "reason": ...}` dentro del `except` sí avisa al llamador (`content-engine-daemon/app/postactions.py:226`): ya no cuenta. `.catch(() => {})` sobre `terminate`, `destroy`, `mkdir`, registros de protocolo y lecturas de `res.text()`/`res.json()` del cuerpo de error bajan a `baja`.
- p03: las rutas de admin del dashboard salían como webhooks por la cabecera `x-webhook-token`: la palabra «webhook» solo cuenta en la ruta o en comentarios.
- p11: `naechsterTag` de `apps/server/src/engine/werktage.ts:83` hace aritmética de fechas en UTC a propósito: se ignora cuando hay `setUTC`, `getUTC` o `T00:00:00Z` a 6 líneas.
- p12: valores por defecto de parámetros (`limit = 20` en una firma) los decide el llamador: fuera.
- p15: listas constantes en mayúsculas (`DOKUMENT_TOOLS.includes`) y comprobaciones de un carácter (`includes("@")`): fuera.

Siguen saliendo, con el ajuste que los quitaría (no aplicado, por no esconder casos reales):
- `operandi-services/services/content-engine-daemon/app/.staging-p0/` está en git y duplica 7 hallazgos de `app/`. Ajuste: borrarla si ya no sirve (otra sesión) o un `comprobar.ignore` en ese repo con `services/content-engine-daemon/app/.staging-p0/`.
- p03: los webhooks de Telegram (`strategist/app/main.py:807`) y de errores de n8n (`claude-debug/app/main.py:48`) son de un solo dueño y salen por «sin cuenta». Ajuste: aplicar la regla de cuenta solo a ficheros que nombran un proveedor de varias cuentas (Unipile, Evolution, Chatwoot, WhatsApp).
- p04: `operandi-dashboardln/lib/supabase/server.ts:52` es el `catch {}` de la plantilla de Supabase para cookies en Server Components. Ajuste: ignorar el `catch` dentro de `setAll`. `# noqa: BLE001` cuenta como comentario que lo justifica (sube a `media` en vez de `alta`); decidir si se quiere así.
- p06: un valor vacío que el código corrige después (`MAX_DIAGNOSE_TTL_STUNDEN`: `Number("")` es 0 y la guarda `raw > 0` devuelve 48) sigue saliendo. Ajuste: buscar en la misma función una guarda `> 0`, `.trim()` o `||`.
- p12: los «últimos N» deliberados (`list_recent_revisions(slug, limit=24)`) salen como `media`. Ajuste: bajar a `baja` si la función o la llamada se llama `recent`, `last`, `latest` o `top`.
- p15: `correlationId.slice(-6).toUpperCase()` en `packages/domain/scripts/trace.ts` y `confirmations-list.tsx:36` es un id corto para mostrar. Ajuste: ignorar cuando el resultado va directo a `toUpperCase()` o a un texto.
- p07: el 80 % de los `fetch` sin `signal` de Linus y del dashboard son del navegador a la propia API (salen como `baja`).

## Para agente Opus (paquete y punto concretos, nunca un barrido)

| Punto | Paquete | Qué preguntar |
|---|---|---|
| 1 | `operandi-services/services/strategist/app/outreach/invite_dispatcher.py`, `calling.py` | Si un tick solapado o un reintento puede mandar dos veces la misma invitación o mensaje; de dónde sale el destinatario |
| 1 | `operandi-services/services/content-engine-daemon/app/pipeline/publish.py`, `share.py` (Rotary) | Doble publicación o doble WhatsApp al grupo si el proceso se reinicia entre enviar y marcar |
| 1 | Linus `apps/web/src/lib/backend/zustellung.ts`, `kartenbau/empfaenger.ts` | Clave de idempotencia por envío; destinatario que sale del modelo o del texto citado |
| 1 | `operandi-dashboardln/app/api/admin/dm-proposal/[id]/route.ts` | Doble clic en aprobar = dos DM |
| 2 | Linus `apps/web/src/lib/backend/durchlauf.ts` (el `:132` conocido), `abgleich-lauf.ts` | Cursores y «visto» guardados antes de terminar |
| 2 | `content-engine-daemon/app/pipeline/comments.py`, `digest.py`; Tojo `sincronizar_feed.py` (`feed-estado.json`) | Qué se pierde si muere justo después de marcar |
| 3 | `operandi-dashboardln/app/api/**/route.ts` y `middleware.ts` | Sesión y filtro por cliente también en rechazar y deshacer; ids del cuerpo |
| 3 | Linus `apps/web/src/app/api/chat-eingang/[pfad]/route.ts` con `chat-eingang.ts`, y `telefon/talkpilot/[pfad]/route.ts` | Si el webhook filtra la cuenta o instancia antes de actuar |
| 3 | `operandi-services/services/strategist/app/main.py` (las 25 comprobaciones de los puntos 1 y 2 de arriba) | Confirmar en el VPS que `WEBHOOK_TOKEN` y `TELEGRAM_WEBHOOK_SECRET` están puestos, y si la comprobación debe fallar cerrada |
| 5 | Linus `packages/domain/src/db/repositories/*` y las aprobaciones de `real-backend.ts` | Escrituras dobles fuera de transacción y lectura-escritura sin condición de estado |
| 5 | `content-engine-daemon/app/postactions.py`, dashboard rutas de admin con varias escrituras a Supabase | Lo mismo |
| 8 | `operandi-services/services/*/app` y dashboard `components/*-form.tsx` | Cada «enviado», «ok», «publicado»: la prueba del efecto que lo respalda |
| 9 | Linus `apps/server/src/engine/agent-loop.ts` (destinatario, fecha, importe del modelo), `content-engine-daemon/app/pipeline/process.py`, `video-engine/app/dialogue.py` | Qué campo del modelo se usa sin contrastar con la fuente |
| 13 | Linus entero | Determinista con herramienta (exportaciones sin uso con `knip` o `ts-prune`), no con modelo; no se hizo porque instala dependencias. A Opus solo las acciones del manifiesto sin ejecutor y las rutas tapadas por `middleware.ts` |
| 14 | Linus `packages/gatekeeper` y los tests de `apps/web/src/lib/backend` | Si entran por la puerta de producción y si se ponen rojos al quitar cada pieza del arreglo (la parte mecánica, `.only`/`.skip`, dio 0 alta) |
| 15 | Linus `chat-lesen.ts:209-210`, `real-backend.ts:8201-8203`, `kartenbau/faden.ts:183,242`, `packages/domain/src/karten-arten.ts:97`, `packages/domain/src/playbook/auswahl.ts:134,138`; Tojo `crear-borrador.py:19` | Un par real distinto que pase como el mismo |
| 4 | Linus `real-backend.ts` (108 `.catch` silenciosos) | No hace falta Opus para encontrarlos; sí para decidir, por familia (lectura de tarjeta, memoria, contactos), si el llamador debe distinguir «no hay» de «no pude» |

## Cómo repetirlo

```bash
python3 scripts/revision-cruzada/comprobar.py ~/max-assistent --ref main --nombre linus
python3 scripts/revision-cruzada/comprobar.py /mnt/c/Users/PC/operandi-dashboardln --ref main --nombre operandi-dashboardln
python3 scripts/revision-cruzada/comprobar.py ~/src/operandi-services --ref main --nombre operandi-services
python3 scripts/revision-cruzada/comprobar.py clients/falkenlead/google-ads/tojo-store --nombre tojo-store
```

Tarda menos de 6 segundos por repo. Más detalle en `scripts/revision-cruzada/README.md`.
