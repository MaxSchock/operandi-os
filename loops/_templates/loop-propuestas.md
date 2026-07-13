# Plantilla · Propuestas

Automatiza el paso de solicitud de cliente a propuesta lista para revisión humana. Pensada
para freelancers, agencias, consultoras y equipos que reciben oportunidades comerciales.
Tiempo estimado de personalización: 10 minutos.

```text
LOOP CANVAS — propuestas            v1.0 · [PERSONALIZA: fecha de creación] · Diseñado por: [PERSONALIZA: usuario] + Claude

1 · OBJETIVO Y "HECHO"
   Produce: propuesta de cliente lista para revisión humana.
   Hecho cuando: la propuesta incluye contexto correcto del cliente, alcance con entregables y fechas, precios marcados como decisión humana `[DECIDE TÚ]`, y siguiente paso claro.

2 · DISPARADOR
   [x] Manual por lote ("procesa la cola")
   [ ] Programado: [PERSONALIZA: cadencia si revisas oportunidades en bloque] vía tarea programada de Claude Desktop
   [x] Por evento: llega una solicitud de cliente por email, formulario, CRM o mensaje directo

3 · COLA DE ENTRADA
   Vive en: `loops/propuestas/cola.md`
   Un item está LISTO cuando tiene: quién pide + qué pide + presupuesto orientativo si lo hay + fecha límite.

4 · ESTACIONES (3–7, en orden)
   E1 Investigación del cliente : datos del solicitante → resumen verificable usando `strategy-web-research` + `tool-firecrawl-scraper`
   E2 Encaje y ángulo : investigación + `brand-context/icp/icp.md` → encaje, dolor probable y ángulo usando `marketing-icp` + `marketing-positioning`
   E3 Redacción : E1+E2 + catálogo/plantillas [PERSONALIZA: ruta] → borrador de propuesta usando `marketing-copywriting`
   E4 Versión visual HTML : borrador aprobado internamente → HTML compartible usando `tool-visual-explainer`
   E5 Verificación : propuesta + HTML → checklist objetivo usando `tool-output-verifier`

5 · OPERARIO POR ESTACIÓN
   E1 → skills `strategy-web-research` y `tool-firecrawl-scraper`
   E2 → skills `marketing-icp` y `marketing-positioning`
   E3 → skill `marketing-copywriting`
   E4 → skill `tool-visual-explainer`
   E5 → skill `tool-output-verifier`
   Checker de E3 → `tool-output-verifier`, separado de `marketing-copywriting`.

6 · VERIFICACIÓN AUTOMÁTICA (el checklist, máx. 5 criterios binarios)
   ☐ Nombre, web y sector del cliente correctos
   ☐ Cero cifras, resultados o credenciales inventadas
   ☐ Todos los entregables incluyen fecha o condición de entrega
   ☐ Todo precio aparece como `[DECIDE TÚ]`
   ☐ Estructura completa: contexto → propuesta → alcance → siguiente paso
   Auto-corrección: máx. 3 intentos antes de escalar.

7 · COMPUERTAS HUMANAS
   Estación E3 → nivel A1 — el usuario aprueba alcance, fechas y precio antes de enviar.
   Estación E4 → nivel A1 — el usuario revisa antes de compartir con cliente.
   Innegociables (siempre humanas): salida a cliente · dinero · irreversibles · compromisos · precio · alcance · envío.
   [PERSONALIZA: otras compuertas propias de tu CONFIG]

8 · CONDICIONES DE PARADA
   Presupuesto por item: 1 ciclo completo por solicitud y máx. 3 autocorrecciones.
   Escala al usuario si: falta información clave del cliente tras investigar · la petición está fuera de catálogo · hay condiciones comerciales especiales · no existe presupuesto orientativo.
   Kill switch: "pausa el loop de propuestas" → no se prepara ni envía ninguna propuesta nueva.

9 · MÉTRICAS Y APRENDIZAJE
   Se mide: first-pass yield · retrabajo · tiempo solicitud→propuesta · tasa de escalación · reglas/semana
   Estado del loop vive en: `loops/propuestas/loop-state.md`
   Reglas aprendidas viven en: `loops/propuestas/REGLAS.md` (toda corrección del usuario → regla numerada)
   Revisión: semanal, 15 min — [PERSONALIZA: día y hora]
```

## Primer lote piloto

Procesa 3 solicitudes reales o simuladas en A1. Observa: si faltan datos mínimos en la cola,
si el precio queda siempre para decisión humana, si la investigación cita fuentes suficientes
y qué partes del alcance corrige el usuario.
