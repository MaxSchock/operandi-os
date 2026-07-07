# H2 — Ejemplo end-to-end

> Caso ficticio realista. Una semana de un operador freelance/consultor genérico que usa el método I.A.S.
> Semana 2026-W19, ejecutada el viernes 8 de mayo de 2026 por la tarde.

---

## Punto de partida

A lo largo de la semana, el operador ejecutó cinco sesiones I.A.S. con H1, dejando estos archivos en `outputs/diarios/`:

| Fecha | Slug | Resumen |
|-------|------|---------|
| 2026-05-04 | `propuesta-cliente-saas-onboarding` | Propuesta de servicios de consultoría: 3 meses para un cliente SaaS B2B medio. |
| 2026-05-05 | `guion-video-canal-propio-skill-trigger` | Guion + thumbnail + descripción para vídeo de canal propio: "Por qué tu skill nunca se activa". |
| 2026-05-05 | `batch-posts-linkedin-semanal` | 7 posts LinkedIn programados, hilo conductor "operador con flota de agentes". |
| 2026-05-06 | `fix-bug-side-project-token-refresh` | Refresh token expirado en una integración del side project. Causa raíz + parche + post-mortem. |
| 2026-05-07 | `sesion-mentoria-alumno-3-plan-digital` | Sesión de tutoría con un alumno: plan de transformación digital pre-entrega. |

Total: 5 diarios. Muestra suficiente.

---

## Invocación

```
/ias-recap
```

La skill lee los 5 diarios, comprueba que `outputs/semanales/2026-W18.md` existe (recap anterior, primero de la skill), y arranca los 5 bloques. Antes de escribir, presenta el resultado en pantalla.

---

## Archivo resultante: `outputs/semanales/2026-W19.md`

```markdown
# Recap semanal 2026-W19

- Ventana cubierta: 2026-05-01 → 2026-05-08
- Diarios leídos: 5
- Recap anterior: outputs/semanales/2026-W18.md

## Bloque 1 — Inventario

- Propuesta cliente SaaS B2B — 3 meses de consultoría, 12 páginas + HTML twin — `outputs/diarios/2026-05-04-propuesta-cliente-saas-onboarding.md`
- Vídeo canal propio "Por qué tu skill nunca se activa" — guion 18 min, thumbnail, descripción y tags — `outputs/diarios/2026-05-05-guion-video-canal-propio-skill-trigger.md`
- Batch 7 posts LinkedIn — hilo "operador con flota", calendario lunes-domingo — `outputs/diarios/2026-05-05-batch-posts-linkedin-semanal.md`
- Fix side project: refresh token caducado — diagnóstico, parche, post-mortem y nota para retomar registro de app OAuth — `outputs/diarios/2026-05-06-fix-bug-side-project-token-refresh.md`
- Sesión mentoría alumno 3 — plan digital pre-entrega con 7 secciones, base para el documento final — `outputs/diarios/2026-05-07-sesion-mentoria-alumno-3-plan-digital.md`

## Bloque 2 — Pareto 80/20

### El 20% que importa

- Propuesta cliente SaaS B2B — único output con probabilidad real de cerrar contrato esta quincena, decisión bloqueante para el trimestre.
- Fix side project — sin él, los registros del fin de semana no entran al sistema. Foundation crítica.

### Descarte sin culpa

- Vídeo canal propio — output válido y necesario para la cadencia, pero el valor se acumula a medio plazo, no esta semana.
- Batch LinkedIn — mismo razonamiento. Ya está cargado, no hay que volver a tocarlo.
- Sesión mentoría alumno 3 — entregable real para el alumno la semana que viene, esta semana fue producción intermedia. Va al 20% la próxima si toca cerrarlo.

## Bloque 3 — Boundary erosion

- Días sin sesión cerrada: ninguno.
- Sesiones tarde-noche (>22h) o madrugada (<7h): martes 5/05 entre 23:30 y 01:15 sobre el batch LinkedIn (varios agentes corriendo en paralelo).
- Decisiones congeladas re-abiertas a mitad de A: en la propuesta del cliente SaaS se reabrió el alcance dos veces durante la generación (de 3 a 5 módulos, luego a 4). H1 lo señaló como lección.
- Hard-stop horario respetado: parcial — se respetó lunes/miércoles/jueves/viernes; martes se rompió.

## Bloque 4 — Techo declarado semana siguiente

- Techo: 4 sesiones I.A.S. (esta semana fueron 5).
- Justificación: la sesión de mentoría se cierra el lunes y bloquea agenda. Mejor terminar lo que ya está abierto antes de empezar nada nuevo. Bajar el techo es deliberado, no por agotamiento.
- Comparación con techo anterior: 2026-W18 declaró 5; ahora bajo a 4 (-1). Razón nombrada arriba.
- Lo que voy a NO hacer la semana que viene:
  - Ningún output nuevo de canal propio (vídeo + posts ya cubren la semana).
  - No reabrir el alcance de la propuesta una vez enviada.
  - No tocar el side project salvo bug crítico nuevo.

## Bloque 5 — Delegables

### Delegar a equipo humano

- Maquetación final HTML twin de la propuesta → asistente de operaciones → criterio de éxito: HTML idéntico al Word, paleta correcta, listo para enviar lunes 12h.
- Programación del batch LinkedIn semana siguiente en el programador de turno → asistente de contenido → criterio: 7 posts subidos con horarios validados, sin tocar copy.

### Intransferible esta semana

- Conversación de cierre con el cliente antes de enviar la propuesta — el cierre comercial no se delega.
- Sesión 4 con el alumno y entrega del documento final — relación tutor-alumno directa, no se traspasa.

## Compromisos para la semana siguiente

- [ ] Lunes 11/05 09:00: cierre comercial con el cliente y envío de propuesta antes de las 14:00.
- [ ] Lunes 11/05: maquetación HTML twin delegada confirmada antes del envío.
- [ ] Miércoles 13/05: documento final del alumno cerrado y enviado.
- [ ] Viernes 15/05 17:00: siguiente recap con techo de 4 sesiones cumplido o explicado.

## Alertas

- Boundary erosion martes noche: si se repite la próxima semana, bajar el techo otra vez (a 3 sesiones) y declarar hard-stop a las 21:30.
- Decisiones congeladas re-abiertas en propuestas: revisar el checklist de I de H1 para propuestas comerciales — el alcance debería congelarse antes de abrir A.

## Notas libres

La sensación al ver los 5 diarios juntos es que la propuesta del cliente se llevó más recursos cognitivos de los que parecía mientras se hacía. La S macro lo deja claro y justifica bajar el techo.
```

---

## Qué pasó después

El operador confirma el recap, la skill escribe el archivo en `outputs/semanales/2026-W19.md`, y muestra los 4 compromisos resumidos en chat:

```
Recap guardado en outputs/semanales/2026-W19.md.

Compromisos esta semana:
1. Cierre y envío propuesta — lunes 11/05.
2. HTML twin propuesta delegado — lunes 11/05.
3. Documento final alumno — miércoles 13/05.
4. Próximo recap — viernes 15/05.

Alerta repetida desde W18: boundary erosion martes noche. Vigila.
```

El lunes siguiente, antes de abrir la primera I de la semana, el operador abre `outputs/semanales/2026-W19.md` para repasar los compromisos. La S macro ha cerrado el ciclo: lo que iba a quedar como ruido acumulado ya tiene forma, prioridad y techo.
