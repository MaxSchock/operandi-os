# Context

Capa dinámica que evoluciona con el uso del OS. Aquí vive todo lo que cambia con el tiempo: identidad del operador, decisiones tomadas, lecciones aprendidas.

## Archivos

- `working-memory.md` — **scratchpad de trabajo** (hilos activos / notas de entorno / decisiones pendientes). Se inyecta al inicio de cada sesión (`meta-start-here`) y se mantiene en el cierre (`meta-wrap-up`). Tope ~2.500 caracteres. Es la memoria "de trabajo" del OS: lo que el agente tiene presente sin buscar nada. Privado (gitignored).
- `soul.md` — personalidad del agente (cómo responde, boundaries). Estática, la editas tú.
- `user.md` — perfil del operador en el repo (preferencias, stack del día a día). Se rellena en onboarding y va creciendo.
- `learnings.md` — feedback consolidado por skill, en formato humano-legible.
- `daily-memory/<YYYY-MM-DD>.md` — sesiones del día con goal/done/pending/decisions.

## Diferencia con Sinapsis

Sinapsis (en `~/.claude/skills/_*.json`) guarda el contexto **global del operador** que aplica a todos los proyectos.

Este `context/` guarda el contexto **específico del repo iAmasters OS** que solo aplica aquí (decisiones que tomaste sobre tu marca, learnings de skills propias, etc.).

## Privacidad

`user.md`, `daily-memory/` están en `.gitignore`. Solo `soul.md`, `learnings.md` (genérico) y este README van al git.
