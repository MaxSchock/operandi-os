# Plan · Recoger el conocimiento de las sesiones de vídeo e imagen, contrastarlo con el motor y proponer mejoras

Estado: EN EJECUCIÓN desde 14-10-2026 16:10 (orden de Max vía sesión iamasters-os-df). Fase 1 hecha 16:23 (561 turnos, Jev se queda con umbral 0,5, 156 correcciones; `projects/conocimiento-video/fase1.md`). Fase 2 hecha 16:35 (145 fichas en 9 temas, `lecciones.md`). Fase 3 hecha 16:47 (19 contradicciones confirmadas, `matriz.md`). Fase 4 en marcha.
Entidad: Operandi (motor `video-engine` + Dashboard). Para quién: Max. Para qué: que el motor tenga lo que hemos aprendido desde mediados de septiembre y deje de repetir errores que ya pagamos una vez.

## Qué hay

- 26 session-logs de vídeo, Cardeleine, M10-M12, revisor y Dashboard desde el 15-09, más los traspasos (`handoff-video-m12-*`, `handoff-cardeleine-*`), el plan `cheeky-pondering-flute` (14 de 17 bloques), la skill `video-escena-por-escena` (7 secciones) y unas 15 reglas `feedback-*` de vídeo e imagen.
- 139 transcripciones completas (`.jsonl`) de esta carpeta, con cada corrección de Max tal como la dijo. `projects/barreras-correccion/jev-correcciones/extraer.py` ya saca los turnos de Max con el final del turno anterior de Claude, anonimizados (1.501 turnos, 123 sesiones).
- El motor en `~/src/operandi-services/services/video-engine` (`a8b05ce`): recetas `dialogue`, `launch`, presentador, `talk.py`, `review.py`, `montage.py`, `keyframes.py`.

## Qué papel tiene Jev

Jev responde sí/no a una pregunta sobre un texto corto, barato (0,00006 $ por llamada) y rápido. El 14-10 medimos que como juez de «¿Max corrige aquí?» acierta poco más que el azar sobre turnos generales (75 % de los corregidos, pero 21 % de falsos positivos). Aquí sirve para lo que sí hace bien: **cribar** miles de turnos a preguntas concretas y cerradas («¿habla de un vídeo, imagen, avatar, móvil, labios, música o montaje?», «¿Max dice que algo está mal o pide repetirlo?»). La **lectura** de cada corrección (qué falló, qué quería Max, qué regla salió) la hace un modelo grande en subagentes, no Jev. Si Jev criba peor que un filtro por palabras en una muestra de 100 turnos etiquetados a mano, se descarta y se sigue con el filtro.

## Fases

**Fase 1 · Extraer (máquina, ~1 h real + tiempo de máquina).**
Con `extraer.py` ampliado: turnos de Max de las sesiones de vídeo e imagen (por nombre de sesión y por palabras: vídeo, imagen, avatar, móvil, labios, veed, Kling, MiniMax, Hailuo, Flux, revisor, montaje, música, launch, Cardeleine, Jana), con el final del turno anterior de Claude y el primer párrafo de la respuesta siguiente. Jev criba con dos preguntas cerradas; muestra de 100 a mano para medir precisión frente al filtro por palabras. Salida: `projects/conocimiento-video/turnos.json` anonimizado y una tabla de cuántos turnos salen por sesión.

**Fase 2 · Leer y destilar (subagentes, ~2 h real).**
Cada corrección pasa a una ficha de seis campos: fecha, qué se entregó, qué dijo Max (literal), causa raíz (técnica mal elegida, revisión insuficiente, encargo sin prueba de aceptación, bug del motor, decisión de producto), lección en una frase, y dónde vive hoy esa lección (regla, skill, motor, en ningún sitio). Las fichas se agrupan por tema: elección de técnica, avatares y labios, móvil con vídeo dentro, imágenes inicial y final, montaje y transiciones, música y audio, revisión antes de entregar, entrega y panel, encargos a ejecutores. Salida: `projects/conocimiento-video/lecciones.md` con las fichas y una tabla por tema con el número de veces que se repitió cada lección (las repetidas son las que más cuestan).

**Fase 3 · Contrastar con el motor (subagente con el código delante, ~1,5 h real).**
Para cada lección: ¿está en el motor? ¿en qué fichero y función? ¿se comprueba automáticamente (revisor, prueba) o solo está escrita en un prompt? ¿contradice el código algo aprendido (hoy: `dissolve` en el montaje, OmniHuman por defecto en `talk.py`, revisor que no mide labios ni bisel)? Salida: matriz lección × (motor / skill / regla / nada) en `projects/conocimiento-video/matriz.md`.

**Fase 4 · Propuesta de mejora (~1 h real).**
Documento interno para Max, dos páginas: los cambios al motor ordenados por errores que evitan por hora de trabajo, cada uno con la prueba de aceptación que lo demuestra (número, no adjetivo), horas reales estimadas y qué receta toca. Separado: lo que no va al motor y se queda en la skill manual (y por qué), y lo que exige decisión de producto de Max (por ejemplo, revisor que retiene frente a revisor que avisa). Salida: `projects/conocimiento-video/propuesta.md` y copia abierta en Windows con `scripts/abrir.sh`.

**Fase 5 · Solo con OK de Max.** Encargo por bloques a una sesión ejecutora del motor con el formato de hoy (requisito, técnica, prueba de aceptación, «dilo antes de gastar»), sin ninguna generación de pago que Max no pida.

## Regla transversal de Max (14-10): cada activo se aprueba antes de seguir

Siempre que una fase genere un activo (foto, imagen inicial o final, clip, vídeo montado, también en pruebas del motor), la sesión:
1. Lo abre en Windows con `scripts/abrir.sh <archivo>` (no basta la ruta) y, si es vídeo, pone al lado las hojas de fotogramas y las medidas de la prueba de aceptación.
2. Explica en dos o tres frases sencillas qué objetivo persigue ese activo (qué tiene que ver el espectador y qué se está comprobando con él), sin jerga.
3. Espera la aprobación de Max. Si la da, pasa al siguiente paso. Si no, itera sobre ese mismo activo hasta que salga lo que se busca; no se avanza con un activo no aprobado ni se encadena el siguiente gasto.
En las fases 1 a 4 no hay activos (solo texto); la regla manda en la fase 5 y en cualquier prueba del motor. Está guardada como regla `feedback-cada-activo-generado-se-aprueba-antes-de-seguir`.

## Modelos (fijados 14-10, criterio de Max: optimizar tokens sin bajar de lo que la tarea exige)

| Quién | Modelo | Por qué |
|---|---|---|
| Sesión ejecutora del plan (orquesta, lee fichas, juzga, escribe la propuesta, revisa vídeos) | **Fable 5.1** | es la que interpreta las correcciones de Max y decide qué va al motor; aquí un modelo menor repite el error que estamos intentando quitar |
| Fase 1, extracción y criba (scripts, Jev, filtro por palabras, muestra de 100) | Sonnet 5.5 | trabajo de código determinista con guion claro; la calidad la fija el script, no el modelo |
| Fase 2, lectura de correcciones y fichas (un subagente por tema, 8 a 9 en paralelo) | Opus 5.5 | hay que entender qué quería Max en cada corrección; Sonnet se queda corto en matiz y Haiku no vale |
| Fase 3, contraste con el código del motor (un subagente por receta: dialogue, launch, presentador, revisor, montaje) | Opus 5.5 | lee ficheros largos y tiene que decir si algo se comprueba o solo está escrito en un prompt |
| Fase 4, propuesta | la sesión (Fable 5.1) | sin subagentes |
| Criba binaria de turnos | Jev 1.13 por OpenRouter | 0,00006 $ por llamada; si criba peor que el filtro por palabras, fuera |
| Transcripciones de audio si hacen falta | Gemini 2.5 Flash por OpenRouter | ya probado en `scripts/transcribir-openrouter.py` |
| Fase 5, cambios en el motor (sesión ejecutora aparte) | Opus 5.5, con Fable 5.1 orquestando y revisando cada activo con Max | código del motor con pruebas de aceptación escritas; el juicio de cada vídeo lo hace la orquestadora con Max |

A cada subagente se le da el contexto completo que necesita (session-logs, traspasos, skill, reglas, código), sin recortar por coste: regla `feedback-contexto-completo-antes-que-ahorrar-tokens`.

## Arranque de la sesión ejecutora

Primer mensaje de Max en la sesión nueva: «Ejecuta el plan `.claude/plans/2026-10-14-conocimiento-video-sesiones-jev-propuesta.md`». La sesión lee este plan entero, la skill `video-escena-por-escena`, los dos traspasos de vídeo y `projects/barreras-correccion/fase1.md`, crea `projects/conocimiento-video/`, y va fase por fase sin parar entre fases (regla `feedback-planes-se-terminan-hasta-la-ultima-fase`); lo que necesite de Max lo pide en lista corta y sigue con lo que no dependa de ello. Al cerrar cada fase: línea en el ledger y estado en este fichero.

## Lo que necesito de Max

- OK para arrancar (fases 1 a 4, nada toca el motor ni genera vídeo; coste de proveedores: Jev y tokens, por debajo de 2 $).
- Si prefiere que la propuesta la vea también Jonas o alguien de Operandi, decirlo antes de la fase 4 (cambia el formato: primero esquema, regla de documentos para terceros).

## Horas

Fases 1 a 4: 5 a 6 horas reales de sesión más el tiempo de máquina de la extracción. Se apuntan en el ledger por fase (operandi / operandi / video-engine).
