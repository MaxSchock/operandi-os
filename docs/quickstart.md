# Quickstart — primeros 30 minutos con iAmasters OS

> Para alguien que clonó el repo, ejecutó `bash scripts/install.sh`, y abrió Claude Code en el repo.

## Minuto 0-5 · Onboarding

Claude Code te lanza el wizard automáticamente. 7 preguntas:

1. Avatar (single business / freelance / agencia / formador)
2. Nivel técnico (cero / intermedio / avanzado)
3. Dominio principal (marketing / operations / strategy / dev / mixto)
4. Stack actual (multi-select)
5. Idioma de outputs cliente (si aplica)
6. Firecrawl API key (opcional pero recomendado)
7. Identidad básica (nombre, email, web/LinkedIn)

Output: `~/.claude/skills/_operator-state.json` y `context/user.md` rellenados.

## Minuto 5-15 · Brand voice (opcional pero recomendado)

Si dijiste sí al brand voice:

- Pega tus URLs públicas (web, LinkedIn, YouTube, blog)
- Firecrawl scraping → extrae voice samples
- Claude analiza patrones de tu voz
- Genera `brand-context/voice/voice-profile.md` + 3 registros (A/B/C)
- Genera `brand-context/positioning/positioning.md` y `brand-context/icp/icp.md`

Output: tu marca queda "instalada" en el OS. Cualquier skill marketing-* la usará automáticamente.

## Minuto 15-25 · Primera tarea real

Pide algo concreto. Ejemplos:

```
"Escribe 3 versiones de post LinkedIn sobre <tema>"
→ Claude usa marketing-copywriting con tu voice profile

"Repurposea esta clase del Café Camaleónico para redes"
→ marketing-content-repurposing

"Genera un HTML compartible explicando esta decisión"
→ tool-visual-explainer
```

## Minuto 25-30 · Wrap-up

Antes de cerrar:

```
/wrap-up
```

Claude:
- Genera daily summary en `~/.claude/skills/_daily-summaries/<TODAY>.md`
- Updates skills registry si añadiste alguna
- Propone git commit (acepta o rechaza)
- Te dice qué empezar mañana al volver

## Próximos días

Cuando vuelvas a abrir Claude Code en el repo:

```
/start-here
```

Te recapitulará lo de ayer + propondrá tarea del día. La memoria persiste — no más "explícame tu stack otra vez".

## Comandos básicos

| Comando | Qué hace |
|---|---|
| `/start-here` | Ritual de inicio (resumen + propuesta) |
| `/wrap-up` | Cierre de sesión + commit |
| `/add-client` | Crear cliente nuevo (multi-cliente) |
| `/system-status` | Dashboard Sinapsis (engine) |
| `/evolve` | Promover instincts aprendidos a permanentes |
| `/eod` | End of day multi-proyecto (Sinapsis) |
| `/dashboard-sinapsis` | Visualización del aprendizaje del sistema |

## Cuándo NO usar el OS

- Editar el código de tu app → abre Claude Code en la carpeta de la app, no en este repo
- Sesión exploratoria que no quieres ensuciar memoria → modo vanilla en otra carpeta
- Tarea ultracorta (<2 min) → más fricción que valor

## Siguiente lectura

- `docs/multi-client-guide.md` (en v0.3.0) — flujo completo de servir N clientes
- `docs/skill-creation-guide.md` — crear tus propias skills siguiendo el patrón
- `docs/synapsis-overview.md` — entender qué hace el engine de memoria
