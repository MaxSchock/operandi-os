# Working Memory (tope ~2.500 car.)

> Solo hilos vivos, una línea. Detalle en session-logs.

## Hilos activos

- 🔥 **Hemmersbach** · servicio en la VM del cliente (`reference-hemmersbach-vm-acceso-vpn-ssh`), prod en ki-prod-01. ⛔ túnel Tailscale (pedido 05-10, recordatorio a Murat 07-10 con la entrada de Access Controls); luego paralelo y corte.
- **Vídeo, revisor final** · solo canario. ⛔ Max prueba «Release» (8c954d6e); luego `VIDEO_FINAL_REVIEW_CLIENTS=all`.
- **Aitor** · huecos enviados 01-10. ⛔ respuesta e invitación.
- **Operandi llamada primero** · en producción; Zayd llama desde 01-10. ⛔ feedback de Zayd.
- **Linus/RHP** · prioridad de pendientes en André, Jonas y main (01-10). ⛔ Jonas: «Hilf mir»; ¿97 sin fecha?
- **Linus Heute limpio** · rama `lo-olvidado-5-aufraeumen` (b90d96e0) SOLO en canario: nombres de WhatsApp, 5 reglas de cierre, caducidad, pregunta privado/trabajo, «Von Linus abgehakt». ⛔ Max: OK para subir a André/Jonas/main (migración 0038); cierre automático aún sin caso real visto en canario.
- **Linus Arbeiter** · construido y probado en el ThinkPad contra el canario (rama `arbeiter-verdrahten`, log 06-10 16:40). ⛔ Max: instalar en André y fusionar; `MAX_ARBEITER=an` en linus-andre; unidades de André; equipo de Jonas. ThinkPad: trabajador vivo, se quita con `& "$env:LOCALAPPDATA\linus-arbeiter\deinstallieren.ps1"`; restos en Descargas (ver log). Tobi sigue en a2-76fa9d5. ⛔ CI de main roja.
- **Suritec/FRED** · ⛔ Gregor: herramienta o frase fija; número dictado al Cockpit; cobro 66-KIS6; conv 611/740; #732.
- **KIsult** · Jaeger: PDF del alcance nuevo enviado a Jonas 07-10 (79-104 h). ⛔ su reacción, luego Tristan; ⛔ audio de Jonas 07-10 sobre Suritec sin contestar; ⛔ OK de Sergio (RHP ERP), luego Jonas; Goldspitze 1.650 € sin facturar; IDENTICA/TalkPilot a Jonas.
- **GBS** · negativas por cron L-V 09:30. ⛔ ¿PMax sigue?; Habiba; a Juan nada sin orden de Max.
- **Vídeo por etapas / Cardeleine** · Jana v6 en su panel (f61d1d18 v1). M0-M11 y P1-P5 desplegados (motor fdaf3bd, panel 88c059c). Prueba real 07-10 OK (plano 2). Dashboard sin recargas en todas las pantallas (panel 950ec76; patrón ActionForm/FilterForm/GET en el CLAUDE.md del repo; AutoRefresh queda en 8 pantallas sin GET propio). Voz del presentador por cliente (`client_features.video_presenter_voice`, motor 13bfcd4): `max` = German_FriendlyMan 1,15. Vídeo 513b7b8d abandonado por Max (plano 1 con la otra persona hablando; no se filma más). M12 «launch» (vídeos de producto al estilo brag, 0 $ en proveedores, ~1,4 $ tokens) EN PRODUCCIÓN 07-10 19:13 (motor 42129d3, panel 0c4d139); canario 65028ac4 entregado, copia en Downloads/m12-launch-canario-cardeleine.mp4, sin sonido (music cobra en fal). Traspaso `clients/operandi/context/handoff-video-m12-launch-hecho-20261007.md`. ⛔ Max: ver el vídeo; OK a música (fal); mezcla host+launch; sonido sintetizado; «otra versión con nota» por escena. ⛔ Max: teclado en la mesa; juicio de labios; veredicto de Jana; luego `madeleine`. Aparcado: talking_head por etapas, narrado con dinero, voz de marca.
- **Rotary** · ⛔ cuenta LinkedIn de la página; César: hora 26-oct y 19-nov.
- **Content-engine** · ⛔ Madeleine filas 158-160 repetidas; fila 112 (aviso 05-10) sin mirar. Referencias virales (07-10): ⛔ Max decide alcance, Madeleine/Jan y 3,50 $ de Apify (`clients/operandi/context/viral-references-candidatas-20261007.md`).
- **Yo Respondo** · ⛔ altas de Christian; leer genérica 13-10; GA4 incrustado (Fernando).
- **Samouraï/Kaps** · ⛔ banner de cookies (Zayd, 02-11); Unipile Hugues.
- **Tojo** · feed y cron de precios (`reference-tojo-feed-merchant-center`). 07-10: Maik mandó Stammdaten; feed corregido (34 enlaces, 37 GTIN, 28 precios), 142 de 143 localizados. Respuesta a Maik y Ralf enviada 07-10 (pide aviso cuando cambien enlaces). ⛔ sus respuestas (EAN de los 21 nuevos, 6110, Steffi); comprobar que el Merchant Center aprueba fahrbar; campaña sin tocar; Richard.
- **Zayd/HNT** · ⛔ dirección JSON-LD; token Webflow; filas 4/6/7/19, hnt.yaml. Imágenes solo hombres y sin letras en producción. 07-10 11:35: fila 13 aprobada y reprogramada a las 12:00 (comprobar que salió); filas 14-18 en «New», ⛔ Max aprueba (la 14 sale 09-10). ⛔ WhatsApp a Zayd sin enviar (borrador en el session-log 07-10 11:35, OK de Max). ⛔ Invitaciones LinkedIn a pymes de Bruselas (orden de Max 06-10): sin construir, exige modo solo-invitación y plan. ⛔ contenido para anuncios (Zayd 01-10); vídeo de Zayd 06-10 sin ver.
- **FWU (personal)** · formulario relleno en Descargas\FWU-reclamacion-2026-10-06. ⛔ firma de Max y subirlo al portal; Marina (WhatsApp 07-10 06:02) espera respuesta de Max, vuelve el 15-10.
- **TN34** · 07-10: respuesta a Beni enviada (dónde ver septiembre, administracion@). ⛔ Luque (grupo Jahnsmüller, 07-10 11:15): artículo UL del doc 4 da 404, title corto de Leistungen, lista de 20 backlinks; al llegar, segundo correo a Beni con eso. ⛔ Max pega las 5 respuestas a Beni. Cardeleine: informe de horas en DE (`1v3xbe1x…`), ¿lo ve Jana?
- **Tracmi** · medición nuestra, campañas de Mario; correo a Roilab 06-10. ⛔ Cookiebot de Trabajadores; ¿cuenta Google del acceso GA4?; 7 conversiones viejas.
- **Estoko** · follow-up a Rafa 06-10. ⛔ export de deals con GCLID, luego datamanager; corte del 24-09 sin explicar.
- **Recuperados 29-09** · ⛔ Kaps parado; Sergi Pena sin Unipile; 21 contactos de Zayd; DMARC falkenlead.
- **Facturación oct** · 67-73 enviadas y apuntadas en la hoja (editable desde 06-10). Gastos: OpenAI bajado (perfil Chromium). ⛔ facturas sept de Ártico, Mar Ledesma, Mario Cortés y Luque; GitHub sin cobro aún. Aparcado: Zayd, Linus 50 %, Goldspitze.
- **Sin dueño (07-10)** · aviso del Merchant Center (760+ productos se añaden solos el 06-11, cuenta 631579311) sin mirar; Cloudways apaga la API v1 y su clave el 15-10 (sin comprobar si algo la usa).
- **Pagos y claves** · ⛔ OpenAI auto-recarga; rotar OpenAI Linus+linus-audit/Tracmi/HNT/tabcom; ROO 26174 (950 €, vence 08-10); Cookiebot docemotos suspendido.
- **OS** · rtk en prueba (08-10). ⛔ `rtk gain` tras 2-3 sesiones de Linus; ⛔ limpieza del PC; fusionar ~180 reglas duplicadas; guard-paja a correo/docs.
- **Otros** · ⛔ webhook TalkPilot André; GDA 100 €/mes (respuesta de Max); Philipp; FNMT y .pfx.
- **Marca personal** · `projects/briefs/marca-personal/`. Canary (Max) publica en su LinkedIn: fila 8 el 08-10 09:00, fila 6 el 09-10 09:00. ⛔ comprobar la salida; fila 7 sin aprobar; Max ve `cayetano-google-v1.mp4`.
- **Llamadas web Falkenlead** · reenvío de Google: GBS funciona (GTM v26); Yo Respondo ya devuelve número (900 843 451, consulta directa 07-10), sin comprobar en la web con visita real. ⛔ 08-10 informe de llamadas GBS y evento `numero_reenvio_mostrado` en las dos. Detalle: session-log 06-10 16:30.
- **Pendiente apuntado por Max (07-10): analizar los 3 vídeos referenciados en el reel** https://www.instagram.com/reel/DeCZn6JMmYf/ · primero leer la descripción y los enlaces del reel; Gemini solo si el texto no basta. Relacionado con el motor de vídeo (M9/M10).

## Notas de entorno

- **Swarm**: editar un `.env` solo llega con `stack deploy`.
- **Linus**: trabajo sin `await` tras responder cuelga la CI sin test rojo (18-09).
- **Evolution**: mp4 grande en base64 da 500; subir a MinIO.

## Decisiones pendientes

- 14-10-2026: borrar grabaciones cifradas en ki-prod-01 (copia y consentimiento).
- «You should know» en prueba (2-6 %/sesión). ⛔ Max decide si se queda.
- CR (d) Wissensaufnahme beim Anschluss: Linus repasa cada acceso nuevo y extrae lo útil.
- Vigilar (07-10): si un entregable vuelve a salir sin propósito o reabre algo ya tratado pese al historial del activador, montar el control al cerrar el turno.
