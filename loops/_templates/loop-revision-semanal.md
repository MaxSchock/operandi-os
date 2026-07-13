# Plantilla · Revisión semanal de loops

Automatiza la revisión semanal de todos los loops activos: métricas, aprendizaje y propuestas
de autonomía. Es el meta-loop del sistema y encaja con el ritual semanal H2 de `metodo-ias`.
Tiempo estimado de personalización: 10 minutos.

```text
LOOP CANVAS — revision semanal            v1.0 · [PERSONALIZA: fecha de creación] · Diseñado por: [PERSONALIZA: usuario] + Claude

1 · OBJETIVO Y "HECHO"
   Produce: scorecard semanal de todos los loops activos + decisiones de autonomía registradas.
   Hecho cuando: existe una tabla con las 5 métricas por loop, cada propuesta cita su métrica, las decisiones humanas quedan anotadas y `loops/_index.md` está actualizado.

2 · DISPARADOR
   [x] Manual por lote ("procesa la cola")
   [x] Programado: viernes vía tarea programada de Claude Desktop; encaja con el ritual semanal H2 de `metodo-ias` [PERSONALIZA: hora]
   [ ] Por evento: [PERSONALIZA: cierre de semana o final de `/wrap-up`]

3 · COLA DE ENTRADA
   Vive en: `loops/_index.md`
   Un item está LISTO cuando tiene: loop activo con `loop-state.md`, `REGLAS.md`, nivel A actual y fecha de última revisión.

4 · ESTACIONES (3–7, en orden)
   E1 Recoger métricas : loop activo → métricas desde `loop-state.md` + aprendizaje desde `REGLAS.md`
   E2 Scorecard : métricas recogidas → tabla con first-pass yield, retrabajo, tiempo de ciclo, escalaciones y reglas/semana
   E3 Propuestas : scorecard → propuestas de subir/bajar nivel A, podar reglas, ajustar checklist o matar loops que no rinden
   E4 Decisión y registro : propuestas revisadas → decisión humana + actualización de `loops/_index.md` y `context/decisions-log.md` si aplica

5 · OPERARIO POR ESTACIÓN
   E1 → Claude
   E2 → skill `automation-loop-engine` en MODO EVALUACIÓN
   E3 → skill `automation-loop-engine` en MODO EVALUACIÓN
   E4 → el usuario decide; Claude registra solo lo aprobado
   Checker de E3 → el usuario, separado de la propuesta generada por `automation-loop-engine`.

6 · VERIFICACIÓN AUTOMÁTICA (el checklist, máx. 5 criterios binarios)
   ☐ Cada loop activo de `loops/_index.md` aparece en la tabla
   ☐ Cada propuesta cita al menos una métrica concreta
   ☐ Ninguna decisión de autonomía se ejecuta sin aprobación humana
   ☐ `loops/_index.md` refleja fecha de revisión y nivel A aprobado
   ☐ Las decisiones relevantes quedan en `context/decisions-log.md`
   Auto-corrección: máx. 3 intentos antes de escalar.

7 · COMPUERTAS HUMANAS
   Estación E4 → nivel A1 — el usuario aprueba antes de subir/bajar autonomía, matar loops o cambiar compuertas.
   Innegociables (siempre humanas): salida a cliente · dinero · irreversibles · compromisos · toda decisión de autonomía.
   [PERSONALIZA: otras compuertas propias de tu CONFIG]

8 · CONDICIONES DE PARADA
   Presupuesto por item: máx. 1 revisión por loop y 60 minutos para la revisión semanal completa.
   Escala al usuario si: faltan métricas · `loop-state.md` no existe · hay reglas contradictorias · una propuesta afectaría a cliente/dinero/compromisos.
   Kill switch: "pausa el loop de revisión semanal" → no se actualiza ningún índice ni decisión.

9 · MÉTRICAS Y APRENDIZAJE
   Se mide: nº loops revisados · decisiones tomadas · reglas podadas · escalaciones · reglas/semana
   Estado del loop vive en: `loops/revision-semanal/loop-state.md`
   Reglas aprendidas viven en: `loops/revision-semanal/REGLAS.md` (toda corrección del usuario → regla numerada)
   Revisión: semanal, 15 min — viernes dentro del H2 de `metodo-ias` [PERSONALIZA: hora]
```

## Primer lote piloto

Revisa 3 loops activos o, si todavía no existen, 3 plantillas candidatas. Observa: si las
métricas están disponibles, si las propuestas son trazables a datos y si el usuario acepta,
rechaza o modifica las decisiones de autonomía.
