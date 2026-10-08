# H2 — Plantilla rellenable de los 5 bloques

> Plantilla manual para ejecutar el recap semanal sin la skill automática.
> Copiar este archivo como `outputs/semanales/YYYY-Www.md`, sustituir `YYYY-Www` por la semana ISO actual y rellenar.

---

## Cabecera

- **Semana ISO:** YYYY-Www
- **Ventana cubierta:** YYYY-MM-DD → YYYY-MM-DD (7 días móviles hacia atrás desde hoy)
- **Diarios leídos:** N
- **Recap anterior:** ruta del archivo o "primero"

---

## Bloque 1 — Inventario

**Pregunta clave: ¿qué se ha producido esta semana?**

Lista plana, una línea por diario. Sin juicio, sin ranking. Si hay 10 diarios hay 10 líneas.

- [Titular] — [1 línea descriptiva] — `outputs/diarios/YYYY-MM-DD-{slug}.md`
- ...

---

## Bloque 2 — Pareto 80/20

**Pregunta clave: ¿cuál es el 20% que aporta el 80% del valor real?**

### El 20% que importa

Entre el 15% y el 30% de los items del Bloque 1. Cada uno con razón explícita.

- [Item] — por qué importa (cliente, ingreso, decisión bloqueante, dependencia crítica)
- ...

### Descarte sin culpa

El resto. **Sin culpa.** Exploración necesaria, sub-outputs del 20%, ya superados. Nombrarlos no es autocrítica.

- [Item] — por qué se archiva
- ...

---

## Bloque 3 — Boundary erosion

**Pregunta clave: ¿paró el operador? ¿pararon los agentes? ¿se respetaron las decisiones congeladas?**

Descriptivo, no terapéutico. Si hubo erosión, se nombra y ya.

- **Días sin sesión cerrada:** [lista de fechas] o "ninguno"
- **Sesiones tarde-noche (>22h) o madrugada (<7h):** [lista] o "ninguna"
- **Decisiones congeladas re-abiertas a mitad de A:** [item afectado] o "ninguna"
- **Hard-stop horario respetado:** sí / no / parcial — 1 línea de contexto

---

## Bloque 4 — Techo de output para la semana siguiente

**Pregunta clave: dado lo producido y lo que importó, ¿cuál es el techo que declaro?**

Anti-ratchet: el operador lo decide antes de que cliente / dirección / inercia lo suban.

- **Techo declarado:** N entregables / N sesiones I.A.S. / N horas con agente
- **Justificación (1-2 líneas):** por qué este número
- **Comparación con techo anterior:** igual / arriba / abajo + razón si cambia
- **Lo que voy a NO hacer (lista corta):**
  - ...
  - ...

---

## Bloque 5 — Delegables

**Pregunta clave: ¿qué pasa al equipo humano la próxima semana, y qué del 20% es intransferible?**

### Delegar a equipo humano

Mínimo 1 por semana, salvo justificación explícita.

- [Item] → [rol o nombre] → [criterio de éxito en 1 línea]
- ...

### Intransferible esta semana

Items del Pareto que solo el operador puede ejecutar. Razón explícita.

- [Item] — por qué solo yo puedo hacerlo
- ...

---

## Compromisos para la semana siguiente

Lista corta de checkboxes accionables. Derivar de Bloques 4 y 5. Si esto queda vacío o vago, el recap fue performativo.

- [ ] Compromiso 1 (concreto, observable, con fecha implícita en la semana)
- [ ] Compromiso 2
- [ ] Compromiso 3

---

## Alertas

Solo se rellena si aplica. Si no hay alertas, escribir "ninguna".

Patrones a vigilar:
- 3 semanas con techo subiendo sin razón nombrada
- 3 semanas sin delegables sin justificación
- 2 semanas con boundary erosion sin corregir
- 2 semanas con muestra baja sin causa declarada

---

## Notas libres (opcional)

Espacio para observaciones que no encajan en los 5 bloques: cambios de prioridad inesperados, aprendizajes meta, cosas que probar la próxima semana. No es obligatorio.
