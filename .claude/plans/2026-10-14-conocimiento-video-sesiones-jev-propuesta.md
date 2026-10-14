# Plan · Recoger el conocimiento de las sesiones de vídeo e imagen, contrastarlo con el motor y proponer mejoras

Estado: HECHO 14-10-2026 23:05 (remates cerrados 15-10 00:25) (fases 1 a 5 completas; fase 5 ejecutada en la sesión 92 de 18:50 a 23:05: 13 bloques + 3b, main del video-engine en `41071d7`, content-engine en `v20261014-scenes2`, strategist `03b4dea`; pendientes de Max y huecos al pie). Antes: EN EJECUCIÓN desde 14-10-2026 16:10 (orden de Max vía sesión iamasters-os-df). Fase 1 hecha 16:23 (561 turnos, Jev se queda con umbral 0,5, 156 correcciones; `projects/conocimiento-video/fase1.md`). Fase 2 hecha 16:35 (145 fichas en 9 temas, `lecciones.md`). Fase 3 hecha 16:47 (19 contradicciones confirmadas, `matriz.md`). Fase 4 hecha 16:55 (`projects/conocimiento-video/propuesta.md`, abierta a Max). 17:25: Max añadió por la tarde los bloques 10 (mosaicos en imágenes clave), 11 (hoja de cara completa desde vídeo), 12 (mosaicos de salón, jardín y piscina) y 13 (traslado de hallazgos a productos y regla de usar todo el material), más una fase 3b (content-engine, 1 h) por las 26 lecciones de julio-septiembre. FASE 5 EN EJECUCIÓN desde 18:50 (Max dijo «ejecútalo» a las 18:35 en la sesión 78, decisiones recomendadas 1-6; sesión ejecutora 92, orquesta Fable 5.1 con ejecutoras Opus 5.5 por bloque). Orden: 3b, 13, 1-2-3-4-8, 10-11-12, 5-6-7, skill y reglas; estado por bloque al pie de este fichero. Antes: esperaba el «lanza» de Max para ejecutar la fase 5 entera de una vez en una SESIÓN NUEVA (traspaso `clients/operandi/context/handoff-video-conocimiento-fase5-20261014.md`, orden de bloques y decisiones por defecto dentro); nada del motor ni del brief tocado. Material ya preparado y gratis: hoja de cara de 28 ángulos subida (`i.ibb.co/PGkwML9d`), fotogramas de la cara y de la casa en VpsFigura `/root/videos-max/{cara,casa}-frames/`. Horas reales fases 1-4: 1,0 h de sesión más ~45 min de máquina (14 subagentes).
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


## Fase 5 · estado por bloque (sesión 92, 14-10-2026)

| Bloque | Estado | Hora | Notas |
|---|---|---|---|
| 3b content-engine | hecho | 19:05 | `fase3b-content-engine.md`: 7 contradicciones C1-C7; se corrigen en el bloque 12 (content-engine); 0,1 h |
| 13 OS | hecho | 19:00 | productos.md, traslados.md, destilador y salud-os, paso de cierre, regla indexada; 0,1 h |
| 1 constantes | hecho | 19:10 | commit c351968 desplegado; A: 0 dissolve; B: moov byte 36 < mdat 6.640; C: 13 s con voz a 10,3 sale 10,708 s; D: 0,09 bajo narrador, 0,25 mudo; E: kling v1 pro, 1,18 $ por 5,2 s; F de pago pendiente de Max; 0,15 h |
| 2 revisor para todos | hecho | 19:50 | 9b6d421 desplegado; A hold con 2 s negro; B all; C compose; D advisory axis 38 px; E frames_seen 8/56 heard false; visión 0,076 $; 0,3 h |
| 12 activos casa | esperando a Max | 19:30 | 6 activos en `fotos-referencia/casa-2026-10-14/`, abiertos en Windows; Max aprueba o pide otro encuadre; 0,15 h |
| 12 content-engine | hecho | 19:55 | 2457bf1 v20261014-scenes, 105 tests; escenas salón/jardín/piscina en el brief tras el OK de Max; 0,2 h |
| 12 cierre | hecho | 20:10 | 74ab419, v20261014-scenes2 desplegada: cuatro escenarios en el brief del canario; queda la parte de `keyframes.py` (bloque 10) |
| 1F prueba de pago | hecha, NO pasa | 20:25 | 1,164 $; cabeza 19 px (risa ojos cerrados, mano), 1er fotograma 4,17 (nitidez Kling, sin desplazamiento), puente estirado 0,6 % (arreglo: reescalar respetando proporciones, va al bloque 5 con la medida tras cada paso de pago y 1 reintento automático); boca y unión pasan; 0,2 h |
| 3 montaje que escucha | hecho | 20:40 | c65ed25 desplegado; heard true, 80-100 % por frase, música 0,35 = defecto, mudo sin música falla; F0 por tramo al bloque 5; consecuencia: montaje cuesta 0,10 $ (panel no lo enseña), tipografía sin música no se monta; 0,35 h |
| 10-11 keyframes y hoja de cara | hecho en rama | 21:05 | commits 6a69124, ac3ae07, d55051e; 8/8 llamadas con [base, hoja, detalles], cliente sin escenarios idéntico byte a byte, inspect rechaza 2 monitores y anillo; hoja automática 28 baldosas (visión 0,29 $) abierta a Max; SQL `sql/20261014_scenarios_face_sheets.sql` por aplicar; fusión y despliegue tras el bloque 4; 0,4 h |
| 4 gasto con tope | hecho | 21:35 | 8a36f1b + 6a588bb desplegados; tope = máx(3 $, estimación + 15 %): 513b7b8d da 11,01 $; tokens 3 $; sin precio = failed; segunda composición retoma try-3; SQL aplicado con copia; huecos: peticiones sin estimación quedan a 3 $, STT de revisión fuera del tope; 0,35 h |
| fusión 8 + 10-11 | hecho | 21:50 | main 03b4dea desplegado con cv2; SQL aplicados (4 escenarios del canario, personaje Max con hoja, staged_flow true en 8 clientes); strategist desplegado; 0,15 h |
| 5 medidas en el revisor | hecho en rama | 22:30 | measure.py; A caza la prueba F (19 px, ojos, mano, reintento 1), B v7 pasa (12 px, 5/5), C v7c/v7d/ref fallan y v7f 0 defectos, D parado 45,9 dB, E 56/56 fotogramas, F voces 87/186 Hz; técnica cambiada con razón: igualar brillo tras ECC (no solo desenfoque), puente por afín ECC, boca por interior oscuro; 0,5 h |
| 6 móvil con vídeo por etapas | hecho en rama | 22:45 | f21105c + d5bac8b; screen_ref como imagen start (panel sin cambios), homografía y lámina x3, Hailuo con 7 claves, bisel v7f 0 / v7c 17 defectos, 2,00 $ por plano; panel: enseñar lámina y seen (pendiente, otro repo); 0,7 h |
| fusión 5 + 6 + 7 | hecho | 23:05 | main 41071d7 desplegado; una sola medida del móvil (la del bloque 5); todas las suites pasan (D1 del bloque 8 queda obsoleta a propósito: el 6 ya filma screen); 0,25 h |
| skill y reglas | hecho | 19:00 | cinco arreglos en la skill (fade, cola 0,4, Wan, abrir.sh, revisión 2 fps, no redesplegar con render); reglas probar-la-via-exacta y reclamo-al-brief indexadas |
| 7 editar solo el clip | hecho en rama | 22:15 | 25c6c8e + f079c2f; A-F con dobles; fuera de la caja 0,17-0,27/255 con material real, regenerado 58-62 marcado; panel: what=person + person_ref; decisión de Max: segmentación a silueta (otra llamada) o rectángulo; 0,25 h |
| 8 camino antiguo | hecho en rama | 21:25 | 8d86948; el motor nunca leía video_staged_flow (lo decide brief.flow del panel): corte por fecha en legacy.py, worker desvía, talking_head → dialogue (quien no es personaje listado sale inventado: hueco del bloque 9), screen falla con aviso hasta el bloque 6; 16/16; SQL y eventos del digest pendientes; fusión con 10-11 tras el bloque 4; 0,15 h |

## Fase 5 · cierre (23:05)

Horas reales de la fase 5: 4,4 h de sesión (orquestación 0,5 + bloques) más unas 4 h de máquina de las ejecutoras. Gasto: 1,164 $ (prueba F) + 0,22 $ (STT bloque 3) + 0,076 + 0,031 + 0,29 $ (visión) ≈ 1,8 $.

Pendiente de Max:
- Prueba F: la foto que habla con Kling v1 pro falla una de dos veces (cabeza, ojos, mano); desde el bloque 5 el motor la rechaza solo y reintenta una vez. ¿Vale el reintento automático con tope de uno, o prefiere ver cada toma?
- Bloque 7: dentro de la caja de la persona, Wan redibuja el fondo; recortar a la silueta exige un modelo de segmentación (otra llamada de pago). Rectángulo (como está) o segmentación.
- `LAUNCH_STRICT=1` cuando el canario pase dos launch seguidos sin agotar intentos (hoy en aviso registrado).
- Bloque 9 (avatar de página como receta, 6 h) cuando haya segundo cliente; mientras, quien habla sin ser personaje registrado sale inventado.
- Panel (otro repo): precio del montaje 0,10 $; lámina x3 y texto `seen` de la referencia del móvil; `what=person` + `person_ref` y `costs.shots[n].person.total`; `lips.qc` de las tomas.
- Pruebas de pago pendientes cuando quiera: 8 imágenes clave del canario con escenarios (1,20 $), hoja de cara automática de punta a punta (0,15 $), toma Hailuo con referencia aprobada (2,28 $), sustitución real con Wan (0,97 $).
- `placement` de los escenarios nombra objetos del lugar (chair, desk, glass table): lo aprobó en el content-engine; en vídeo sale igual. Si quiere la versión estricta, una línea en `scenarios.start_prompt`.

## Remates (23:20, tras «termina con todo lo tuyo»)
- Tope por cliente `madeleine` = 12 $ (sus vídeos cuestan 6-11 $ y las entregas antiguas no tienen estimación); copia previa en `clients/operandi/backups/client_features-madeleine-antes-cap-20261014.json`.
- Hechos: remates del motor (`8dcddcf` desplegado: `TakeRejected` en el camino antiguo apunta coste y evento, suites b4 y b8 en el repo, ramas `fase5-*` borradas con copia de SHA); content-engine `abd8c24` (`v20261014-repairguard`): aviso en `image_notes` y `generation_inputs.repair_rebuilt` cuando una reparación rehace la escena (dHash > 72/256), 113 tests.
- Panel hecho (`a737b5e`, Vercel desplegado, `prod-forms-inplace.py` = 0): precio del montaje 0,10 $ con la misma regla que el motor (0 $ si todas las voces ya están transcritas; `plan.costs` NO tiene `assemble`, el panel lo calcula y usará `costs.assemble` si el motor lo añade), diálogo de pago y `confirmed_usd`; lámina x3 y `qc.seen` bajo la referencia del móvil; casilla «Only change the person» con selector de foto o personaje y precio `costs.shots[n].person.total` (botón propio en planos de clip); rótulo «Measured: correct / refused» por toma leyendo `lips.qc`, `lips.phone` o `lips.measures`+`mouth_fails`, y «Checked: N of N frames, sound listened» en la entrega; tarjeta `video_request_cap_usd` / `video_token_cap_usd` en `admin/clients/<slug>` (vacío = defecto, 0 = sin tope). Arreglo de paso: las sumas de `costs.shots` trataban `person` (objeto) como número. Solo el precio del montaje se ve hoy con datos reales (capturas abiertas a Max: `montaje-precio.png`, `montaje-confirmacion.png`); el resto aparece con la primera petición del motor nuevo. Tarjeta de topes sin probar en vivo (el canario no es admin).
- Strategist hecho (`dab99a5`, desplegado, 4 tests): sección «Reparaciones de imagen que rehicieron la escena (24h)» en el resumen diario (cliente, fila o id corto, distancia, hora, 50 caracteres del post), leyendo `generation_inputs.repair_rebuilt` de las últimas 24 h; sin avisos no aparece. Cierra el hueco «el aviso no sale en el digest».
- Fase 5 cerrada del todo a las 00:25 del 15-10. Horas reales de la fase (ledger): 5,0 h.
- Max 23:15: lo abierto hasta ahora (escenas de la casa, hoja automática, referencia del móvil) «tenía buena pinta».
- Sin hacer por depender de otros: escenarios para los demás clientes del content-engine (hace falta foto base de cada uno).
