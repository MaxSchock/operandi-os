# Traslados (tope ~3.000 car.)

> Hallazgos que funcionaron y el producto al que tienen que llegar. Índice vivo, no informe: una fila por hallazgo, detalle en el origen. Destinos en `docs/productos.md`. Estados: pendiente · hecho · descartado. Lo apunta el destilador y el cierre de sesión; el arranque enseña los pendientes.

| id | Hallazgo | Origen | Destino | Estado | Fecha |
|---|---|---|---|---|---|
| foto-base-oficina | Foto base del lugar como escena + hoja de cara + mosaico de detalles; texto solo de la persona | brief canary, `fotos-referencia/LEEME.md` | content-engine (todos los briefs con persona) y video-engine `keyframes.py` | hecho en video-engine 14-10 (bloque 10, `scenarios.py`); content-engine solo canario, resto de briefs pendiente | 2026-10-14 |
| hoja-cara-28-angulos | Hoja de 28 ángulos sacada de un vídeo de la cara (1 fps, selección por ángulo) | `fotos-referencia/max-hoja-cara-v2-28-angulos.jpg` | brief canary (imagen 2), content-engine, video-engine `keyframes.py` | hecho en content-engine (2457bf1) y video-engine (bloque 11, `faces.py`, personaje Max con hoja) 14-10 | 2026-10-14 |
| launch-v7-ai-avatar | Launch v7: kling ai-avatar + puente first-last, hecho a mano | `projects/video-cardeleine-v7/` | video-engine, bloque 9 | pendiente | 2026-10-14 |
| mosaicos-casa | Escena base 4:5 + mosaico de 16 detalles por estancia (salón, jardín, piscina) | vídeo de la casa 13-10 | content-engine (brief canary), keyframes; bloque 12 | hecho 14-10: brief (74ab419) y video-engine (`client_features.video_scenes`) | 2026-10-14 |
| medidor-bisel-opencv | Medidor del bisel del móvil con OpenCV (portar la lógica, no el fichero) | `projects/video-cardeleine-v7/review.py` | video-engine `review.py`, bloque 5 | hecho 14-10 (`measure.phone`) | 2026-10-14 |
| aceptacion-v5-v7 | Scripts de aceptación v5-v7 (lógica, no las cajas en píxeles) | `projects/video-cardeleine-v7/` | video-engine `review.py`, bloque 5 | hecho 14-10 (`measure.py`: cara, cabeza, boca, mano, movimiento, F0) | 2026-10-14 |
| mosaicos-referencia-fotos-a-video | Mosaicos de referencia para generar fotos con consistencia; aplicable también a vídeo y a las 18 tandas de oficina | projects/conocimiento-video/visual/ lámina 8 y bloque 10 de propuesta. | content-engine-daemon, video-engine | pendiente | 2026-10-14 |
| foto-real-como-imagen-1-solo-persona-en- | Foto real de la oficina como imagen 1 y el texto describe solo a Max, sin inventariar objetos; da la sala fiel y consistente. | brief de la oficina de Max y fotos-referencia/ (fila 9 y 11, tandas 10 | Marca personal de Max; content-engine-daemon | pendiente | 2026-10-14 |
| escena-sin-prompt-anterior-al-repetir-im | Al repetir una imagen por «no se parece», extraer solo la escena y no reutilizar el prompt anterior con su descripcion vieja de la sala. | cambio de codigo 43307a7 en el motor de imagenes | content-engine-daemon | pendiente | 2026-10-14 |
