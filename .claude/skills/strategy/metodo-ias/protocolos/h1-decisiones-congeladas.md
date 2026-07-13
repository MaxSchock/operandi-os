# H1 — Bloque de decisiones congeladas

> Patrón específico del bloque que se inyecta al prompt del agente al inicio de la fase **A**.
> Su función única: que el agente no reabra a mitad de ejecución decisiones que el operador ya cerró.

---

## Por qué existe este patrón

La fuente de quemazón identificada por Harvey en La Forja ("le agregaste otra información que no habías tomado en cuenta y ya te cambia totalmente el output") aparece casi siempre por el mismo mecanismo: el agente, ante una ambigüedad, **inventa una alternativa razonable**. Esa alternativa se aleja de la decisión que el operador tenía en mente, el output cambia, y los 45 minutos se queman.

El bloque de decisiones congeladas corta ese mecanismo en seco. Ante ambigüedad, el agente no inventa: marca `[BLOQUEO]` y para.

---

## Plantilla literal

```
DECISIONES CONGELADAS — NO REABRIR
- {clave}: {valor elegido} | razón: {1 línea}
- {clave}: {valor elegido} | razón: {1 línea}
- {clave}: {valor elegido} | razón: {1 línea}
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

### Reglas de redacción

1. **Una decisión por línea.** No combinar varias claves en una.
2. **Clave corta** (1–3 palabras). Evita frases largas en la clave; mete el detalle en el valor.
3. **Valor concreto.** "PDF + Notion", no "documento bonito".
4. **Razón en una línea.** No es defensa filosófica; es trazabilidad para futuras revisiones.
5. **Sin verbos blandos.** Prohibidos "preferiblemente", "idealmente", "si es posible", "si te sale", "mejor". O entra cerrado o no entra.
6. **Cláusula de bloqueo siempre al final**, literal. No la parafrasees.

---

## Cinco ejemplos genéricos

### Ejemplo 1 — Pitch deck para inversor pre-seed

```
DECISIONES CONGELADAS — NO REABRIR
- formato: PDF + Notion público | razón: lectura asíncrona antes de la reunión
- longitud: 12 slides exactas | razón: estándar YC respetado por el público objetivo
- tono: directo, sin marketing speak | razón: perfil financiero detecta humo
- cifras: solo con fuente nombrada o métricas internas | razón: credibilidad ante perfil técnico
- demo: captura real de la app, no mockup | razón: el producto ya está en beta
- valuation: no mostrar en el deck | razón: se negocia en la reunión
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

### Ejemplo 2 — Landing de captación de un producto digital propio

```
DECISIONES CONGELADAS — NO REABRIR
- framework: Next.js + Tailwind + shadcn/ui | razón: stack del operador
- deploy: Vercel | razón: estándar del operador
- copy: español neutro, sin anglicismos sustituibles | razón: audiencia hispanohablante mixta
- formulario: solo nombre y email | razón: bajar fricción inicial al máximo
- analítica: solo el panel del propio host | razón: no introducir tracking externo en esta sesión
- testimonios: usar solo los 3 ya validados | razón: no inventar prueba social
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

### Ejemplo 3 — Curso online de 8 horas (4 módulos × 2h)

```
DECISIONES CONGELADAS — NO REABRIR
- bloques: 4 módulos × 2 h | razón: estructura validada en cohorte anterior
- entregables por módulo: vídeo + manual PDF + ejercicio | razón: formato base
- evaluación: cuestionario por módulo + proyecto final | razón: requisito de certificación interna
- tono: didáctico para perfil no técnico | razón: alumnado mixto sin requisitos técnicos
- duración del vídeo por módulo: 25-35 min | razón: ventana de atención sostenible
- tareas opcionales avanzadas: identificar pero no producir esta sesión | razón: scope acotado
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

### Ejemplo 4 — Post LinkedIn de marca personal

```
DECISIONES CONGELADAS — NO REABRIR
- longitud: <600 caracteres antes del "ver más" | razón: máximo enganche en feed
- estructura: gancho 2 líneas + cuerpo + cierre con pregunta | razón: patrón que ha funcionado antes
- tono: primera persona, directo, sin emojis | razón: voz coherente con el resto del feed
- enlaces externos: ninguno en el cuerpo | razón: penalización del algoritmo
- cierre: pregunta abierta a la audiencia | razón: empuja comentarios y alcance
- hashtags: máximo 3, ya validados | razón: no introducir hashtags nuevos esta sesión
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

### Ejemplo 5 — Plantilla de email automatizado de bienvenida

```
DECISIONES CONGELADAS — NO REABRIR
- secuencia: 3 emails (día 0, día 2, día 5) | razón: validado en cohorte anterior
- longitud por email: <200 palabras | razón: lectura móvil
- objetivo email 1: agradecer y dar primer paso útil | razón: enganche día 0
- objetivo email 2: aportar caso de uso concreto | razón: dar valor antes de pedir
- objetivo email 3: invitar a una acción opcional (no venta dura) | razón: validado
- emoji en asunto: ninguno | razón: línea editorial
- firma: nombre + un enlace, no más | razón: minimizar ruido visual
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

---

## Cómo se inyecta en la sesión

El bloque se copia tal cual al inicio del prompt de la fase **A**, antes del objetivo y antes de los inputs. Patrón:

```
Vas a producir el activo descrito abajo.
Antes del trabajo, lee el siguiente bloque y respétalo literalmente.

[BLOQUE DE DECISIONES CONGELADAS]

Objetivo: ...
Inputs: ...
Restricciones: ...
Formato: ...
Criterios de aceptación: ...

Empieza.
```

El operador no reabre el bloque a mitad de ejecución. Si surge una decisión nueva legítima (ejemplo: a mitad de la generación llega un dato que cambia el alcance), el flujo correcto es:

1. Parar la fase **A**.
2. Volver a **I**.
3. Añadir o modificar la decisión en el bloque.
4. Reinyectar el bloque actualizado.
5. Reanudar **A**.

Eso mantiene la trazabilidad y evita que la decisión se "cuele" como microdecisión silenciosa.

---

## Qué NO entra en el bloque

- Decisiones que aún no están tomadas. Si dudas, no la pongas.
- Decisiones que dependen del resultado intermedio. Esas son criterios de aceptación (dimensión 5 del checklist), no decisiones congeladas.
- Información de contexto. El contexto va en "Inputs" del prompt, no en el bloque.
- Preferencias estéticas vagas. Si no se puede formular como `clave: valor concreto`, no es una decisión.
