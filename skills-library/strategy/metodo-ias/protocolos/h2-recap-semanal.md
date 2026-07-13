# H2 — Recap Semanal (S macro)

> Protocolo de la fase **S (Síntesis) semanal** del método I.A.S.
> Cierra el ciclo Intención → Acción → Síntesis a escala de semana.
> Lee de `outputs/diarios/` (lo que produjo H1) y escribe en `outputs/semanales/`.

---

## 1. Qué es y enunciado de la hipótesis

Sin una parada semanal estructurada, el operador con IA agéntica acumula **deuda invisible**: outputs sin priorizar, decisiones sin cerrar, expectativa subiendo unilateralmente. Una **S macro semanal** convierte el método I.A.S. en un ciclo cerrado en lugar de un embudo abierto.

**Citas de origen (taller La Forja, 2026-05-06):**

Uno de los participantes, mostrando outputs acumulados de meses anteriores:
> "Sí que creo que hacemos mucha más salida de documentación de la que era consciente."

Carlos:
> "Mi mayor problema es que tengo demasiadas cosas desorganizadas. La skill nos ayude a organizar y saber dónde tenemos las cosas, ir con una flecha."

Dani (origen del bloque de delegables):
> "Tú trabajas con un equipo, qué cosas deberías delegar sí o sí."

**Tres patrones que H2 contrarresta:**

- **Ratchet effect:** cada win sube el listón sin parada negociada. Si no se declara explícitamente un techo para la semana siguiente, el techo lo declara la inercia o el cliente.
- **Boundary erosion:** los agentes no paran. Si el operador vincula su valor al output del agente, tampoco para. El recap audita si hubo cierres reales.
- **Mountain of outputs:** se generan 10×, se revisan 2×, se usa 1×. El recap obliga a separar el 1× útil del resto sin culpa.

---

## 2. Cuándo activarse

Trigger natural, **no automático**. El operador lo dispara cuando:

- **Viernes por la tarde**, antes de cerrar la semana laboral (recomendado por defecto).
- **Lunes por la mañana**, antes de abrir la primera I de la semana nueva.
- **Fin de iteración / sprint**, aunque caiga a mitad de semana.
- **Fin de bloque temático** (ej. acabas la fase de propuestas y entras en ejecución).

Reglas anti-deriva:

- No se ejecuta más de una vez por semana ISO.
- No se ejecuta antes de 5 días desde el recap anterior (excepto fin de sprint declarado).
- Si llevas dos semanas sin recap pero hay diarios acumulados, se hace **un solo recap consolidado** marcado `multi-semana`, no dos recaps separados rellenando huecos.

---

## 3. Input del protocolo

**Lectura obligatoria:** `outputs/diarios/*.md` de los últimos 7 días.

- Se usa **ventana móvil de 7 días naturales contados hacia atrás desde el momento del recap**, no semana ISO calendárica. Razón: el operador no siempre cierra el viernes; un sábado que produjo dos diarios cuenta para el recap del lunes siguiente, no se pierde.
- La etiqueta del archivo de salida sí usa semana ISO (`YYYY-Www`) para que dos recaps no colisionen, pero el contenido no se limita a esa semana ISO.
- Si el último recap se hizo hace más de 7 días, la ventana se extiende hasta cubrir el gap (caso `multi-semana`).

**Lectura opcional:**

- El archivo de la semana anterior (`outputs/semanales/YYYY-Www-1.md`) si existe, para comparar techos declarados y cumplimiento.

**No lee:**

- `SKILL.md`, `README.md`, ni archivos de configuración.
- Diarios fuera de la ventana móvil declarada.

---

## 4. Los 5 bloques fijos del recap

Cada bloque tiene **una pregunta clave**, **qué leer** de los diarios y **formato fijo de respuesta**. El recap se ejecuta en este orden, sin saltarse bloques.

### Bloque 1 — Inventario

- **Pregunta clave:** ¿qué se ha producido esta semana?
- **Qué leer:** secciones `resultado` y `objetivo` de cada diario.
- **Formato:** lista plana, una entrada por diario.
  ```
  - [titular en una línea] — [1 línea descriptiva] — `outputs/diarios/YYYY-MM-DD-{slug}.md`
  ```
- **Regla:** sin valoración, sin ranking, sin filtrado. Es inventario crudo. Si hay 12 diarios, hay 12 líneas.
- **Anti-patrón a evitar:** empezar a juzgar aquí. El juicio es del Bloque 2.

### Bloque 2 — Pareto 80/20

- **Pregunta clave:** ¿cuál es el 20% de lo producido que aporta el 80% del valor real esta semana?
- **Qué leer:** del Bloque 1 + sección `criterios de aceptación` y `decisiones congeladas` de cada diario.
- **Formato:**
  ```
  ### El 20% que importa
  - [item del inventario] — por qué importa (1 línea: cliente, ingreso, decisión bloqueante, etc.)

  ### Descarte sin culpa
  - [item del inventario] — por qué se archiva (exploración válida, sub-output del 20%, ya superado, etc.)
  ```
- **Regla dura:** **el descarte va sin culpa.** No es "esto fue malo". Es "esto fue exploración necesaria pero no entra en el highlight reel". Sin esta regla, el bloque se convierte en autocrítica y deja de servir.
- **Cuota orientativa:** entre 15% y 30% de los items en "el 20% que importa". Si todo importa, no se ha hecho el ejercicio.

### Bloque 3 — Detección de boundary erosion

- **Pregunta clave:** ¿paró el operador? ¿pararon los agentes? ¿se respetaron las decisiones congeladas?
- **Qué leer:** timestamps de creación y modificación de los diarios, sección `decisiones congeladas` y `lecciones`.
- **Formato:**
  ```
  - Días sin sesión cerrada: [lista de fechas o "ninguno"]
  - Sesiones tarde-noche (>22h) o madrugada (<7h): [lista o "ninguna"]
  - Decisiones congeladas re-abiertas a mitad de A: [item del diario afectado o "ninguna"]
  - Hard-stop horario respetado: [sí/no/parcial — explicar 1 línea]
  ```
- **Regla:** este bloque es **descriptivo, no terapéutico**. Si hubo erosión, se nombra. La acción correctiva va en el Bloque 4 y en compromisos. Aquí no se justifica.
- **Conexión con la idea anexa #5** (hard-stop horario): este bloque es donde se mide.

### Bloque 4 — Recalibración del techo de output

- **Pregunta clave:** dado lo que se produjo y lo que importó, ¿cuál es el techo declarado para la semana siguiente?
- **Qué leer:** Bloques 1, 2 y 3 ya rellenos + el archivo de la semana anterior si existe.
- **Formato:**
  ```
  - Techo declarado semana siguiente: [N entregables / N sesiones I.A.S. / N horas con agente]
  - Justificación (1-2 líneas): [por qué este número, no más, no menos]
  - Comparación con techo anterior: [igual / arriba / abajo + razón]
  - Lo que se va a NO hacer (declaración explícita): [lista corta]
  ```
- **Regla anti-ratchet:** el techo lo declara el operador antes de que dirección, cliente o inercia lo suban unilateralmente. Si el techo sube, debe haber **una razón nombrada** (capacidad real ganada, no presión externa aceptada por defecto).
- **Anti-patrón a evitar:** el techo sube cada semana sin justificación. Si pasa dos semanas seguidas, el recap lo señala como alerta.

### Bloque 5 — Lista de delegables

- **Pregunta clave:** de lo hecho esta semana, ¿qué debería pasar al equipo humano la próxima semana, y qué del 20% del Pareto sigue siendo intransferible?
- **Qué leer:** Bloque 1 + Bloque 2 + sección `restricciones` y `lecciones` de cada diario.
- **Formato:**
  ```
  ### Delegar a equipo humano
  - [item] → [a quién o a qué rol] → [criterio de éxito en 1 línea]

  ### Intransferible esta semana
  - [item del 20%] — por qué solo el operador puede hacerlo (1 línea)
  ```
- **Origen:** aporte explícito de Dani en La Forja. Sin este bloque, el operador tiende a quedarse con todo y a quemar al equipo o a sí mismo.
- **Regla:** mínimo 1 delegable nombrado por semana, salvo justificación explícita ("equipo de baja", "semana sin nadie disponible"). Si tres semanas seguidas sin delegables, el recap lo señala como alerta.

---

## 5. Salida — plantilla del archivo `outputs/semanales/YYYY-Www.md`

```markdown
# Recap semanal {YYYY-Www}

- Ventana cubierta: {YYYY-MM-DD} → {YYYY-MM-DD}
- Diarios leídos: {N}
- Recap anterior: {ruta o "primero"}

## Bloque 1 — Inventario

{lista plana de items con paths a diarios}

## Bloque 2 — Pareto 80/20

### El 20% que importa
{items + razón}

### Descarte sin culpa
{items + razón}

## Bloque 3 — Boundary erosion

{4 líneas descriptivas según formato del bloque}

## Bloque 4 — Techo declarado semana siguiente

- Techo: {N}
- Justificación: {1-2 líneas}
- Comparado con semana anterior: {igual/arriba/abajo + razón}
- Lo que NO se va a hacer: {lista}

## Bloque 5 — Delegables

### Delegar
{items con rol y criterio}

### Intransferible
{items con razón}

## Compromisos para la semana siguiente

- [ ] {compromiso 1, derivado del Bloque 4}
- [ ] {compromiso 2, derivado del Bloque 5}
- [ ] {compromiso 3, opcional, derivado del Bloque 3}

## Alertas

{si hay 3 semanas con techo subiendo, 3 sin delegables, o 2 con boundary erosion no corregida, listar aquí. Si no hay alertas, escribir "ninguna"}
```

---

## 6. Anti-patrones que H2 detecta y nombra

El recap **falla en silencio** si cae en cualquiera de estos. El operador debe poder ver el patrón directamente en el archivo:

1. **"Todo importa, nada se descarta"** — Bloque 2 con el 90% en el lado del 20%. El recap no ha cumplido su función.
2. **Techo que sube unilateralmente** — Bloque 4 con techo más alto que la semana anterior **sin razón nombrada**. Es ratchet effect aceptado por defecto.
3. **"No hubo tiempo de delegar"** — Bloque 5 vacío sin justificación. Tres semanas seguidas → alerta automática.
4. **Recap performativo** — archivo largo, lleno de adjetivos, sin compromisos accionables al final. Se reconoce porque la sección "Compromisos" tiene 0 checkboxes o todos vagos ("mejorar la planificación").
5. **Boundary erosion normalizada** — Bloque 3 reportando trabajo nocturno o agentes sin parar dos semanas seguidas sin que el Bloque 4 baje el techo. Patrón clásico previo al burnout.
6. **Recap sin cierre** — el archivo se queda escrito pero los compromisos no se revisan en el siguiente recap. La skill no obliga a revisarlos pero el archivo siguiente debería abrirse leyendo el anterior.

---

## 7. Regla de muestra baja

Si en la ventana móvil de 7 días hay **menos de 3 diarios** en `outputs/diarios/`:

1. **Avisar al inicio del recap:**
   > "Muestra baja: solo {N} diario(s) en los últimos 7 días. Recap en versión corta. ¿Quieres continuar?"

2. **Versión corta del recap (si el operador continúa):**
   - Bloque 1: inventario completo (es corto por definición).
   - Bloque 2: Pareto se sustituye por **"¿Lo que se hizo esta semana mereció una sesión I.A.S. dedicada o pudo haberse resuelto sin método?"**
   - Bloque 3: se mantiene tal cual.
   - Bloque 4: techo se declara como **N para la semana siguiente, partiendo de la base de retomar el método**, no como recalibración.
   - Bloque 5: se omite si N ≤ 1; se mantiene si N = 2.

3. **Diagnóstico explícito al final del archivo:**
   El recap incluye una sección "Por qué bajó el ritmo" con sugerencias para que el operador marque la real:
   - [ ] Vacaciones / festivo / viaje declarado
   - [ ] Sprint terminado, semana de respiro intencionado
   - [ ] Bloqueo en un proyecto concreto (cuál: ___)
   - [ ] Abandono del método (he vuelto a operar sin I.A.S.)
   - [ ] Otro: ___

4. **Si dos semanas seguidas con muestra baja sin causa declarada → alerta dura:** "Posible abandono del método. Revisar si I.A.S. sigue aportando o si el flujo de trabajo cambió."

---

## 8. Acoplamiento con H1

- H1 produce un activo en `outputs/diarios/YYYY-MM-DD-{slug}.md` con secciones fijas: objetivo, inputs, restricciones, formato, criterios, decisiones congeladas, resultado, lecciones.
- H2 **lee** esas secciones, no las modifica.
- Si una sección esperada no existe en un diario (porque H1 evolucionó), H2 lo nota y sigue con lo disponible, sin romperse. Marca el diario como `parcial` en el inventario.
- H2 no asume que todos los diarios siguen exactamente el mismo esquema, pero asume que **al menos titular + path + 1 línea de qué se hizo** son recuperables.
