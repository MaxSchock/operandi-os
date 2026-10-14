# Plan: revisión cruzada de todos los desarrollos con la lista de fallos repetidos

Estado: fase 0 hecha el 14-10-2026 (inventario de patrones). Fases 1 a 6 pendientes; arrancar en sesión nueva con este fichero y `docs/revision-cruzada/patrones-de-error-2026-10-14.md` como traspaso.
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

Script `scripts/revision-cruzada/pasar.py` (Python, en el OS):
- Entrada: ruta del repo, lista de extensiones, modelo, tope de gasto.
- Trocea por fichero (y por módulo cuando el fichero pase de 60 KB), adjunta los imports del mismo paquete que quepan y la lista de 15 puntos.
- Pide al modelo JSON estricto: `[{punto, fichero, linea, resumen, escenario_de_fallo, confianza}]`. Rechaza salidas que no sean JSON válido y reintenta una vez.
- Guarda en `docs/revision-cruzada/<repo>/<fecha>/hallazgos.jsonl` y un `coste.txt` (tokens y dólares por fichero). Para en seco al llegar al tope.
- Prueba de humo: `packages/gatekeeper/src` de Linus (30 KB) y comparar a ojo.
- Antes de correr: Max activa en OpenRouter «solo proveedores sin registro de datos» (ajustes de privacidad de la cuenta). Comprobar con una petición que el modelo elegido sigue disponible.

## Fase 2: pase sobre Linus

Seis paquetes (`apps/web/src`, `apps/server/src`, `packages/*/src`, tests de web aparte). Después: agrupar por punto, quitar duplicados, ordenar por daño. Salida: `docs/revision-cruzada/linus/<fecha>/triaje.md` con las 30 sospechas más graves.

## Fase 3: verificación y arreglos en Linus

Agente Opus o Codex en solo lectura sobre las 30: CONFIRMADO / PLAUSIBLE / DESCARTADO con la prueba. Lo confirmado se arregla en bloques de una sesión con test rojo primero, suite del paquete, canario y subida por la escalera (canario, Tobi, André, Jonas) según las reglas de Linus.

## Fase 4: pase sobre los demás repos

En este orden: `operandi-dashboardln`, `operandi-services` (strategist, content-engine-daemon, video-engine, claude-debug), motor de Rotary, Tojo. Mismo triaje y misma verificación. Los workflows de n8n no entran en este pase (otro medio); su revisión va por `reference-gotchas-n8n` a mano.

## Fase 5: las diez lecciones no trasladadas (apartado C)

Cada una con su arreglo concreto:
1. Strategist: `BackgroundScheduler(timezone="Europe/Madrid")` y horas en hora local; dashboard «hoy» y semana en Europe/Madrid (`calling/page.tsx:193`, `videos/page.tsx:68-71`). Antes del 25-10.
2. Strategist: `INVITE_DAILY_CAP` con valor por defecto que aguante la cadena vacía (como `render.py:50-53` del video-engine). Comprobar primero el `.env` del VPS.
3. Regla nueva en memoria: «la marca de "ya visto" se escribe después de procesar, nunca antes» (Hemmersbach 24-08, Linus 09-10).
4. Pasar el bloqueo atómico antes de enviar de los gotchas de Operandi a `reference-gotchas-apis-externas-y-llm`.
5. Webhooks: filtro por `account_id` como regla global.
6. «Éxito no es guardado»: regla global con los tres casos.
7. Añadir la revisión de Codex a `operandi-dashboardln/CLAUDE.md` y crear `operandi-services/CLAUDE.md` con la misma cadena (tsc, suite, Codex, canario).
8. Supabase: comprobar los privilegios por defecto de `anon` (`ALTER DEFAULT PRIVILEGES`) y cerrar el aviso del brief de KIsult.
9. operandi-services: los 27 `except` silenciosos a la bandeja de errores o a un aviso; strategist `main.py:47` avisa por Telegram si el resumen no se programa.
10. CLAUDE.md global, «Privacidad y secretos»: sustituir la receta de `hasPrefix` por la de `println` + `cut` + `grep -c`.

## Fase 6: cierre

Ledger (`personal,os,revision-cruzada` para el corredor; cada arreglo en su cliente), reglas nuevas indexadas con `python3 ~/.claude/hooks/indexar-reglas.py`, línea en working-memory, informe de una pantalla a Max: cuántos hallazgos, cuántos confirmados, cuántos arreglados, coste real.

## Lo que necesita de Max

- Activar en OpenRouter el filtro de proveedores sin registro de datos (fase 1).
- OK a tocar los repos de Operandi (fases 4 y 5) en sesiones separadas.
- La línea exacta para el CLAUDE.md global (fase 5.10), que se le propone en el chat.
