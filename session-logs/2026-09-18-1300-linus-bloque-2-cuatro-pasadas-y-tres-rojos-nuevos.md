# Linus · bloque 2: cuatro pasadas en el canario, tres rojos nuevos (18-09, 13:00)

Cliente: KIsult / RHP (Linus, `max-assistent`). Rama `wortschatz-aus-korrektur`, worktree
`~/max-assistent-wortschatz`. Canario `linus-audit` en `a2-4b46156`, main en `4b46156`.

## Qué se hizo

**La CI roja que dejé.** Los dos asertos de `apps/web/src/test/kontakte-doppelt.test.ts` seguían esperando el
formato viejo de la lista de homónimos. Los había pasado en verde ANTES de cambiar ese formato y no los volví a
correr: exactamente la regla de Max del 16-09. Arreglados al contrato nuevo (`Kennung <id>, zum Vorlesen genau
so: „<fila>“`), fichero entero verde en local (28/28) y CI de la rama verde. Comprobado de paso que nadie más
dependía del formato: las líneas 86-87 y `kontakt-anlegen-doppelt.test.ts:91` vienen del renderizador de
`nachschlagen` y del alta, que no se tocaron.

**Main, imagen y canario.** `4b46156` a main por fast-forward, imagen `a2-4b46156`, despliegue
`SOLO=linus-audit` con migración, hashes y sonda en verde. Ningún otro stack tocado.

**Cuatro pasadas del guion**, informes leídos turno a turno
(`bench/kundenpruefung/out/2026-09-18-{1113,1242,1248,1255}-wortschatz-aus-korrektur.md`).

## Lo que quedó probado (verde)

- **El freno de la doble escucha funciona cuando puede comparar.** Pasada 1113, turno 5: la abschrift decía
  «Die mit KI-Sult» y la wiedergabe «keyshold»; el servidor respondió «zeigen auf verschiedene Zeilen» y no
  construyó tarjeta. El rojo de producto del 18-09 queda cerrado con una medición, no con un argumento.
- **Su «Ja» elige la fila y no aprueba nada.** Pasada 1242, turno 3: tras el sí, contacto intacto, sin tarjeta
  en otra fila. Pasada 1255, turno 9: el dedo sobre «Löschen» sí ejecuta, la fila de keyshold desaparece y las
  otras dos quedan. Las dos mitades de la decisión de Max, medidas por separado.
- **Servir la frase a leer funciona.** Pasada 1248, turno 4: Linus leyó la fila entera, literal, como se le
  sirvió entre comillas. Mi diagnóstico de la pasada 1242 («el modelo no lee la frase servida») era falso;
  lo que pasa es que a veces no lo hace.

## Lo que sigue rojo

El turno «una frase, tarjeta» falla en las cuatro pasadas y el vocabulario no llega a aprenderse. En la última
pasada la causa fue nueva: con una tarjeta de borrado en el foco, la voz reinterpreta la orden siguiente como
«corrige la tarjeta del foco», y la ronda 2 ni se plantea.

## Tres rojos nuevos, medidos (van a sesión aparte)

1. **Una tarjeta del jefe desaparece sin que él lo pida.** Pasada 1248, turno 4: el jefe dice «trag als Notiz
   ein», la wiedergabe lo convierte en «Karte im Fokus korrigieren» y Linus llama `karte_verwerfen
   {welche:"fokus"}` sobre su tarjeta de borrado. En la 1255 la misma reinterpretación sin tirarla.
2. **Dice el estado en vez de leerlo.** Pasada 1242: «ich merke die Karte vor» / «sie wartet auf deine
   Freigabe» sin tarjeta, en tres turnos de cinco. Pasada 1255, turno 10: «Rückgängig» por voz no devolvió el
   contacto mientras Linus decía que lo hacía (lo devolvió la limpieza del banco).
3. **El hueco del freno, con daño medido.** Pasada 1248, turno 2: abschrift «Die mit Kysolt», que no nombra
   ninguna fila; el modelo eligió la fila por Kennung y `merkmalBelegt` lo bendijo, porque comprueba que las
   palabras sean del jefe, no que señalen esa fila. Aquí acertó; anoche, con «Die mit Kisult», falló.

## Qué se añadió al banco

- `keinFalschesVorgemerkt`: mide frase a frase que no se afirme una tarjeta inexistente. Verificado contra las
  ocho frases reales de la pasada 1242 antes de darlo por bueno (un «soll» al final del turno no puede
  excusar la afirmación del principio; «keyshold.com» no debe partirse por su propio punto).
- `nichtsWeggeworfen`: ninguna llamada a `karte_verwerfen` en turnos donde el jefe no lo pidió.
- Dos turnos opcionales que **contestan a lo que Linus acaba de preguntar** («Nein» si leyó otra fila, «Ja» si
  leyó la del jefe). El audio se genera antes de la pasada, así que el texto tiene que ser fijo: dos turnos
  excluyentes, no uno que decida sus palabras en el micrófono.
- Copia de los contactos a disco antes de cada pasada, y la limpieza dice **cuál** de las dos vías devolvió un
  borrado.

## Dos fallos propios, corregidos

- Los asertos viejos que tumbaron la CI (arriba).
- Una línea de limpieza que yo mismo había escrito una hora antes afirmaba que el «Rückgängig» del recorrido
  había devuelto el contacto, cuando la tarjeta estaba rechazada y no se había borrado nada. Es la misma clase
  de frase que llevamos dos días quitando del producto, y la tenía en mi propio informe.

## Estado al cerrar

Canario `a2-4b46156` con los tres contactos verificados en vivo y sus mismas Kennungen. Rama en `83edd5f`
(solo banco por encima de main). CI de main sobre `4b46156` lanzada a las 12:15, todavía en marcha al cerrar;
la de la rama, con el mismo árbol, en verde.

Horas reales: 4,5 h de trabajo (14 h de reloj, 9,5 h de huecos descontados). ~1,5 h de máquina no contadas.
