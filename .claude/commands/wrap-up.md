---
description: Cierre de sesión iAmasters OS. Genera daily summary, sincroniza skills, propone commit.
---

# /wrap-up

Invoca la skill `meta-wrap-up` que vive en `.claude/skills/_meta/meta-wrap-up/SKILL.md`.

## Qué hace

1. Recapitula la sesión (qué se hizo, qué quedó)
2. Sincroniza `synapsis/skills-catalog.json` si hubo cambios en `.claude/skills/`
3. Actualiza el skills registry de `CLAUDE.md`
4. Append a `context/learnings.md` si hubo aprendizajes
5. Genera/actualiza `~/.claude/skills/_daily-summaries/<TODAY>.md`
6. Detecta proyectos a archivar (status: done > 7 días)
6.5. **Retira lo cerrado de `context/working-memory.md`** (ver abajo)
7. Propone Git commit (espera aprobación)
8. Sugiere `/eod` Sinapsis si es final del día
9. Si el último backup tiene >7 días o no existe ninguno (`bash scripts/backup.sh --list`), sugiere en una línea lanzar `/backup` (30 segundos). No insistir si dice que no.

## Retirada de working-memory (paso 6.5, sin preguntar)

`context/working-memory.md` se inyecta en contexto al arrancar CADA sesión, así que
su coste es fijo. Añadir es barato de escribir y caro de mantener, por eso el cierre
tiene que retirar y no solo añadir:

- Por cada hilo tocado hoy: si su pendiente se cerró, **borrar la línea**. No marcarla
  como hecha ni tacharla: borrarla. El relato ya está en el session-log.
- Si el hilo sigue vivo pero su texto ha crecido, recortarlo a qué falta y dónde está
  el detalle. Un hilo son una o dos líneas, nunca un informe.
- Regla de olor: si el fichero pasa de ~2.500 caracteres, se está usando como informe
  en vez de como scratchpad. Podar antes de seguir.

(2026-08-03: llegó a 25.723 caracteres, diez veces su tope, con hilos de mediados de
julio ya cerrados. Se podó a 4.010.)

## Comando

Carga e invoca la skill `meta-wrap-up`. Sigue el proceso de su SKILL.md paso a paso.

NO hace push automático ni commit sin aprobación explícita.
