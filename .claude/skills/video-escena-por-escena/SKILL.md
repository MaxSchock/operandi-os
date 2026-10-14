---
name: video-escena-por-escena
description: Producción manual de un vídeo del motor de Operandi escena por escena con Max (guion del cliente, imágenes inicial/final, filmación por plano, labios, montaje con transiciones, música y subtítulos, entrega al panel). Úsala cuando Max pida filmar, refilmar, montar o entregar un vídeo de cliente (Cardeleine u otro) fuera del flujo automático del Dashboard.
---

# Vídeo escena por escena (Operandi video-engine, manual)

Protocolo destilado de Cardeleine, 03 a 05-10-2026. Cada regla nació de un error real de esos días.

**Desde el 14-10-2026 el motor hace solo casi todo esto por etapas** (fase 5 del plan de conocimiento de vídeo, `projects/conocimiento-video/propuesta.md`): `fade`, faststart, cola de 0,4 s, revisor que retiene para todos y escucha, tope de gasto por petición, escenarios por cliente con foto base + hoja de cara + mosaico, hoja de cara desde vídeo, medidas de cara/cabeza/boca/mano/bisel con rechazo y un reintento, receta `screen` (clip del cliente dentro del móvil con referencia aprobada) y cambio de persona con Wan sobre la toma aprobada. Este protocolo manual queda para lo que el motor aún no cubre (avatar de página que habla, bloque 9) y para entender qué mide; antes de hacer algo a mano, comprobar si el panel ya lo hace.
Reglas hermanas ya activas (no repetirlas aquí, se activan solas): `feedback-no-regenerar-imagenes-por-criterio-propio-ni-gastar-sin-max`, `feedback-imagen-final-y-pantalla-con-vida-y-fiel-a-la-referencia`, `feedback-no-meter-avisos-legales-no-pedidos`, `feedback-video-dentro-de-video-siempre-minimax`, `feedback-revisar-video-a-dos-fotogramas-por-segundo-no-muestra`, `feedback-editar-solo-el-clip-pedido-no-regenerar-lo-aprobado`.

## 0. Antes de tocar nada

1. **El guion es del cliente y de Max.** Leer el prompt original en `video_requests.brief` (campos `request`, `lines`, `end_text`, `visual_directions`) ANTES de afirmar nada sobre lo que falta o sobra. Error 05-10: dije que el cartel final no seguía el prompt sin mirarlo; sí lo seguía palabra por palabra.
2. **Tabla de planos antes de gastar.** Por plano: escena (lugar), quién sale, qué se dice (texto exacto), tipo (`persona`, `pantalla`, `silent`, `clip`), cámara, ¿corte de escena o continuidad con el anterior?, ¿labios en quién y dónde?, duración = duración del audio + 0,3 s de cabeza. Max la aprueba. Nada se filma que no esté en esa tabla (error 05-10: escena 3a montada sin estar en el guion).
3. **Un plano con texto dura lo que dura el texto.** Nunca acortar, acelerar ni recortar un plano hablado por criterio propio (error 05-10: retime de la escena 3 a 3,4 s: «¿Qué mierda acabas de hacer?»).
4. **Cada gasto se anuncia con su coste y espera un OK explícito.** Elegir entre tomas («B») NO es un OK al siguiente paso de pago (error 05-10: 1,46 $ en Kling tomando «B» como OK). Tras dos intentos fallidos de lo mismo: parar y enseñar lo que hay.

## 1. Imágenes (Nano Banana Pro, 0,15 $/imagen)

- **Corte de escena** (otro lugar, otro encuadre, otro sujeto): la imagen inicial NO tiene que coincidir con la final del plano anterior ni la final con la inicial del siguiente. **Continuidad** (misma escena, otra posición de cámara): la final del plano anterior es la inicial del siguiente.
- Imagen final de un plano: con vida (gente del fondo con gesto nuevo, mano o cámara movida), móvil sólido con la pantalla pegada, mano sin anillos, **avatar con la boca cerrada** (error 05-10: end frame con la boca abierta).
- Pantalla de app: la interfaz de referencia del cliente, no una invención. Texto pequeño inclinado y fuera de foco no tiene que leerse; en primer plano del móvil sí (pasar la captura limpia como referencia).
- Un cambio de opinión de Max sobre una escena reescribe esa escena entera (imágenes nuevas), no se parchea la anterior.

## 2. Filmación por plano (fal, `app.models`)

| Plano | Modelo | Por qué |
|---|---|---|
| Personas, continuidad | `flux3-first-last` (0,17 $/s, 704x1280, 5-20 s) | respeta las dos imágenes |
| Primer plano de móvil con pantalla | `flux3-image` desde una imagen ya en primer plano | mantiene la pantalla pegada al móvil al balancear |
| Pantalla de móvil | NUNCA `kling3-pro-image` | despega la pantalla y dibuja una barra de estado fantasma (captura de Max 05-10) |
| Personas reales | NUNCA Veo 3.1 | rechaza parecidos reales, máximo 8 s |
| Texto pequeño en pantalla | NUNCA minimax H3 imagen-a-vídeo | deforma el texto |
| Vídeo dentro de vídeo (avatar hablando en la pantalla del móvil) | `fal-ai/minimax/hailuo-03/reference-to-video` (0,19 $/s) con foto de referencia aprobada + vídeo real del cliente + audio | única vía que dejó el contenido dentro del bisel (08/09-10); pegar la grabación a mano o editar con Kling rompió los márgenes dos veces |

- **FLUX ignora «acercamiento en el primer segundo»** (dos veces). Si hace falta un primer plano, el plano arranca ya en primer plano desde su propia imagen; el acercamiento es otro plano o no existe.
- **No cambiar de modelo sin probar la perspectiva** en un plano corto antes del largo (error 05-10: Kling elegido por mí, pantalla despegada, dinero perdido).
- Un plano largo (13 s de FLUX) tarda más de 15 min: lanzar con `run_in_background` y timeout alto; el proceso sigue vivo en el contenedor aunque muera el ssh (comprobar por `/proc/*/cmdline`), no relanzar.
- Prompt de FLUX para pantallas: «camera holds this framing… the screen content stays attached to the phone and tilts with it… screen text stays sharp and unchanged… no rings».

## 3. Voz y labios

- TTS con `talk.speak`; nombres de marca en `talk.PRONUNCIATIONS` (`Cardeleine → Kardelehn`, `Madeleine → Madlen`). Marca nueva: tres tomas y Max elige, luego fijar en `talk.py`, commit y `docker service update --force video-engine_app` (deploy.sh no reinicia si la etiqueta no cambia).
- Audio de un plano: 0,3 s de silencio delante (`adelay`), duración del plano = audio + cola.
- **Lipsync `veed/lipsync/v2` (0,07 $/s) elige la cara más grande.** Avatar dentro de un móvil: recortar la región del móvil (x,y,w,h), sincronizar solo el recorte, pegarlo con `overlay`. Comprobar el recorte con `drawbox` en tres fotogramas ANTES de pagar (error 05-10: labios en la Madeleine del fondo).
- Visitante de frente preguntando: labios a cuadro completo (es la cara más grande).

## 4. Montaje (ffmpeg solo existe en el contenedor)

- Normalizar cada entrada: `scale=704:1280:force_original_aspect_ratio=increase,crop=704:1280,fps=24,format=yuv420p,setsar=1,settb=AVTB`; `xfade` exige misma resolución, fps y timebase.
- Transiciones: `xfade=transition=fade:duration=0.4` entre planos de la historia (nunca `dissolve`: a tamaño real sale como lluvia de granos, 08-10), `fadewhite:duration=0.6` al cartel final; audio con `acrossfade` de la misma duración; corte seco solo en continuidad y junto a escenas de página launch. Sin transición el corte suena a golpe (Max 05-10: «¿tu programa no permite hacer transiciones?»).
- Recortar el silencio al final de un plano hablado (fin de la voz + 0,4 s, la misma cifra que `VOICE_TAIL_S` del motor), también en tomas `first-last`; si no quedan segundos muertos.
- **Música:** automatización fija, no compresor (sidechaincompress solo bajó 2-3 dB): `volume='if(lt(t,T_cartel),0.09,...0.25)'` con `eval=frame`, fade in 1,2 s y fade out 2,7 s. Al 0,35 tapaba la voz.
- **Subtítulos siempre:** STT del motor (`render.STT_MODEL`, 0,10 $) sobre la pista de voz montada → tiempos por palabra → bloques por frase ≤ 42 caracteres → `ffmpeg.write_srt` → filtro `subtitles` con el `force_style` de `ffmpeg.concat_and_mix`. Corregir la ortografía de marca que el STT invente («Cardelaine»).
- Cartel final: el texto del cliente (`end_text`) tal cual; el motor lo dibuja con `dialogue.end_card_png`.
- Antes de entregar, la revisión de la regla `feedback-revisar-video-a-dos-fotogramas-por-segundo-no-muestra`, no una muestra: hoja de TODOS los fotogramas a 2 fps (`fps=2,tile=7x3`), un fotograma por escena a tamaño real (720 px) con un solo eje por escena, el vídeo visto en movimiento, y audio transcrito por tramos (texto y sexo del hablante contra el guion); medir niveles con `volumedetect` por tramo (voz −19 a −23 dB media, música bajo voz con máximo ≤ −20 dB) y la cola de los últimos 4 s en pasos de 0,5 s. «Revisado» sin esos números no es revisado.

## 5. Entrega

1. Copia en `/mnt/c/Users/PC/Downloads/<cliente>-completo-vN-<fecha>.mp4` y abrirla a Max en Windows con `~/iamasters-os/scripts/abrir.sh <archivo>` en la misma respuesta (con la hoja de fotogramas y las medidas al lado); una ruta, un adjunto o `SendUserFile` solos no cuentan como entrega (regla `feedback-abrir-archivos-a-max-en-windows`).
2. WhatsApp al chat propio de Max (`179830280736869@lid`) con la versión `-wa.mp4` (720p, crf 27): `peek` como comando separado ANTES del `send-video` en el mismo turno (el hook bloquea si no).
3. Panel del cliente: entregar como versión nueva de SU petición (`deliverables/<id>/vN.mp4` + `thumb.jpg`, `video_requests` a `delivered`, fila en `video_assets`), copiando antes la fila a `clients/<empresa>/clients/<cliente>/backups/`. Nunca una fila nueva si la petición del cliente existe.
4. Al cliente solo se le escribe cuando Max lo pide; borrador en su buzón (Cardeleine: Drafts de `max@falkenlead.com` por IMAP, copia `.eml` en backups), dos o tres frases, sin explicar lo que se cambió por dentro.
5. Ledger de horas con el tiempo real de la sesión.

## 6. Pantallas de móvil con vídeo dentro (aprendido del 08 al 09-10-2026, vídeo de Jana)

Cuatro versiones rechazadas por Max antes de acertar. El orden que funcionó:

1. **Partir del clip o la foto antigua que ya dio bien el teléfono** (mano, bisel, inclinación, fondo), no de un fotograma nuevo. Si el clip bueno no está en la copia del VPS, buscarlo antes de usar otro: en v7/v7b partí de la toma de Kling rechazada porque la buena no estaba, y heredé sus marcas fantasma.
2. **Foto de referencia con homografía, nunca un rectángulo recto.** Localizar las cuatro esquinas de la pantalla (recta ajustada a cada lado), proyectar la interfaz real del cliente sobre ese cuadrilátero y recortarla con la silueta de esquinas redondeadas. El modelo copia la referencia al píxel, defectos incluidos: escalón en una esquina, franja clara del borde de la grabación, muesca más isla dinámica a la vez.
3. **Anatomía del teléfono en la referencia:** UN solo recorte de cámara (la muesca del propio teléfono), barra de estado coherente (hora a la izquierda de la muesca, iconos a la derecha), ventana del vídeo a ras de ambos biseles, ficha debajo tal cual la enseña la grabación del cliente (aunque quede media pantalla en blanco). Si la grabación del cliente es de un Mac, la barra de estado se maqueta a mano y se dice.
4. **Max aprueba la foto antes de pagar la generación.** Enseñarla a resolución original más una lámina x3 con cuadrícula horizontal (`drawgrid`) de la parte alta, los dos bordes y una esquina de la ventana; en el mensaje, ángulo del borde superior del bisel y de la ventana en grados (±0,3°) y distancia bisel-ventana en px a ambos lados en cuatro alturas (0-2 px a 704).
5. **Generación:** Hailuo 3 reference-to-video con Imagen 1 = la foto aprobada, Imagen 2 = captura limpia de la interfaz, Vídeo 1 = grabación real del cliente, Audio 1 = la frase. Una sola; si falla, se enseña y decide Max. Con audio de referencia el modelo dice la frase a su ritmo con su propia voz: si los labios están bien, se usa esa pista (transcribirla y comprobarla palabra por palabra, medir tono frente a la referencia) y veed sobra.
6. **Revisión de la toma y del montaje, medida, no mirada:** parte alta del móvil x3 con cuadrícula en seis momentos (incluidos los dos fundidos), ángulos y distancias en números, esquinas de la ventana, hoja a 2 fps, fotogramas enteros a 704. Fallos que pasaron tres revisiones mías por mirar a ojo: muesca doble, isla pegada al borde del vídeo, franjas de 10-15 px, contenido horizontal dentro de un teléfono inclinado.
7. **Cola de audio:** al cambiar la duración de un plano, recalcular el fundido de la música y medir los últimos 4 s en pasos de 0,5 s; en v7e la música se apagaba a 28,5 s y volvía a 29 s, y Max lo oyó antes que yo.
8. **Formato de salida:** `-pix_fmt yuv420p`, perfil High, faststart. El v6 salió en yuv444p (High 4:4:4), que iPhone y muchos Android no reproducen.
9. **Transiciones:** xfade `fade`, no `dissolve` (lluvia de granos a tamaño real).

## 7. Elegir la técnica por el requisito del plano, no por el último caso que salió bien (13-10-2026)

Antes de encargar o pagar cualquier plano, escribir en una línea qué ve el espectador: **estado inicial, estado final, qué se mueve, qué tiene que quedar idéntico**. La técnica sale de esa línea con esta tabla, nunca de «lo que funcionó la última vez»:

| Requisito del plano | Técnica | Prueba de aceptación antes de pagar el siguiente paso |
|---|---|---|
| Un vídeo real tiene que verse dentro de un marco (pantalla de móvil, ventana) | MiniMax Hailuo 3 con vídeo de referencia y foto de referencia aprobada por Max | contenido dentro del bisel 0-2 px en seis momentos, anatomía del aparato, inclinación |
| Una foto fija que ya está en la composición cobra vida, dice una frase y vuelve a quedarse (avatar de página, retrato en tarjeta) | habla desde la foto con `fal-ai/kling-video/v1/pro/ai-avatar` (imagen + audio; 0,115 $/s, factura el clip alargado: 7,2 s por 5,2 s de audio) recortado donde la boca se asienta, + puente `kling3-pro-first-last` 3 s (a 2x si el gesto es corto) del último fotograma del habla a la foto. Probado 14-10 (v7 del launch): cabeza < 5 px, boca 2-3,7× en los picos, cerrada en los silencios. OmniHuman 1.5 articula igual de bien pero desplaza el cuerpo 130-170 px y no arranca en la foto: descartado. **No** veed sobre un clip first-last: veed solo retoca la zona de la boca y sobre una foto que sonríe con dientes no cierra ni abre los labios (v5 y v6 del launch, 14-10, «lipsync off») | tras el habla: primer fotograma igual a la foto (dif. media < 3/255 en cara y busto), cabeza < 15 px, abertura de la boca en los picos del audio ≥ 1,5× la inicial y en los silencios ≤ 1,2× (hoja de la boca a 8 fps con tiempo y dB); tras el puente: último fotograma igual a la foto y unión < 3; sin fundido de vuelta |
| Un presentador habla a cámara en su propio plano, desde una foto | camino de presentador del motor (`_host_start`) | identidad y ropa constantes, boca cerrada en los extremos |
| Cambiar a la persona de un clip ya aprobado | Wan 2.2 animate/replace sobre el clip existente (`dialogue.SWAP_MODEL`; ganó el 02-10 frente a Kling O3 edit, que dejó a la mujer original dos veces, y a PixVerse, que dejó una mancha; el 08-10 una toma B de Kling sí cambió cara y complexión, así que Kling es reserva, no defecto); nunca redibujar ni volver a filmar | solo cambia la persona; fuera de su caja, diferencia media frente al clip aprobado < 4/255 en 6 momentos; misma duración ±1 fotograma; comparar con la foto del cliente |
| Arreglar composición, ejes, textos, música | editar la página o el montaje; ninguna generación | medidas antes y después |

Origen: v4 del launch de Cardeleine. Apliqué la regla del móvil de Jana («vídeo dentro de vídeo → Hailuo con referencias») a animar la foto de Isabella, que era el caso de la segunda fila; 2,48 $ en una versión rechazada. Max: «¿por qué no has hecho esto así la primera vez?».

**En todo encargo a una sesión o agente ejecutor** van las tres cosas: la línea del requisito, la técnica de la tabla, y la prueba de aceptación con su número; y esta frase literal: «si la técnica prescrita no cumple el requisito tal como está escrito, dilo antes de gastar». El ejecutor comprueba la prueba de aceptación después de cada paso de pago y antes del siguiente, no al final.

## Operativa del contenedor

- Scripts siempre desde archivo: `scp` a `/tmp` del VPS, `docker cp /tmp/x.py $C:/app/x.py`, `docker exec -w /app $C python3 x.py` (`C=$(docker ps -q -f name=video-engine_app | head -1)`). Un heredoc a `docker exec` sin `-i` no llega.
- Material de trabajo en `/tmp/s1` del contenedor: se pierde al redesplegar. Copia en `/root/backups/video-engine-s1-<fecha>/` antes de `service update`.
- Antes de `docker service update --force video-engine_app`, comprobar que no hay ninguna petición en `rendering` ni trabajo en `video_jobs` corriendo (un reinicio a mitad de render lo mata y el vigilante lo da por fallido con reembolso, 06-07-2026); `git push` y el `service update` van en comandos separados.
- Artefactos intermedios en storage bajo `scratch/manual-escenas-<fecha>/`.
