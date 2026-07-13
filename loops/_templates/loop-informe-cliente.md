# Plantilla · Informe de cliente

Automatiza informes periódicos por cliente con avances, métricas y siguientes pasos en HTML
listo para enviar. Pensada para el modo multi-cliente del OS (`clients/`). Tiempo estimado de
personalización: 10 minutos.

```text
LOOP CANVAS — informe cliente            v1.0 · [PERSONALIZA: fecha de creación] · Diseñado por: [PERSONALIZA: usuario] + Claude

1 · OBJETIVO Y "HECHO"
   Produce: informe periódico por cliente en HTML listo para revisión y envío.
   Hecho cuando: el HTML incluye avances, métricas con fuente, siguientes pasos accionables y datados, tono register B, y queda guardado en `clients/<cliente>/projects/` o [PERSONALIZA: ruta].

2 · DISPARADOR
   [x] Manual por lote ("procesa la cola")
   [x] Programado: viernes vía tarea programada de Claude Desktop o dentro de `/wrap-up` del viernes [PERSONALIZA: hora]
   [ ] Por evento: [PERSONALIZA: cierre de sprint, entrega o actualización de métricas]

3 · COLA DE ENTRADA
   Vive en: clientes activos en `clients/` (cada cliente = 1 item)
   Un item está LISTO cuando tiene: carpeta de cliente activa + notas o métricas de la semana + destinatario o canal de envío [PERSONALIZA: ubicación de notas].

4 · ESTACIONES (3–7, en orden)
   E1 Recolección : `clients/<cliente>/` → notas, métricas y decisiones de la semana con rutas fuente
   E2 Síntesis : notas y métricas → resumen semanal, riesgos y siguientes pasos
   E3 Informe HTML : síntesis + marca del cliente/operador → HTML autocontenido usando `tool-visual-explainer`
   E4 Verificación : informe + fuentes → checklist objetivo usando `tool-output-verifier`
   E5 Registro : informe aprobado → línea de estado enviado/pendiente en el cliente

5 · OPERARIO POR ESTACIÓN
   E1 → Claude leyendo solo archivos del cliente correspondiente
   E2 → Claude con contexto del cliente y decisiones recientes
   E3 → skill `tool-visual-explainer`
   E4 → skill `tool-output-verifier`
   E5 → Claude
   Checker de E3 → `tool-output-verifier`, separado de `tool-visual-explainer`.

6 · VERIFICACIÓN AUTOMÁTICA (el checklist, máx. 5 criterios binarios)
   ☐ Todo dato o métrica tiene fuente en archivos del cliente
   ☐ No hay relleno genérico ni afirmaciones sin evidencia
   ☐ Los siguientes pasos son accionables y tienen fecha o responsable
   ☐ El tono respeta el register B del voice profile
   ☐ El HTML está guardado en la ruta del cliente y listo para revisar
   Auto-corrección: máx. 3 intentos antes de escalar.

7 · COMPUERTAS HUMANAS
   Estación E4 → nivel A1 — el usuario aprueba antes de enviar el informe al cliente.
   Estación E5 → nivel A1 — el usuario confirma enviado/pendiente si implica comunicación externa.
   Innegociables (siempre humanas): salida a cliente · dinero · irreversibles · compromisos · envío del informe.
   [PERSONALIZA: otras compuertas propias de tu CONFIG]

8 · CONDICIONES DE PARADA
   Presupuesto por item: máx. 3 autocorrecciones o 30 minutos por cliente.
   Escala al usuario si: el cliente no tiene notas esa semana · faltan métricas prometidas · hay conflicto entre archivos · hay decisión sensible no registrada.
   Kill switch: "pausa el loop de informes cliente" → no se genera ni envía ningún informe nuevo.

9 · MÉTRICAS Y APRENDIZAJE
   Se mide: first-pass yield · retrabajo · tiempo por informe · clientes saltados/semana · reglas/semana
   Estado del loop vive en: `loops/informe-cliente/loop-state.md`
   Reglas aprendidas viven en: `loops/informe-cliente/REGLAS.md` (toda corrección del usuario → regla numerada)
   Revisión: semanal, 15 min — [PERSONALIZA: día y hora]
```

## Primer lote piloto

Procesa 3 clientes activos en A1. Observa: qué clientes no tienen notas suficientes, si cada
métrica tiene fuente, si los siguientes pasos son realmente accionables y qué tono corrige el
usuario antes del envío.
