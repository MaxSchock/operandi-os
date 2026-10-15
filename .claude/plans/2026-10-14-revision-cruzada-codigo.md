# Plan: revisión cruzada de todos los desarrollos con la lista de fallos repetidos

Estado 15-10-2026 (decisión de Max, vía sesión 51): el pase ancho barato se abandona. Tres humos sobre el gatekeeper de Linus (DeepSeek v1 72 % ruido, DeepSeek v2 100 %, Qwen3 Coder 89 %) y ninguno reencuentra el fallo real; un agente revisando a otro no separa señal de ruido, y lo que se puede dibujar como árbol de decisión va a un workflow determinista, no a un agente (`projects/investigacion-reels-2026-10-14/charlas-construir-con-ia-2026-10-15/aprendizajes.md`, «Segunda lectura»). Fases 2 y 4 tal como estaban: FUERA, nada más de dinero en DeepSeek/Qwen para esto (gasto total 0,026 $). Fase 3: el fallo confirmado del gatekeeper (`gatekeeper.ts:114/152`) se arregla ya con el test rojo escrito, suite, canario y escalera (sesión de Linus, tras el bloque D). Fase 4 nueva: los 15 puntos del apartado D se convierten en comprobaciones deterministas (grep, AST o tests) en `scripts/revision-cruzada/`, sin modelo, y se corren en todos los repos; lo que no se pueda expresar así va a un agente Opus sobre el paquete y el punto concretos, nunca un barrido. Fase 5 HECHA el 15-10 (los diez puntos; ver cada uno). Fase 6: ledger, reglas indexadas, working-memory e informe a Max hechos el 15-10. El filtro de proveedores de OpenRouter ya no hace falta para este plan. Antes: fase 0 hecha el 14-10 (inventario de patrones), fase 1 hecha (corredor), fase 2 parada dos veces.
Entidad: transversal (Linus es KIsult/RHP; dashboard, strategist, content-engine y video-engine son Operandi; Rotary es personal).
Para quién: Max. Para qué: que lo aprendido en un proyecto se compruebe en todos, con un pase barato en anchura y un modelo fuerte solo sobre lo señalado.
Origen: Max, 14-10: «¿hay tareas muy pesadas de revisión que no hemos hecho por coste?» y «revisar si hemos respetado lo que hemos aprendido en un proyecto también en todos los demás».

## Decisiones ya tomadas

- Modelo del pase ancho: uno barato de pago en OpenRouter (DeepSeek V3.2 o Qwen3 Coder, ~0,30 $/M tokens de entrada), no un gratuito: sin registro de datos por el proveedor y mejor que los gratuitos. Coste estimado por pase completo de Linus: 0,5 $ (1,1 M tokens de código). Tope por pase: 3 $.
- Los gratuitos solo para resúmenes y clasificaciones sin código de cliente.
- Nada de datos reales de clientes (transcripts, correos) en el pase: solo código y tests.
- Verificación de hallazgos: Opus (agente con `model: opus`) o Codex en solo lectura. Cada hallazgo acaba en un arreglo con test o se descarta por escrito; nunca un informe sin dueño.
- Lista de búsqueda: los 15 puntos del apartado D de `patrones-de-error-2026-10-14.md`, ordenados por daño.

## Fase 0: inventario de patrones (hecha 14-10)

`docs/revision-cruzada/patrones-de-error-2026-10-14.md`: 16 clases, cómo buscarlas, 10 lecciones no trasladadas entre proyectos, lista de 15 puntos.

## Fase 1: el corredor del pase

**Hecha 14-10-2026 20:05 (subagente, 0,5 h):** `scripts/revision-cruzada/pasar.py` + `test_pasar.py` (17 en verde) + `README.md`. Prueba en seco sobre gatekeeper: 4 trozos, ~25.000 tokens, 0,009 $ (peor caso 0,019 $) con `deepseek/deepseek-v3.2` a tarifa real de `/models`; `apps/server/src` en seco: 69 trozos, ~0,20 $. Cada petición lleva `provider.data_collection: deny` además del filtro de cuenta. Pase real pendiente de T6 (filtro OpenRouter de Max); comando listo en el README. Resultado seco en `docs/revision-cruzada/linus-gatekeeper/2026-10-14/seco.txt`.

Script `scripts/revision-cruzada/pasar.py` (Python, en el OS):
- Entrada: ruta del repo, lista de extensiones, modelo, tope de gasto.
- Trocea por fichero (y por módulo cuando el fichero pase de 60 KB), adjunta los imports del mismo paquete que quepan y la lista de 15 puntos.
- Pide al modelo JSON estricto: `[{punto, fichero, linea, resumen, escenario_de_fallo, confianza}]`. Rechaza salidas que no sean JSON válido y reintenta una vez.
- Guarda en `docs/revision-cruzada/<repo>/<fecha>/hallazgos.jsonl` y un `coste.txt` (tokens y dólares por fichero). Para en seco al llegar al tope.
- Prueba de humo: `packages/gatekeeper/src` de Linus (30 KB) y comparar a ojo.
- Antes de correr: Max activa en OpenRouter «solo proveedores sin registro de datos» (ajustes de privacidad de la cuenta). Comprobar con una petición que el modelo elegido sigue disponible.

## Fase 2: pase sobre Linus

**15-10-2026 (subagente, 0,4 h): parada antes del pase.** Comparación a ojo de la prueba de humo (gatekeeper, 0,0085 $): 2 reales (el mismo fallo: metadatos analizados pero no tapados, `gatekeeper.ts:114/152`), 3 dudosos, 13 ruido (72 %). Gasto del pase de Linus: 0 $. Propuesta de ajuste del prompt y detalle en `docs/revision-cruzada/linus-gatekeeper/2026-10-15/comparacion-a-ojo.md`. Siguiente: aplicar el ajuste en `pasar.py`, repetir humo, y solo con ruido por debajo de la mitad lanzar el pase.
**15-10-2026, segunda vuelta: tampoco se lanza el pase.** Seis reglas y campo `linea_prueba` (con descarte, `descartados.jsonl`) aplicados en `pasar.py`, 20 tests en verde. Humo v2 DeepSeek: 6 hallazgos, 100 % ruido, 0,0081 $ (`linus-gatekeeper-v2/2026-10-15/`). Humo Qwen3 Coder: 9 hallazgos, 89 % ruido, 0,0092 $ (`linus-gatekeeper-qwen/2026-10-15/`). Ninguno encuentra el real de la v1. Gasto del pase de Linus: 0 $. Decisión pendiente: el pase ancho barato no separa señal de ruido en este código; ver informe.

Seis paquetes (`apps/web/src`, `apps/server/src`, `packages/*/src`, tests de web aparte). Después: agrupar por punto, quitar duplicados, ordenar por daño. Salida: `docs/revision-cruzada/linus/<fecha>/triaje.md` con las 30 sospechas más graves.

## Fase 3: verificación y arreglos en Linus

**Estado 15-10 13:10:** el fallo real del gatekeeper está arreglado en la rama `gatekeeper-meta-getrennt` (sha `c417a128`, en origin, CI run 38718488460 en marcha). Test rojo primero (comprobado: 2 de los 3 tests nuevos fallan sin el arreglo), verde con él; suite del gatekeeper 56/56, privacy-suite, tsc de domain y gatekeeper limpios. Cambio: `ingest` pasa `findings` por el contenido y por cada metadato (remitente, asunto, nombre de adjunto) por separado; `redactedContent` solo lleva los tramos del cuerpo y el nuevo campo opcional `GatekeeperDecision.redactedMeta` devuelve cada metadato tapado donde lo necesitaba (`packages/domain/src/contracts/gatekeeper.ts`). Los llamadores (`chat-lesen.ts:142`, `klassifizieren.ts:87`, `real-backend.ts:6222`) no cambian: dejan de recibir un cuerpo con marcador ajeno; usar `redactedMeta` para enseñar el remitente tapado queda como mejora. Falta: CI, canario (guion de lectura de chat tras desplegar), main.
PARADO 15-10 13:05 por orden de Max (consumo del plan): se retoma junto con el bloque D de Linus; pasos en el plan del tirón, sección D. CI de `c417a128` VERDE (run 38718488460, leído 13:20 al cerrar).

- **Primera (de la prueba de humo, comprobada al ejecutar):** `packages/gatekeeper/src/gatekeeper.ts:114/152`: `ingest` analiza contenido+remitente+asunto+nombre de adjunto pero solo tapa `content`, con los tramos del texto unido. Efecto: el remitente sigue en claro y el contenido gana un marcador que no le toca. Test que lo demuestra: `ingest({ content: "Hallo, bitte zahlen.", kind: "chat", meta: { sender: "DE89 3704 0044 0532 0130 00" } })` debe devolver `redactedContent === "Hallo, bitte zahlen."` y el remitente tapado (hoy: `"Hallo, bitte zahlen.[Kontonummer entfernt]"` y remitente intacto). Llamadores: `chat-lesen.ts:142`, `klassifizieren.ts:87`, `real-backend.ts:6159`.

Agente Opus o Codex en solo lectura sobre las 30: CONFIRMADO / PLAUSIBLE / DESCARTADO con la prueba. Lo confirmado se arregla en bloques de una sesión con test rojo primero, suite del paquete, canario y subida por la escalera (canario, Tobi, André, Jonas) según las reglas de Linus.

## Fase 4: pase sobre los demás repos

**Hecha 15-10-2026 (subagente, ~1,3 h):** `scripts/revision-cruzada/comprobar.py` + `test_comprobar.py` (40 en verde), sin modelo: p03 parcial, p04, p06, p07, p10, p11, p12, p14 y p15 parciales. Linus main 909 hallazgos (245 p04 alta, 108 en `real-backend.ts`), dashboard 157, operandi-services 183 (25 alta en p03: autenticación del strategist que se apaga con `WEBHOOK_TOKEN` vacío), Tojo 6; 0 credenciales escritas. Reencuentra C1, C2 y el `chatFuer` de 9 dígitos. Rotary sin repo propio (share.py dentro de operandi-services; `wa-eventos` solo en el VPS, sin revisar). Informe y lista para Opus en `docs/revision-cruzada/comprobaciones-deterministas-2026-10-15.md`.

**Sustituida el 15-10 (decisión de Max):** comprobaciones deterministas de los 15 puntos en `scripts/revision-cruzada/` (una por punto: except silenciosos, schedulers sin zona horaria, defaults de env que no aguantan cadena vacía, webhooks sin filtro por `account_id`, marca de «visto» antes de procesar, etc.), corridas sobre todos los repos; cada hallazgo acaba en arreglo con test o descarte escrito. Lo no expresable como comprobación va a un agente Opus sobre paquete y punto concretos. Texto anterior, ya descartado:

En este orden: `operandi-dashboardln`, `operandi-services` (strategist, content-engine-daemon, video-engine, claude-debug), motor de Rotary, Tojo. Mismo triaje y misma verificación. Los workflows de n8n no entran en este pase (otro medio); su revisión va por `reference-gotchas-n8n` a mano.

## Fase 5: las diez lecciones no trasladadas (apartado C)

Cada una con su arreglo concreto:
1. **Hecho 15-10 (`f00e6de`, desplegado y verificado en el VPS):** resumen diario y vencimiento de invitaciones con `CronTrigger(timezone="Europe/Madrid")`, ventana de invitaciones en hora de Madrid (`*_LOCAL`, las `*_UTC` se ignoran con aviso), «hoy» y semana del dashboard en calendario de Madrid (`22512e1`, Vercel). Strategist: (timezone="Europe/Madrid")` y horas en hora local; dashboard «hoy» y semana en Europe/Madrid (`calling/page.tsx:193`, `videos/page.tsx:68-71`). Antes del 25-10.
2. **Hecho 15-10:** `num(key, default)` en `config.py` para todos los enteros (vacío o mal formado = valor por defecto), con test. Antes: Strategist: `INVITE_DAILY_CAP` con valor por defecto que aguante la cadena vacía (como `render.py:50-53` del video-engine). Comprobar primero el `.env` del VPS.
3. **Hecho 15-10:** `feedback-marca-de-visto-despues-de-procesar`. Regla nueva en memoria: «la marca de "ya visto" se escribe después de procesar, nunca antes» (Hemmersbach 24-08, Linus 09-10).
4. **Hecho 15-10** (`claim-atomico-antes-de-enviar` en los gotchas). Pasar el bloqueo atómico antes de enviar de los gotchas de Operandi a `reference-gotchas-apis-externas-y-llm`.
5. **Hecho 15-10:** `feedback-webhook-filtra-por-account-id`. Webhooks: filtro por `account_id` como regla global.
6. **Hecho 15-10:** `feedback-exito-no-es-guardado`. «Éxito no es guardado»: regla global con los tres casos.
7. **Hecho 15-10:** sección «Review chain» en `operandi-dashboardln/CLAUDE.md` y `operandi-services/CLAUDE.md` nuevo. Añadir la revisión de Codex a `operandi-dashboardln/CLAUDE.md` y crear `operandi-services/CLAUDE.md` con la misma cadena (tsc, suite, Codex, canario).
8. **Hecho 15-10:** grants a anon revocados desde el 03-09; RLS activado hoy en las 21 tablas que lo tenían apagado; privilegios por defecto sin tocar (documentado en los briefs). Supabase: comprobar los privilegios por defecto de `anon` (`ALTER DEFAULT PRIVILEGES`) y cerrar el aviso del brief de KIsult.
9. **Hecho 15-10 (parcial, lo señalado):** strategist avisa por Telegram si el resumen no se programa y si faltan los tokens; auth cerrada en 24 rutas y el webhook de Telegram; 5 except del strategist y 7 del content-engine (los nombrados, más el recuento de respuestas que devolvía 0) con aviso o excepción; los demás quedan en `docs/revision-cruzada/comprobaciones-deterministas-2026-10-15.md`. operandi-services: los 27 `except` silenciosos a la bandeja de errores o a un aviso; strategist `main.py:47` avisa por Telegram si el resumen no se programa.
10. **Hecho 15-10.** CLAUDE.md global, «Privacidad y secretos»: sustituir la receta de `hasPrefix` por la de `println` + `cut` + `grep -c`.

## Fase 6: cierre

Ledger (`personal,os,revision-cruzada` para el corredor; cada arreglo en su cliente), reglas nuevas indexadas con `python3 ~/.claude/hooks/indexar-reglas.py`, línea en working-memory, informe de una pantalla a Max: cuántos hallazgos, cuántos confirmados, cuántos arreglados, coste real.

## Lo que necesita de Max

- ~~Activar en OpenRouter el filtro de proveedores sin registro de datos (fase 1).~~ Ya no hace falta (15-10).
- OK a tocar los repos de Operandi (fases 4 y 5) en sesiones separadas.
- La línea exacta para el CLAUDE.md global (fase 5.10), que se le propone en el chat.
