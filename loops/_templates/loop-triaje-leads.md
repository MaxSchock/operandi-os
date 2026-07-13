# Plantilla · Triaje de leads

Automatiza el enriquecimiento, puntuación ICP y primera respuesta de leads nuevos. Pensada
para negocios con formularios, CRM, hojas de leads o bandejas de entrada comerciales. Tiempo
estimado de personalización: 10 minutos.

```text
LOOP CANVAS — triaje leads            v1.0 · [PERSONALIZA: fecha de creación] · Diseñado por: [PERSONALIZA: usuario] + Claude

1 · OBJETIVO Y "HECHO"
   Produce: ficha enriquecida del lead + puntuación contra ICP + borrador de primera respuesta.
   Hecho cuando: la ficha tiene datos verificados, fit alto/medio/bajo con 3 razones citables, borrador personalizado y estado registrado.

2 · DISPARADOR
   [x] Manual por lote ("procesa la cola")
   [x] Programado: al empezar el día vía tarea programada de Claude Desktop [PERSONALIZA: hora]
   [x] Por evento: entra un lead nuevo en CRM, hoja, formulario o email [PERSONALIZA: herramienta]

3 · COLA DE ENTRADA
   Vive en: [PERSONALIZA: CRM/hoja/bandeja donde gestionas leads] o, por defecto, `loops/triaje-leads/cola.md`
   Un item está LISTO cuando tiene: nombre o empresa + canal de contacto + necesidad declarada + origen del lead.

4 · ESTACIONES (3–7, en orden)
   E1 Enriquecer : lead básico → ficha con qué hace, tamaño y señales verificadas usando `strategy-web-research` + `tool-firecrawl-scraper`
   E2 Puntuar ICP : ficha + `brand-context/icp/icp.md` → fit alto/medio/bajo + 3 razones citables usando `marketing-icp`
   E3 Responder : ficha + score + register cercano → borrador de primera respuesta usando `marketing-copywriting`
   E4 Verificar y registrar : ficha + borrador → checklist pasado + estado actualizado usando `tool-output-verifier`

5 · OPERARIO POR ESTACIÓN
   E1 → skills `strategy-web-research` y `tool-firecrawl-scraper`
   E2 → skill `marketing-icp`
   E3 → skill `marketing-copywriting`
   E4 → skill `tool-output-verifier` + Claude para registrar estado
   Checker de E3 → `tool-output-verifier`, separado de `marketing-copywriting`.

6 · VERIFICACIÓN AUTOMÁTICA (el checklist, máx. 5 criterios binarios)
   ☐ Los datos del lead están verificados y no son supuestos
   ☐ El score incluye 3 razones citables contra ICP
   ☐ El borrador menciona algo específico del lead
   ☐ El borrador no promete precio, plazo ni resultado
   ☐ La ficha queda registrada con estado y siguiente acción
   Auto-corrección: máx. 3 intentos antes de escalar.

7 · COMPUERTAS HUMANAS
   Estación E3 → nivel A1 — el usuario aprueba antes de enviar cualquier respuesta.
   Estación E2 → nivel A1 inicial; puede proponerse A2 tras 10 leads seguidos aceptados sin tocar.
   Innegociables (siempre humanas): salida a cliente · dinero · irreversibles · compromisos · envío de respuesta.
   [PERSONALIZA: otras compuertas propias de tu CONFIG]

8 · CONDICIONES DE PARADA
   Presupuesto por item: máx. 3 autocorrecciones o 20 minutos por lead.
   Escala al usuario si: faltan datos mínimos · no hay fuente verificable · el lead pide precio/plazo cerrado · el ICP no existe o está desactualizado.
   Kill switch: "pausa el loop de triaje leads" → no se procesa ningún lead nuevo.

9 · MÉTRICAS Y APRENDIZAJE
   Se mide: first-pass yield · retrabajo · tiempo por lead · % leads con datos insuficientes · reglas/semana
   Estado del loop vive en: `loops/triaje-leads/loop-state.md`
   Reglas aprendidas viven en: `loops/triaje-leads/REGLAS.md` (toda corrección del usuario → regla numerada)
   Revisión: semanal, 15 min — [PERSONALIZA: día y hora]
```

## Primer lote piloto

Procesa 3 leads en A1. Observa: cuántos llegan sin datos mínimos, si las razones de score son
citables, si el borrador suena específico y si el usuario cambia la clasificación ICP.
