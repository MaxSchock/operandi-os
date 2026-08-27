# Sesión 1 · Inventario de fricción (mayo-agosto 2026)

Corpus: 319 chats completos del 12-05 al 27-08 (`_wiki/raw/chat-history/`, 50 MB en bruto, destilados a 3,2 MB de 4.414 mensajes humanos). Extracción semántica en 17 lotes paralelos. Dataset completo: [`incidentes.json`](incidentes.json).

## El número

**596 incidentes** en 108 días: momentos en que Max corrigió, repitió una norma, tuvo que recordar un estado o expresó frustración. Una media de **5,5 por día trabajado**.

| | |
|---|---|
| Correcciones | 404 |
| Reglas que Max tuvo que repetir | 98 |
| Frustración explícita | 70 |
| Estado que Max tuvo que recordar | 24 |
| **Gravedad alta** (consecuencia externa o trabajo tirado) | **172** |

Reparto por mes: mayo 112 · junio 240 · julio 80 · agosto 164. Por entidad: KIsult 313 · Operandi 203 · Falkenlead 39 · interno 37.

## El hallazgo central

**252 de los 490 incidentes clasificables (51%) ocurrieron cuando la regla ya estaba escrita en el sistema.** De ellos, 77 de gravedad alta.

El problema no es que no se apunten las cosas. Se apuntan bien: 123 ficheros de memoria con su Why y su How to apply. Se repiten igual, porque **nada las hace llegar al momento en que hay que aplicarlas**.

## Patrones raíz

Las 549 formulaciones distintas se reducen a 14 patrones. La columna "reincidencia" cuenta los incidentes posteriores a la fecha en que la regla ya existía por escrito.

| Patrón | Inc. | Regla escrita desde | Reincidencia | Alta |
|---|---:|---|---:|---:|
| Verificar antes de afirmar / dar por hecho | 96 | 13-06 | **65 (67%)** | 20 |
| Deliverable de cliente (idioma, nivel, formato, atribución) | 83 | 13-06 | **63 (75%)** | 20 |
| Envío externo (hilo real, entidad correcta, canario) | 50 | 16-06 | **32 (64%)** | 12 |
| Comunicación con Max (castellano llano, paso a paso, directo) | 45 | 13-06 | 21 (46%) | 1 |
| Autonomía: no pedir permiso, no delegar en Max | 28 | 13-06 | 10 (35%) | 0 |
| "No puedo" sin haber mirado | 26 | 27-08 (hoy) | — | 5 |
| Recall de estado ya establecido | 26 | *sin regla* | — | 7 |
| Calidad del output generado (imagen, voz, variedad) | 24 | 13-06 | 12 (50%) | 4 |
| Horas y facturación | 23 | 14-07 | **14 (60%)** | 7 |
| Ruta/herramienta correcta (Unipile, OAuth, capturas) | 22 | 13-06 | 5 (22%) | 2 |
| Alcance y disciplina (un problema a la vez, no complicar) | 21 | 23-06 | 6 (28%) | 1 |
| Cierre parcial presentado como completo | 17 | 15-06 | 12 (70%) | 4 |
| Atribución de entidad/cliente | 16 | 13-06 | 7 (43%) | 3 |
| Borrado / acción destructiva | 10 | 13-06 | **3** (verificado a mano) | 3 |
| Secretos en claro | 3 | 02-06 | **0** | 0 |

*(106 incidentes quedan sin patrón raíz: casos únicos que no se repiten. 17% del total.)*

## Las tres reglas irrompibles, contrastadas

- **Nunca borrar sin backup** (regla 1): 7 borrados reales, 3 de ellos posteriores a la regla. El más grave, el 18-08: limpié el buzón de pruebas E2E de Hemmersbach antes de que pudieras ver los resultados.
- **Nunca enviar sin revisar el hilo** (regla 2): **32 incidentes posteriores a la regla**, 12 de gravedad alta. El cruce de entidades del 24-06 (tests de Hemmersbach enviados desde Operandi) se repitió dos veces el mismo día.
- **Secretos**: 3 incidentes, todos anteriores a la regla, **cero reincidencia**.

## Por qué secretos es la excepción que explica todo lo demás

Secretos es el único patrón con reincidencia cero. También es el único cubierto por un mecanismo que **se dispara solo**: el instinto `env-vars-never-hardcode`, con 10.883 activaciones registradas desde mayo. Se inyecta en cada comando que huele a credencial, sin que nadie se acuerde de nada.

Las otras trece reglas viven en ficheros que nadie lee en tiempo de ejecución. Su reincidencia va del 22% al 75%.

La muestra de secretos es pequeña (3 incidentes) y no prueba una ley por sí sola. Pero la dirección coincide con el resto de la evidencia: **lo que se activa, se cumple; lo que solo está escrito, se repite.**

## Qué habría evitado cada incidente

| Vía | Inc. | Lectura |
|---|---:|---|
| Mejor razonamiento | 388 | La información estaba y aun así fallé. Aquí es donde muerde la sobrecarga: 74 KB de reglas planas en cada arranque, todas al mismo nivel de prioridad |
| Inyección de la regla en el momento | 75 | Directamente resoluble con un activador en `UserPromptSubmit` |
| Recall de un dato o estado que existía | 73 | Directamente resoluble conectando el índice de memoria (hoy indexa 3 ficheros) |
| Un gate técnico que bloquee la acción | 55 | Las 55 más peligrosas: envíos, borrados, cruces de entidad |
| Imprevisible | 5 | |

## Fiabilidad de este inventario

- **Spot-check adversarial**: 6 incidentes al azar verificados contra el transcript original. 6 de 6 citas literales correctas, 2 de 2 interpretaciones revisadas a fondo correctas. El campo `turno` que devuelven los extractores es poco fiable; la cita y el chat sí localizan el momento.
- **Auditoría manual de las categorías pequeñas y graves**: en "borrado" encontré 2 falsos positivos de la clasificación automática y corregí la cifra de 5 a 3. Las categorías con menos de 15 incidentes tienen margen de error apreciable; las grandes son robustas por volumen.
- **Sesgo de superviviente**: esto solo recoge lo que Max vio y corrigió. Lo que se le pasó no está aquí.
- **Las fechas de alta de las reglas son conservadoras**: muchas marcan 13-06 porque es cuando arrancó el repositorio que las versiona. Varias existían antes, así que el 51% de reincidencia es un suelo, no un techo.

## Handoff a la Sesión 2

Preguntas que S2 tiene que responder con el inventario en la mano:

1. Las 62 reglas no enlazadas en `MEMORY.md`, ¿a qué patrones corresponden y cuántos incidentes explican?
2. ¿Qué reglas se contradicen entre capas? (medición léxica descartada por insuficiente: hay que leer el contenido)
3. ¿Qué reglas están muertas — escritas, cargadas y sin un solo incidente asociado en cuatro meses?
4. Diagnóstico de Sinapsis: por qué el learner escribe "no patterns", por qué 41 de 53 instintos nunca disparan, si `/evolve` sigue vivo. Reparar o jubilar, componente a componente.
5. Los 106 incidentes sin patrón raíz: ¿casos únicos de verdad, o un patrón que no supe ver?
