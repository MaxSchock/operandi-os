# Frases que delatan texto de IA: investigación y barrera

Entidad: interno (vale para Operandi, KIsult, Falkenlead y personal). Para quién: Max. Para qué: que ningún mensaje ni documento que salga en su nombre se reconozca como escrito por IA. Origen: 08-10-2026, Jaeger («Worum es geht», «Frage:», «Moin Jonas» repetido, documento de cuatro páginas).

## Estado 15-10-2026: HECHO (fases 1 a 5). Cerrado el 15-10: ejemplo 2 de `tool-humanizer` reescrito sin negritas ni rótulos (contradecía M9 y B2); barrera nueva `~/.claude/hooks/guard-subida-drive.py` (PreToolUse) que pasa la lista a todo lo que sube a Drive o se escribe en un Google Doc, con paso único `touch /tmp/claude-drive-consent`. El revisor por modelo para documentos NO se construye: la medición del 14-10 (`projects/barreras-correccion/fase1.md`) muestra que los jueces por modelo no separan lo corregido de lo sano; los documentos siguen con la lista mecánica, el recuento de palabras y el revisor de estructura de `guard-paja-mensaje` para mensajes.

## Estado 08-10-2026: fases 1 a 4 hechas, fase 5 a medias

Hecho: investigación e informe; lista única `~/.claude/hooks/frases-ia.json` (35 patrones) con `frases_ia.py`; conectada a `guard-mensaje-corto`, `guard-respuesta` y a la barrera nueva `guard-documento` (Stop); revisor `guard-paja-mensaje` con cinco preguntas y fechas del hilo; regla irrompible 3 en `~/.claude/CLAUDE.md` y regla en memoria. Copias de todo lo tocado en `~/.claude/backups/guards-20261008/`.

Probado: las dos versiones rechazadas del PDF de Jaeger bloquean y la aceptada pasa; «Frage:», cierre de cortesía, raya y transliteración bloquean; siete mensajes cortos buenos pasan; el revisor distingue el saludo repetido del primero del día.

Medido (fase 5): sobre 3.000 mensajes de Max a terceros anteriores al 01-06-2026, las frases y el vocabulario de la lista marcan 2 (0,07 %). Otros 190 llevan raya, emojis de interfaz, markdown o la palabra «Claude»; no se ha podido separar cuáles tecleó Max y cuáles son texto pegado o automático. «Claude» a secas ya no bloquea en mensajes (66 usos propios). Max, 09-10: la lista se aplica tal cual; si necesita una formulación que la lista bloquea, lo dirá él. Falta también: corregir el ejemplo 2 de `tool-humanizer`, que contradice la lista; revisor por modelo para documentos (hoy los documentos solo pasan la lista mecánica y el recuento de palabras); las subidas a Drive no las ve ninguna barrera.

## Fase 1. Investigación

Cinco líneas en paralelo, notas en `projects/frases-ia/research_notes/Frases que delatan texto IA/`:

1. Inglés: palabras y frases (estudios de vocabulario en exceso, guía de Wikipedia, listas de editores).
2. Estructuras que no dependen del idioma: etiquetas delante de frases, tríadas, «no es X, es Y», negritas de entrada, resúmenes, cierres con oferta, rayas, simetrías.
3. Alemán: Floskeln y construcciones típicas en mensajes y documentos de negocio.
4. Español: lo mismo.
5. Corpus propio: todo lo que Max y Jonas han marcado ya como paja o voz de IA en session-logs y reglas, más las listas que ya existen (skill `tool-humanizer`, `guard-mensaje-corto`, `guard-paja-mensaje`).

Informe final en `projects/frases-ia/reports/Frases que delatan texto IA.md`.

## Fase 2. Lista única

Un solo fichero de datos (`~/.claude/hooks/frases-ia.json`) con cada patrón, idioma, categoría y un ejemplo. De ahí leen todas las barreras; no hay listas sueltas por hook.

## Fase 3. Barreras

- Mensajes (WhatsApp, correo): `guard-mensaje-corto.py` lee la lista.
- Documentos (HTML y PDF que van a Descargas o Drive): barrera nueva sobre el texto del documento.
- Respuestas en el chat a Max: `guard-respuesta.py` lee la lista.
- Lo que no es una palabra sino una estructura lo revisa el modelo de `guard-paja-mensaje.py`, con los ejemplos de la fase 1.

## Fase 4. Regla

Línea en las reglas irrompibles de `~/.claude/CLAUDE.md` que apunta a la lista, y regla en memoria con disparadores.

## Fase 5. Prueba

Pasar por las barreras los textos de hoy (PDF de Jaeger del 07-10 y las cuatro versiones del 08-10, los WhatsApp a Jonas) y diez mensajes reales de Max. Las barreras tienen que marcar los primeros y dejar pasar los segundos.

## De parte de Max

Nada.
