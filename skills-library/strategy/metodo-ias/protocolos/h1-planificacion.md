# H1 — Planificación previa exhaustiva

> Protocolo diario de la fase **I (Intención)** del método I.A.S.
> Validación de la Hipótesis 1 del taller La Forja (2026-05-06).

---

## 1. Qué es

H1 es el protocolo que convierte la fase **I** en un activo cerrado antes de tocar la **A**. No es un párrafo de intención: es un **checklist verde/rojo** sobre seis dimensiones, más un **bloque de decisiones congeladas** que el agente no puede reabrir a mitad de ejecución.

### Enunciado de la hipótesis

La microdecisión durante la ejecución es la principal fuente de quemazón al trabajar con IA agéntica. Si la fase **I** entrega un checklist verde/rojo completo más decisiones congeladas antes de pasar a **A**, las microdecisiones bajan a casi cero, el agente termina en una pasada y el operador no se quema.

### Citas de origen

**Ricardo (taller La Forja, 2026-05-06):**
> "Las decisiones tienen que ser más de planificación o de proceso, como hace Alfonso. Si el proceso está tan refinado, no hay microdecisiones. Cuando hay microdecisiones, nos quemamos."

**Harvey (mismo taller):**
> "El output que te da la IA… de repente le agregaste otra información que no habías tomado en cuenta en la planificación y ya te cambia totalmente el output. Llevamos 45 minutos, te gastaste los tokens, y me estás cambiando el resultado."

H1 ataca exactamente esa cadena: planificación incompleta → input añadido a mitad → output rehecho → tokens y energía quemados.

---

## 2. Cuándo activarse

H1 se dispara en cualquiera de estos tres momentos:

1. **Arranque de sesión nueva con IA.** Antes del primer prompt sustancial. No vale empezar a chatear y "ya iremos viendo".
2. **Arranque de tarea sustancial dentro de una sesión activa.** Cualquier entregable que justifique más de 10–15 minutos de agente trabajando: documento, informe, código no trivial, pieza de marketing, propuesta.
3. **Señal de microdecisión emergente.** El operador detecta que la IA empieza a preguntar alternativas ("¿prefieres A o B?", "¿qué tono usamos?", "¿cuánto debe medir?") o que el operador mismo está dudando sobre detalles que deberían estar fijados. Eso es bandera roja: parar **A**, volver a **I**, completar H1.

Si el operador no se reconoce en ninguno de los tres triggers, la sesión es de exploración libre y H1 no aplica.

---

## 3. Las 6 dimensiones del checklist verde/rojo

Cada dimensión se pinta **verde** cuando la respuesta es concreta, accionable y verificable por un tercero. Se pinta **roja** cuando es vaga, condicional o ausente.

### 3.1. Objetivo concreto del activo a producir

**Pregunta:** ¿qué activo concreto sale de esta sesión y para qué se usa?

- Verde: "Pitch deck de 12 slides para reunión con inversora ángel el martes 12 a las 11:00. Sirve para abrir conversación de ronda pre-seed."
- Rojo: "Algo sobre la auditoría del cliente." / "Ver qué sale."

### 3.2. Inputs disponibles

**Pregunta:** ¿qué materiales reales tengo y dónde están?

- Verde: "Conversación inicial en `inputs/conversacion-2026-04-25.md`, métricas actuales en `inputs/metrics-abril.csv`, deck antiguo en `inputs/deck-pre-ronda-2025-12.pptx`, notas sobre la tesis del receptor en `inputs/tesis-receptor.md`."
- Rojo: "Tengo notas por ahí." / "La transcripción la subo si hace falta."

### 3.3. Restricciones (tiempo / formato / audiencia)

**Pregunta:** ¿qué condiciones de borde no son negociables?

- Verde: "Tiempo: 90 minutos máximo de sesión. Formato: Word + HTML twin. Audiencia: Director de Operaciones, perfil técnico-industrial, no habla AI. Idioma: español neutro, sin anglicismos."
- Rojo: "Cuanto antes mejor." / "Que se lea bien."

### 3.4. Formato del output esperado

**Pregunta:** ¿qué estructura concreta tiene el entregable?

- Verde: "Documento con 6 secciones fijas: contexto, hallazgos AS-IS, fugas detectadas, quick wins (3), roadmap 3-6-12, próximos pasos. Cada sección 1–2 páginas. Tablas para fugas y roadmap."
- Rojo: "Un informe profesional." / "Que tenga buena pinta."

### 3.5. Criterios de aceptación

**Pregunta:** ¿cómo sé que el entregable está terminado y bien?

- Verde: "Cierra cuando: (a) las 6 secciones están rellenas, (b) cada quick win lleva impacto cuantificado en horas/euros, (c) el roadmap tiene fechas concretas, (d) ningún hallazgo va sin cita o referencia interna del cliente."
- Rojo: "Cuando esté bien." / "Cuando me convenza."

### 3.6. Decisiones congeladas

**Pregunta:** ¿qué decisiones ya están tomadas y el agente no debe reabrir?

- Verde: "Formato: PDF + Notion público (no presencial). Tono: directo, sin marketing speak. Plantilla propia estándar. No incluir valuation. No proponer todavía términos concretos de la operación."
- Rojo: "Ya lo iremos decidiendo." / "Ahí dale lo que veas mejor."

Las 6 dimensiones se cubren en este orden. No saltar una para volver luego: si una sale roja, se cierra antes de pasar a la siguiente.

---

## 4. Gate verde/rojo

Regla dura del protocolo:

> **Si una sola de las 6 dimensiones está roja, no se pasa a la fase A.**

No hay ponderaciones, no hay "verde con asteriscos", no hay "casi verde". O las 6 están verdes o se vuelve a trabajar en **I**.

### Cómo se pinta verde cada dimensión

Cuatro caminos legítimos:

1. **Responder con un dato concreto** que cumpla el patrón "verde" del apartado 3.
2. **Bajar el alcance** hasta que la dimensión sea respondible. Si el objetivo es ambiguo porque la tarea es demasiado grande, se parte la tarea.
3. **Buscar el input que falta** antes de seguir. Si el input está roto y no se puede arreglar ahora, la sesión se aborta y se reagenda.
4. **Congelar la decisión** en el bloque del apartado 5 si la dimensión depende de una decisión todavía abierta.

Caminos no legítimos (anti-gate):

- "Lo verá la IA cuando llegue." Falso: la IA inventará una alternativa, gastará tokens, y obligará a rehacer.
- "Lo voy refinando sobre la marcha." Eso es exactamente lo que H1 viene a evitar.
- "Es que es muy creativo, no se puede planificar." Si es divergencia pura, H1 no aplica y la sesión va por otro carril (modo exploratorio, no método I.A.S.).

---

## 5. Bloque de decisiones congeladas

### Qué es

El bloque de decisiones congeladas es un fragmento de texto que se inyecta literalmente en el prompt del agente al iniciar la fase **A**. Su función única: cortar las microdecisiones a mitad de ejecución.

Está aparte del checklist (dimensión 3.6) porque cumple un papel distinto. El checklist comprueba que la decisión existe; el bloque la entrega al agente con un formato que **bloquea la improvisación**.

### Cómo se redacta

Cuatro reglas:

1. **Una decisión por línea**, en formato `clave: valor elegido | razón: una línea`.
2. **Razón corta y operativa**. No es justificación filosófica, es trazabilidad.
3. **Clausura explícita al final**: si el agente encuentra un caso fuera de las decisiones, debe **parar y marcar `[BLOQUEO]`**, no improvisar.
4. **Sin verbos blandos**. "Preferiblemente", "idealmente", "si es posible" están prohibidos. O la decisión está tomada o no entra al bloque.

### Plantilla

```
DECISIONES CONGELADAS — NO REABRIR
- {clave}: {valor elegido} | razón: {1 línea}
- ...
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.
```

Plantilla detallada con ejemplos en `h1-decisiones-congeladas.md`.

### Ejemplo de instrucción al agente

Al inicio del prompt de la fase **A**:

```
Vas a producir el activo descrito abajo.
Antes del trabajo, lee el siguiente bloque y respétalo literalmente.

DECISIONES CONGELADAS — NO REABRIR
- formato: PDF + Notion público | razón: lectura asíncrona pre-reunión
- tono: directo, sin marketing speak | razón: perfil financiero detecta humo
- valuation: no incluir | razón: se negocia en la reunión
- longitud: 12 slides exactas | razón: estándar respetado por el receptor
Si encuentras un caso fuera de estas decisiones, marca [BLOQUEO] y para. No improvises alternativas.

Objetivo: ...
```

---

## 6. Salida del protocolo

Cuando el gate pasa a verde, H1 emite un activo único en disco:

**Path:** `outputs/diarios/YYYY-MM-DD-{slug}.md`

Donde `{slug}` es el identificador corto del activo (ej. `pitch-deck-inversor`, `landing-producto-propio`). Un fichero por sesión H1.

### Estructura fija del fichero

```markdown
# {Título del activo} — {YYYY-MM-DD}

## Objetivo
{Respuesta dimensión 3.1}

## Inputs
{Respuesta dimensión 3.2}

## Restricciones
{Respuesta dimensión 3.3}

## Formato
{Respuesta dimensión 3.4}

## Criterios de aceptación
{Respuesta dimensión 3.5}

## Decisiones congeladas
{Bloque 5 al pie de la letra}

## Resultado
{Path/identificador del activo final producido en fase A}

## Lecciones
{1–3 líneas: qué obligó a re-trabajar I, qué dimensión fue la difícil, qué se reusa}
```

Las primeras 6 secciones se rellenan al cerrar **I**. Las dos últimas se completan al cerrar **S**. Esto enlaza H1 con la fase de Síntesis sin acoplar protocolos.

---

## 7. Anti-patrones que H1 detecta y bloquea

Cinco patrones que tiran la sesión y que el protocolo está obligado a marcar:

1. **Alternativas pre-elegidas sin criterio.** "Vamos a usar X." → ¿criterio? Si no hay, la dimensión 3.6 sale roja.
2. **"Ya lo veremos" / "lo voy viendo".** Marcador léxico directo de microdecisión emergente. Cualquier dimensión que termine así está roja por definición.
3. **Inputs ambiguos.** "Tengo notas por ahí", "creo que está en Drive". Si el operador no puede dar el path o el archivo en menos de 30 segundos, el input no existe a efectos del agente.
4. **Criterio de aceptación blando.** "Cuando me guste", "cuando esté bien", "que quede profesional". Bloquea la dimensión 3.5: hay que reformular en condiciones binarias verificables.
5. **Decisiones disfrazadas de preferencias.** "Mejor en Word, aunque si te sale en PDF también vale". Eso no es congelar: es delegar la decisión al agente y reabrir el debate más tarde. Forzar elección binaria antes de seguir.

Cuando H1 detecta cualquiera de estos cinco patrones, devuelve el control al operador y nombra el patrón. No reescribe la dimensión por su cuenta: el operador decide.
