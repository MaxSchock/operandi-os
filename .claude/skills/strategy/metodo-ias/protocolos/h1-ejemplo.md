# H1 — Sesión end-to-end (ejemplo)

> Caso ficticio realista. Un operador genérico que usa el método I.A.S. prepara un activo concreto.
> Activo a producir: pitch deck de 12 slides para una reunión con un inversor pre-seed.
> Fecha de la sesión: 2026-05-06.

---

## 1. Arranque con `/ias-start`

El operador escribe en Claude Code:

```
/ias-start pitch-deck-inversor
```

El comando lanza el protocolo H1. El agente carga la plantilla del checklist (`h1-checklist-template.md`) en memoria y empieza a interrogar dimensión por dimensión, sin permitir saltos.

Mensaje inicial del agente (en tono humano, sin jerga interna del protocolo):

```
Antes de meterte con el agente, necesito una cosa para que el resto fluya.
¿Qué activo concreto sale de esta sesión y quién lo recibe?
```

---

## 2. Rellenado del checklist

### Dimensión 1 — Objetivo concreto

Operador:

> Pitch deck de 12 slides para una reunión presencial el martes 12 de mayo a las 11:00 con una inversora ángel especializada en SaaS B2B. Sirve para abrir conversación de ronda pre-seed (ticket objetivo 100k).

Agente: dimensión cubierta.

### Dimensión 2 — Inputs disponibles

Operador:

> Tengo el guion de la conversación inicial con la inversora en `inputs/conversacion-2026-04-25.md`, métricas actuales de la app en `inputs/metrics-abril.csv`, deck antiguo de la última ronda en `inputs/deck-pre-ronda-2025-12.pptx`, y notas sobre la tesis de inversión de la inversora en `inputs/tesis-inversora.md`.

Agente: dimensión cubierta.

### Dimensión 3 — Restricciones

Operador:

> Tiempo: sesión de 90 minutos como máximo, hard-stop a las 23:00. Audiencia: inversora ángel con perfil financiero y técnico, lee deck antes de la reunión y luego comenta. Idioma: español. Formato presentación: lectura en pantalla en remoto (Notion público o PDF), no presencial.

Agente: dimensión cubierta.

### Dimensión 4 — Formato del output

Operador:

> 12 slides exactas con esta estructura: portada, problema, solución, demo (mock estático), mercado, modelo de negocio, tracción, equipo, competencia, plan de uso de fondos, ask, contacto. Una idea por slide. Texto corto (<40 palabras por slide). Las slides salen en `outputs/decks/2026-05-12-inversor-pre-seed/`.

Agente: dimensión cubierta.

### Dimensión 5 — Criterios de aceptación

Operador:

> Cuando esté bien quiero que se vea profesional y sólido.

Agente:

```
Eso no me sirve para saber cuándo parar. "Profesional y sólido" lo decide
quien lo lee y a esa hora ya es tarde. Reformula como cosas verificables
por un tercero — por ejemplo: ¿cuántas cifras con fuente? ¿qué slides
llevan número? ¿hay algo que no debe aparecer?
```

**Aquí el flujo se detiene por primera vez.** El operador reformula:

> Cierra cuando: (a) las 12 slides están maquetadas con el contenido definitivo, (b) las slides 5, 6, 7 y 10 llevan al menos una cifra con fuente nombrada (mercado, pricing, métricas, uso de fondos), (c) la slide de demo lleva captura real de la app y no mockup ficticio, (d) ningún slide tiene "Lorem ipsum", "TBD" o placeholders, (e) la slide de competencia menciona al menos 3 jugadores reales con un punto diferencial por cada uno.

Agente: dimensión cubierta. El flujo se reanuda.

### Dimensión 6 — Decisiones congeladas

Operador:

> - formato: PDF + Notion público | razón: la inversora prefiere lectura asíncrona antes de la reunión
> - longitud: 12 slides exactas | razón: estándar Y Combinator que la inversora respeta
> - tono: directo, sin marketing speak | razón: perfil financiero, detecta humo
> - cifras: solo con fuente nombrada o métricas internas | razón: credibilidad ante perfil técnico
> - demo: captura real, no mockup | razón: la app ya está en beta, no hay excusa
> - precio en slide ask: no mostrar valuation pre-money | razón: se negocia en la reunión

Agente: dimensión cubierta.

---

## 3. Resumen interno antes de pasar a la fase A

El protocolo confirma silenciosamente que las 6 dimensiones están en condiciones de pasar a ejecución. Sin anuncios de "verde" ni numerar dimensiones al usuario:

```
Listo. Tengo lo que necesito. Antes de empezar a generar, te paso el bloque
que el agente va a respetar literalmente durante toda la sesión.
```

---

## 4. Bloque de decisiones congeladas final

```
DECISIONES CONGELADAS — NO REABRIR
- formato: PDF + Notion público | razón: la inversora prefiere lectura asíncrona
- longitud: 12 slides exactas | razón: estándar YC respetado por la inversora
- tono: directo, sin marketing speak | razón: perfil financiero detecta humo
- cifras: solo con fuente o métricas internas | razón: credibilidad ante perfil técnico
- demo: captura real, no mockup | razón: la app ya está en beta
- precio: no mostrar valuation pre-money en el deck | razón: se negocia en reunión
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

Este bloque se inyecta literalmente en el prompt de la fase **A**.

---

## 5. Cierre de la sesión

La fase **A** corre con el bloque inyectado y produce las 12 slides en `outputs/decks/2026-05-12-inversor-pre-seed/`. Una sola pasada. El agente bloqueó dos veces durante la generación con `[BLOQUEO]`: una al dudar si añadir un slide adicional de roadmap (no estaba en la estructura definida), otra al dudar si poner una valuation indicativa en la slide ask. En ambos casos el operador confirmó que no, en menos de 30 segundos.

Al cerrar la fase **S** (Síntesis local de la sesión), el protocolo H1 escribe el activo en disco:

**Path:** `outputs/diarios/2026-05-06-pitch-deck-inversor.md`

Contenido:

```markdown
# Pitch deck inversor pre-seed — 2026-05-06

## Objetivo
Pitch deck de 12 slides para reunión presencial 2026-05-12 11:00 con
inversora ángel SaaS B2B. Ticket objetivo 100k pre-seed.

## Inputs
- inputs/conversacion-2026-04-25.md
- inputs/metrics-abril.csv
- inputs/deck-pre-ronda-2025-12.pptx
- inputs/tesis-inversora.md

## Restricciones
- Tiempo sesión: 90 min máx, hard-stop 23:00.
- Audiencia: inversora ángel, perfil financiero-técnico, lectura asíncrona.
- Idioma: español.
- Formato: lectura en pantalla, no presencial.

## Formato
12 slides exactas (portada, problema, solución, demo, mercado, modelo,
tracción, equipo, competencia, uso de fondos, ask, contacto).
Texto corto <40 palabras/slide. Una idea por slide.

## Criterios de aceptación
- 12 slides maquetadas con contenido definitivo.
- Slides 5, 6, 7, 10 con cifra y fuente.
- Slide demo con captura real (no mockup).
- Cero "TBD", "Lorem ipsum", placeholders.
- Slide competencia con 3 jugadores reales y diferencial.

## Decisiones congeladas
DECISIONES CONGELADAS — NO REABRIR
- formato: PDF + Notion público | razón: lectura asíncrona pre-reunión
- longitud: 12 slides exactas | razón: estándar YC respetado por la inversora
- tono: directo, sin marketing speak | razón: perfil financiero detecta humo
- cifras: solo con fuente o métricas internas | razón: credibilidad técnica
- demo: captura real, no mockup | razón: la app ya está en beta
- precio: no mostrar valuation pre-money | razón: se negocia en reunión
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.

## Resultado
outputs/decks/2026-05-12-inversor-pre-seed/deck.pdf
outputs/decks/2026-05-12-inversor-pre-seed/notion-public-url.md

## Lecciones
- Dimensión 5 (criterios de aceptación) volvió a salir vaga la primera vez.
  El reflejo "cuando esté bien" sigue ahí. Forzar reformulación binaria
  desde el inicio en próximas sesiones.
- Bloqueos del agente durante A: 2 veces, ambas resueltas en <30 s.
  El bloque congelado evitó al menos dos rehechos completos.
- Reusar el bloque congelado como base para el siguiente deck B2B SaaS,
  cambiando solo el público y el formato.
```

---

## 6. Lectura del ejemplo

Tres cosas que conviene mirar al releer el caso:

1. **El flujo se detuvo una vez** (criterios de aceptación) y eso fue el mayor ahorro de la sesión: si el operador hubiera entrado a fase **A** con "cuando esté bien", el agente habría inventado un techo de calidad y los 45 minutos de Harvey habrían vuelto a aparecer.
2. **El bloque congelado bloqueó dos veces durante A**, en menos de 30 segundos cada una. Sin él, cada una de esas dudas habría sido una microdecisión emergente.
3. **El fichero `outputs/diarios/2026-05-06-pitch-deck-inversor.md` es el activo trazable.** No es un acta de la sesión: es el contrato I → A → S, listo para que el protocolo de Síntesis (H2) lo lea sin tener que reconstruir nada.
