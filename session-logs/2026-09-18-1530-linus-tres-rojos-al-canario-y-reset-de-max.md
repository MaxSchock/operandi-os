# 2026-09-18 15:30 · Linus: tres rojos al canario, la prueba de Max los desmonta, y reset del enfoque

Entidad: KIsult / RHP. Repo `~/max-assistent`. Sesión `linus-learn-blocks-review` (segunda compactación).

## Qué se hizo

- Rojo 1 (`verwerfen-belegt.ts`), rojo 2 (patrones «vorgemerkt»/«zurückgeholt» en `erledigt-wache.ts`) y rojo 3
  (`zeilenAusSeinenWorten`, el servidor comprueba la fila del modelo contra sus palabras; decisión de Max
  «que compruebe y pregunte»). Rama `verwerfen-nur-mit-seinen-worten`, CI verde en b1aec9f, main cc2ada9.
- Guion `wortschatz-aus-korrektur` a main (83edd5f) y ajustado para conocer los dos frenos (b1d39b9).
- Canario `linus-audit` a a2-b1aec9f (sonda ok). Copia de contactos antes de que Max probara.

## Qué midió la prueba de Max (13:02-13:04 UTC)

- 0 tarjetas creadas; la voz dijo dos veces que había una esperando.
- El texto del servidor llega a Realtime «sinngemäß» (`delegation.ts:14`): 219 caracteres del agente, ~134 hablados.
  Las barreras de frases del servidor no ven lo que sale por el altavoz. Mis tests verdes medían el carril equivocado.
- Primer turno con tres homónimos: la voz leyó una fila pidiendo «ja» (frase servida por 4b46156 mal usada).
- Voz doble: latido de Piper (`herzschlag.ts:112` no calla con trabajo abierto). Max: no lo quiere de ninguna forma.
- ~10 correos en pantalla al pedir «el último»: sin mirar.
- Deepgram sigue para `/api/stt`; la segunda voz era Piper (`MAX_TTS=piper`).

## Lo que Max dejó dicho (reglas nuevas)

`feedback-linus-una-tarjeta-en-foco` (una tarjeta en foco, preguntar antes de cambiar, guardar lo hecho,
intuitivo, e2e variadas, consejo de sabios) y `feedback-linus-sin-segunda-voz-piper`.
Jonas (`max-demo`) sigue en a2-e519f51, que no tiene latido: nada que instalar.

## Fallos míos de esta sesión

- Dos días en el rincón de los homónimos cuando borrar ya va con el dedo.
- «Rojo 2 arreglado» afirmado con tests del agente, sin medir el altavoz.
- La revisión Codex de los bloques 1 y 2, prometida en el plan, nunca se hizo.
- No pedí sesión vacía con el contexto lleno; Max tuvo que decírmelo.

## Siguiente

Sesión vacía: plan desde los siete puntos de Max + hechos medidos, consejo de sabios, ejecución por ramas
pequeñas, e2e variadas. Traspaso reescrito en `clients/kisult/clients/rhp/linus-sprint-a3-handoff.md`.
