# Comparación a ojo: humo v2 sobre gatekeeper (DeepSeek V3.2, prompt con las seis reglas)

Código `f09996d2`, mismo que la v1. 6 hallazgos, 0 descartados por `linea_prueba`, 0,0081 $. «Ejecutado» = comprobado corriendo el código con Node 24.

**Resultado: 0 reales, 0 dudosos, 6 ruido (100 %).** Peor que la v1 (72 %): además se pierde el único real (metadatos sin tapar, `gatekeeper.ts:114/152`).

| # | Punto | Sitio | Veredicto | Porqué |
|---|---|---|---|---|
| 1 | 1 | gatekeeper.ts:192 | ruido | Ejecutado: un payload con «[Zugangsdaten entfernt]» y «[Kontonummer entfernt]» sale `clean`, sin segunda redacción. |
| 2 | 4 | gatekeeper.ts:96 | ruido | Bloqueo de adjunto sin clasificar: regla del spec, igual que en la v1. |
| 3 | 5 | gatekeeper.ts:114 | ruido | Una tarjeta partida entre asunto y contenido es un caso inventado; además el punto 5 (carreras) no tiene nada que ver. |
| 4 | 9 | layer1.ts:327 | ruido | Ejecutado: «Passwort: Passwort: geheim123» sale «Passwort: Passwort: [Zugangsdaten entfernt]». No se filtra nada; el caso está documentado en `jederTreffer`. |
| 5 | 15 | layer1.ts:95 | ruido | Tapa de más (lado seguro), y «ändere» sin cifras ni símbolos no pasa `looksLikeSecret`. |
| 6 | 10 | layer1.ts:122 | ruido | Apunta a un comentario; el caso (tarjeta pegada a una UUID sin separador) es inventado. |

Observaciones: el filtro `linea_prueba` no tiró nada (el modelo copia líneas que existen, también para hallazgos falsos). El tope de 3 por trozo actúa como cuota: dos trozos devolvieron exactamente 3.
