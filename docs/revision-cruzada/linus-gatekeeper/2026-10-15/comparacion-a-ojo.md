# Comparación a ojo: prueba de humo sobre gatekeeper (15-10-2026)

Código: `~/max-assistent-kartenbau/packages/gatekeeper/src` en `f09996d2`. Modelo `deepseek/deepseek-v3.2`, 18 hallazgos, 0,0085 $.
Los casos marcados «ejecutado» se comprobaron corriendo el código con Node 24 (prueba en el scratchpad, nada escrito en el repo).

**Resultado: 2 reales (el mismo fallo dos veces), 3 dudosos, 13 ruido (72 %).** Pasa de la mitad: el pase grande NO se ejecuta.

| # | Punto | Sitio | Veredicto | Porqué |
|---|---|---|---|---|
| 1 | 1 | gatekeeper.ts:114 | real | Ejecutado: con un IBAN en `meta.sender` sale `redactedContent: "Hallo, bitte zahlen.[Kontonummer entfernt]"`. Los tramos se calculan sobre contenido+metadatos y se aplican solo a `content`: el contenido gana un marcador que no le toca y el remitente sigue en claro. Afecta a `chat-lesen.ts:142` (sender) y a `attachmentName` (`klassifizieren.ts:87`, `real-backend.ts:6159`). |
| 2 | 4 | gatekeeper.ts:95 | ruido | Bloquear un adjunto sin clasificar es la regla del spec, con motivo `attachment-not-classified`; el aviso al usuario es cosa del que llama. |
| 3 | 5 | gatekeeper.ts:114 | real (duplicado de 1) | Mismo fallo, contado con otro punto. |
| 4 | 8 | gatekeeper.ts:164 | ruido | Mostrar datos propios en la app es decisión de diseño; un falso positivo ahí no filtra nada. |
| 5 | 9 | gatekeeper.ts:114 | ruido | Una carpeta mal declarada bloquea de más: falla hacia el lado seguro. |
| 6 | 10 | gatekeeper.ts:191 | ruido | Un string en memoria no es una fuga; el evento que se guarda es el limpio. |
| 7 | 12 | gatekeeper.ts:82 | ruido | `decidedByLayer` es informativo; no hay escenario donde se pierda o se filtre algo. |
| 8 | 15 | gatekeeper.ts:100 | dudoso | Igualdad exacta (`INBOX/Privat` no coincidiría), pero hoy ningún llamador pasa `meta.folder`: camino muerto. |
| 9 | 15 | layer1.ts:95 | ruido | Ejecutado: «Passwort vergessen: Herbst2026!» sale como «Passwort vergessen: [Zugangsdaten entfernt]». Lo caza el segundo patrón, que el modelo no leyó. |
| 10 | 15 | layer1.ts:101 | dudoso | Cierto que una frase de contraseña en minúsculas sin cifras no se tapa, pero es un límite asumido de la heurística, no un error. |
| 11 | 15 | layer1.ts:92 | ruido | Ejecutado: «PIN: 1234» se tapa (primer patrón). El ejemplo del modelo (9 cifras) supera el umbral de 6. |
| 12 | 15 | layer1.ts:126 | ruido | El comentario documenta la exclusión medida; una tarjeta real no empieza dentro de una UUID. |
| 13 | 4 | layer1.ts:157 | ruido | `null` es el resultado normal de «no es IBAN válido», no una excepción tragada. |
| 14 | 8 | layer1.ts:360 | dudoso | Ejecutado el mecanismo: `redactSpans` con tramos [5,10] y [8,15] deja en claro 10-15. En `findings()` los tramos del diccionario no pasan por `dropOverlaps`, así que puede pasar; falta un texto real en el que un término de salud solape el inicio de un IBAN o una clave. |
| 15 | 15 | layer2-ner.ts:74 | ruido | El propio modelo concluye que no hay escenario. |
| 16 | 15 | layer2-ner.ts:98 | ruido | Casar por prefijo es deliberado (palabras compuestas); el ejemplo «klinik» en «klinisch» es falso, no lo contiene. |
| 17 | 4 | layer2-ner.ts:66 | ruido | Hipotético (`null` en `extraTerms`) sin camino real. |
| 18 | 12 | layer2-ner.ts:70 | ruido | Rendimiento, fuera de la lista. |

## Por qué sale tanto ruido

- La confianza no separa: hay ruido con 0,9 (9, 11) y un real con 0,7 (3). Un filtro por confianza no lo arregla.
- El modelo no comprueba el resto del fichero antes de afirmar (9 y 11 los cazan otras reglas del mismo trozo).
- Reporta decisiones documentadas en comentarios como fallos (2, 4, 12, 16).
- Mete hipótesis sin camino real (6, 13, 17) y temas fuera de la lista (18).
- Rellena: 18 hallazgos en 761 líneas, cuando lo esperable es 0 a 3.

## Ajuste propuesto del prompt (`SISTEMA` en `pasar.py`, línea 322)

Añadir a «Reglas de respuesta»:

1. Antes de incluir un hallazgo, recorre el CÓDIGO A REVISAR completo y comprueba que ninguna otra regla, rama o patrón del mismo trozo ya cubre el caso. Si lo cubre, no lo incluyas.
2. Si un comentario del código explica el comportamiento como decisión tomada o medida, no es un hallazgo salvo que el escenario rompa lo que dice ese comentario.
3. Fuera: rendimiento, memoria, mensajes al usuario, «podría fallar si hubiera un error interno», y casos que fallan hacia el lado seguro (bloquear o tapar de más).
4. `escenario_de_fallo` debe dar la entrada literal y el recorrido por líneas que lleva al fallo; si no puedes escribir la entrada literal, no lo incluyas.
5. Como mucho 3 hallazgos por trozo, los de más daño. Lo normal es devolver [].
6. Campo nuevo `linea_prueba`: la línea exacta del código que produce el fallo, copiada tal cual (se valida que exista en el trozo y se descarta si no).

Después del ajuste, repetir la prueba de humo sobre gatekeeper (0,01 $) y volver a comparar a ojo antes de lanzar el pase de Linus. Si sigue por encima del 50 % de ruido, probar `qwen/qwen3-coder` con el mismo prompt antes de subir de precio.
