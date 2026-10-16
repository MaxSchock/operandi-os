# Comparación a ojo: humo sobre gatekeeper con qwen/qwen3-coder (prompt con las seis reglas)

Código `f09996d2`. 9 hallazgos, 0 descartados por `linea_prueba`, 0,0092 $.

**Resultado: 0 reales, 1 dudoso, 8 ruido (89 %).** Tampoco encuentra el real de la v1.

| # | Punto | Sitio | Veredicto | Porqué |
|---|---|---|---|---|
| 1 | 15 | gatekeeper.ts:101 | dudoso | Igualdad exacta de carpeta (ya dudoso en la v1); lo de mayúsculas es falso (se pasa a minúsculas en la 100) y hoy ningún llamador manda `meta.folder`. |
| 2 | 1 | gatekeeper.ts:190 | ruido | Limpiar dos veces un evento no daña nada (ejecutado en la v2: los marcadores salen `clean`). |
| 3 | 9 | gatekeeper.ts:250 | ruido | Tapar de más bajo la clave `password` es el lado seguro y está documentado. |
| 4 | 15 | layer1.ts:44 | ruido | Es exactamente el caso medido y resuelto el 14-09 que explica el comentario. |
| 5 | 15 | layer1.ts:151 | ruido | Ejemplo con caracteres que no son hex; no es una UUID ni un IBAN. |
| 6 | 1 | layer1.ts:213 | ruido | Falso positivo de tarjeta: tapa de más, lado seguro. |
| 7 | 15 | layer2-ner.ts:74 | ruido | «Schwarzt» y «Kardiologenarzt» no casan: `startsAtWordBoundary` exige que antes no haya letra. |
| 8 | 15 | layer2-ner.ts:76 | ruido | Mismo error que el 7. |
| 9 | 15 | layer2-ner.ts:85 | ruido | `from = index + term.length` sí encuentra la segunda aparición. |
