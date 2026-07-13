# H2 — Trigger y persistencia

> Cómo se dispara el recap semanal y cómo se guarda. Sin cron ni programación externa: el acto de invocar es parte del valor.

---

## Disparo manual

El recap es **siempre explícito**. Lo lanza el operador desde Claude Code:

```
/ias-recap
```

No hay versión automática. Razón: si el recap se dispara solo, deja de funcionar como **acto de cierre consciente**. El propio acto de invocarlo es parte del valor — fuerza al operador a parar y abrir el archivo.

Variantes admitidas del comando:
- `/ias-recap` — recap normal de la ventana móvil de 7 días.
- `/ias-recap multi-semana` — cuando el último recap se hizo hace más de 7 días, consolida todo en uno solo.
- `/ias-recap rapido` — versión corta forzada (útil cuando el operador sabe de antemano que la muestra es baja, p.ej. tras vacaciones).

---

## Cadencia recomendada

Dos slots naturales, el operador elige el que encaja con su ritmo:

- **Viernes por la tarde** — antes del cierre semanal. Cierra la semana en caliente, con la memoria fresca.
- **Lunes por la mañana** — antes de empezar la primera I de la semana nueva. La distancia ayuda a separar lo importante del ruido.

Otros slots válidos:
- **Fin de sprint o fin de iteración** — aunque caiga miércoles.
- **Antes de un viaje o pausa larga** — para no volver a una pila de diarios sin procesar.

Reglas anti-deriva:
- Máximo un recap por semana ISO (la etiqueta del archivo lo impide).
- Mínimo 5 días entre recaps (evita recaps reactivos).

---

## Persistencia

**Una carpeta:** `outputs/semanales/`

**Un archivo por semana:** `outputs/semanales/YYYY-Www.md`

- `YYYY-Www` es **semana ISO**, no semana natural. Ej: `2026-W19.md`, `2026-W20.md`.
- El archivo se nombra con la semana ISO en la que **se ejecuta** el recap, aunque la ventana de lectura sean los 7 días móviles hacia atrás.
- Si la ventana atraviesa dos semanas ISO (recap del lunes que cubre desde el miércoles anterior), el archivo va a la semana ISO actual, no a la anterior.

**Regla dura: nunca sobrescribir.**

- Si `outputs/semanales/2026-W19.md` ya existe y el operador invoca `/ias-recap` en esa misma semana, la skill:
  1. Abre el archivo existente.
  2. Muestra al operador qué hay dentro.
  3. Pregunta: ¿añadir nota / corregir / abortar?
  4. Si añade nota, va a una sección `## Adenda {YYYY-MM-DD}` al final, **nunca** modifica los 5 bloques originales.
- Razón: el recap es un acto histórico. Sobrescribirlo destruye la trazabilidad del ratchet effect.

**Si ya existe el de la semana ISO actual y el operador necesita un nuevo recap por sprint:**
- Sufijo `-sprint-{N}`. Ej: `2026-W19-sprint-2.md`.
- No es lo normal, pero la skill lo permite si el operador lo pide explícitamente.

---

## Conexión con H1

H2 depende de H1. Comprobaciones al inicio del comando:

1. **¿Existe `outputs/diarios/`?**
   - No → "No hay material. Ejecuta `/ias-start` durante la semana antes de hacer recap. Abortando."
   - Sí → continúa.

2. **¿Cuántos diarios en la ventana móvil de 7 días?**
   - 0 → mismo mensaje que arriba. Aborta.
   - 1-2 → activa **regla de muestra baja** del protocolo (ver `h2-recap-semanal.md` sección 7).
   - 3+ → recap completo.

3. **¿Existe el archivo de la semana ISO anterior?**
   - Sí → se lee para comparar techos en el Bloque 4.
   - No → el Bloque 4 se rellena sin comparación, marcado como "primer recap" o "sin recap previo en la ventana".

4. **¿Hay diarios fuera de la ventana de 7 días que nunca entraron en un recap?**
   - Si llevas mucho sin recap, esos diarios huérfanos se listan al final del recap actual con: "Diarios no procesados por estar fuera de la ventana móvil. Considera `/ias-recap multi-semana` la próxima vez."

---

## Cuándo NO ejecutar

- Si el operador acaba de cerrar una sesión I.A.S. hace menos de 1 hora — el recap necesita distancia mínima del trabajo.
- Si la ventana de 7 días está vacía y no hay justificación — el comando avisa pero no genera archivo vacío.
- Si ya se hizo recap de esa semana ISO en las últimas 24 horas — confirma con el operador antes de tocar nada.

---

## Lo que H2 NO hace

- No notifica. No envía email. No publica nada.
- No depende de cron, scheduled-tasks ni automatizadores externos similares.
- No lee fuera de `outputs/diarios/` y `outputs/semanales/`.
- No modifica `SKILL.md`, ni `comandos/`, ni `INTEGRACION.md`, ni `protocolos/h1-*`.
- No exporta el recap a Obsidian, Drive ni a ningún destino externo (eso queda para reglas pasivas globales si el operador las activa por separado).

---

## Flujo de invocación, paso a paso

```
1. Operador: /ias-recap
2. Skill: lee outputs/diarios/ y outputs/semanales/
3. Skill: aplica chequeos de la sección "Conexión con H1"
4. Skill: si todo OK, ejecuta los 5 bloques en orden (ver h2-recap-semanal.md sección 4)
5. Skill: presenta el archivo final al operador antes de escribirlo
6. Operador: confirma / pide ajustes / aborta
7. Skill: escribe en outputs/semanales/YYYY-Www.md
8. Skill: muestra al operador el path final y los compromisos para la semana
```

El paso 5 (presentación previa) es importante: el recap no se escribe sin que el operador haya leído los 5 bloques en pantalla. Es lo que evita que se vuelva un trámite automático.
