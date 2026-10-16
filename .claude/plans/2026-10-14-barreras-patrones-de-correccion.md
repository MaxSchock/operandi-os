# Barreras para los tres patrones de corrección más repetidos, con medición semanal

Estado: hecho 14-10-2026 (fases 1 a 4, sesión 64). Fases 2 y 3 medidas y NO cableadas: ningún juez (Jev, Haiku 5.5 con y sin evidencia, regla literal) separa turnos corregidos de sanos (69 % frente a 67 %); detalle en `projects/barreras-correccion/fase1.md`. Fase 4 en marcha: `scripts/medir-correcciones.py` cada lunes dentro de `mantenimiento-setup.sh`, historial en `docs/medicion-setup/correcciones-historial.json`. Entidad: personal (setup de Max). Para quién: Max. Para qué: que la tasa de mensajes de Max que me corrigen baje de forma medible.

## Lo que ya sabemos (no reinvestigar)

Origen: `projects/investigacion-reels-2026-10-14/informe.md` (apartado «Jev sobre las correcciones de Max») y `jev-correcciones/`. Jev 1.13 por OpenRouter (`POST https://openrouter.ai/api/alpha/decisions`, clave `~/.config/openrouter/api.key`, 0,042 $/M tokens de entrada) clasificó 1.501 turnos anonimizados de Max de 123 sesiones (0,076 $). Prueba de aceptación superada: 44/50 contra etiquetado a ciegas.

Umbral 0,5: 279 correcciones en 77 sesiones. Patrones por sesiones afectadas: afirmar sin comprobar (35), no seguir instrucción o decisión explícita (32), preguntar o pasar a Max lo que yo podía hacer (27), olvidar lo ya dicho (24), entregable malo o sin revisar (19), forma de escribir (18). Tasa de corrección por quincena: 21 %, 15 %, 21 %. No baja. Los cuatro primeros tienen regla irrompible escrita y activa; las reglas no bastan. Lo arriesgado (borrar, enviar, cuenta equivocada) sale en 5-6 sesiones: las barreras que ya existen para eso (`guard-borrado`, `guard-envio-externo`, `guard-email-send`) funcionan. Ese es el modelo a copiar.

Barreras actuales en `~/.claude/hooks/` (cableadas en `~/.claude/settings.json`): PreToolUse `guard-email-send`, `guard-borrado`, `guard-envio-externo`, `guard-mensaje-corto`, `guard-paja-mensaje`, `guard-anbindung-dateien`; Stop `guard-respuesta`, `guard-documento`, `guard-repaso-canales`. El informe del lunes (`docs/medicion-setup/2026-10-12.md`) ya decía que tres reglas fallan pese a estar activas y que «toca convertirlas en gate».

## Fase 1 · Investigación acotada (media sesión, salida: una página en `projects/barreras-correccion/fase1.md`)

1. Qué puede hacer hoy un hook Stop en Claude Code: bloquear, devolver texto al modelo, leer el transcript del turno. Documentación oficial, no memoria; `guard-respuesta.py` como ejemplo vivo.
2. Por qué las tres barreras Stop actuales no cazan los patrones 1-3: leerlas y probarlas contra 10 correcciones reales de cada patrón (ids en `jev-correcciones/jev_todo.json`, texto en `turnos.json`; los turnos de Claude previos están en los transcripts de `~/.claude/projects/-home-max-iamasters-os/*.jsonl`).
3. Juez: patrón de texto frente a Jev. Para «afirma que está hecho» hace falta leer el turno entero de Claude y ver si hubo comprobación (una herramienta que verificó: test, curl, consulta, lectura). Decidir con una prueba de 30 turnos cuál acierta más; Jev tarda 300 ms y cuesta 0,00003 $ por turno. Lo que va a Jev se anonimiza con `jev-correcciones/extraer.py` (función `anon`) antes de salir.
4. Nada más. No reescribir reglas, no podar memoria, no tocar el destilador.

## Fase 2 · Barrera del patrón 1: afirmar sin comprobar

Requisito: al cerrar el turno, si la respuesta afirma que algo está hecho, arreglado, desplegado, enviado, apuntado o verificado, en ese mismo turno (o sesión, para lo apuntado) tiene que existir una llamada a herramienta que lo respalde; si no, el hook bloquea y devuelve «afirmas X sin haberlo comprobado: compruébalo o reescribe como pendiente». Prueba de aceptación: sobre las 63 correcciones reales de este patrón, reconstruir el turno de Claude anterior y pasar el hook; debe saltar en al menos 50 y en menos de 5 de 50 turnos sin corrección (muestra de `turnos.json` con corr < 0,2). Se cablea en `settings.json` con copia previa del fichero (regla 1).

## Fase 3 · Patrones 2 y 3

- Patrón 3 (preguntar o pasar a Max lo comprobable): al cerrar, si la respuesta pide a Max que compruebe, mire, confirme o decida algo que se puede resolver con una API, fichero o dato que la sesión ya tiene, bloquear con la lista de lo que puedo comprobar yo. Aceptación: 29 correcciones reales, saltar en 22; falsos positivos < 10 % (ojo: las preguntas Tier 3 son legítimas, el hook las deja pasar).
- Patrón 2 (no seguir instrucción o decisión): es el más difícil de detectar en el cierre. Primera versión limitada a «pregunta explícita de Max en su último mensaje sin responder» (ya existe regla `feedback-responder-preguntas-explicitas-antes-de-seguir`). Aceptación: sobre las 50 correcciones, saltar en las que son de ese subtipo (contarlas primero).

## Fase 4 · Medición semanal

`jev-correcciones/extraer.py` + `clasificar.py` corren cada lunes dentro de `scripts/mantenimiento-setup.sh` sobre los turnos nuevos desde la última corrida (guardar marca de fecha), escriben la tasa de corrección de la semana y la tabla de patrones en `docs/medicion-setup/<fecha>.md`. Coste ~0,02 $/semana. Aceptación del plan entero: tasa de corrección por debajo del 12 % dos quincenas seguidas (hoy 21 %).

## Fuera de este plan

Minar aciertos en el destilador y reescribir `soul.md` como persona (ideas del reel de Angus): baratas, independientes, se hacen aparte cuando Max lo diga.

## Reglas que aplican

Copia antes de tocar `settings.json` u hooks (regla 1). Sin em-dashes. Horas reales al ledger (`docs/horas-ledger.csv`, entidad personal, proyecto barreras-correccion). Lo que salga a Jev, anonimizado. No hace falta más OK de Max para las fases 1-4; sí para cualquier cosa que toque producción de clientes (no debería haber).
