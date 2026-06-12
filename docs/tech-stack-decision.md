# Tech stack por proyecto — árbol de decisión

> Decidido 2026-06-12 (sesión de optimización del setup). Objetivo: dejar de usar n8n por inercia.
> Regla transversal: **si el flujo es >50% prompts/LLM y <50% integración, n8n sobra.**

## El árbol

Pregunta en orden. La primera que encaje, gana.

**1. ¿Es un one-off, o necesita interactuar con una web sin API?**
→ **Script puntual / Playwright** en el VPS. Sin orquestador, sin deploy formal. Ejemplos: scraping autenticado, RPA sobre panel propietario (CRM Pierre), backfills de una vez.

**2. ¿Es lógica centrada en LLM con estado conversacional o decisiones de agente?**
→ **Servicio Python en VPS** (patrón strategist: FastAPI + Claude Agent SDK + cron interno, deploy como stack Swarm). Ejemplos: strategist, claude-debug, content-engine-daemon. Señales: prompts largos versionados en git, memoria entre turnos, herramientas propias, polling continuo.

**3. ¿Es operación interna mía (reporting, mantenimiento, auditoría) que cambia a menudo?**
→ **Claude Code + cron/schedule** (o routine de claude.ai). Barato de crear y de tirar. Ejemplos: vigilancia Kaps Step 4B vía routines, auditorías de workflows, EOD. Si sobrevive 3 meses sin cambios y necesita fiabilidad, promocionar a servicio (opción 2).

**4. ¿Es integración multi-paso determinista entre sistemas, con triggers externos y volumen?**
→ **n8n**. Es su terreno: webhooks/schedules como triggers, queue mode para volumen, retries y error-workflow integrados, version history, y el cliente puede ver/tocar el flujo. Ejemplos: outreach Step 1-5 (27 workflows), pipeline Hemmersbach, RAG ingest Suritec.

**5. ¿Son solo 2 SaaS conocidos conectados para un cliente que se lo va a auto-gestionar?**
→ Valorar **Zapier/Make** antes que n8n self-hosted (sin mantenimiento de infra nuestro).

## Matices que rompen empates

- **¿Quién lo mantiene después?** Si el cliente hereda el sistema: n8n (UI visual) o Zapier. Si lo mantengo yo: código en git siempre gana a nodos.
- **¿Cuánto cuesta el error?** Mensajería a leads reales o facturación → donde haya safety gates probados (hoy: n8n con Outbound Safety Gate). No migrar esos flujos sin replicar los gates.
- **Deuda conocida de n8n**: binary_data en BD (~13GB), gotchas de splitInBatches/ExecuteWorkflow, edición vía REST con body estricto. Cada workflow nuevo hereda ese mantenimiento; contarlo como coste.
- **Híbrido válido**: n8n como capa de triggers/integración que llama por HTTP a un servicio Python para la parte LLM (patrón ya usado en Pierre: workflow n8n + server.js + preprocessor).

## Backlog de salidas de n8n (estado 2026-06-12)

| Candidato | Destino | Esfuerzo | Por qué |
|---|---|---|---|
| Daily digest comercial v4 | strategist (ya tiene cron 09:00) | Bajo | El contenido ya lo genera Claude; n8n solo envuelve |
| LN Auto-Reply v4 (personal brand, 5 personas) | strategist | Medio | Prompts versionados en git, menos hardcode por persona |
| Error Notification `P7wPxAjFeTbElZvn` | se queda en n8n | — | Es el productor del inbox; claude-debug ya consume. Revisar solo si falla |
| Outreach Step 1-5 (27 workflows) | se queda en n8n | — | Queue mode + volumen + safety gates: caso de uso correcto |

Las migraciones se ejecutan en sesiones dedicadas, una a una, con periodo de doble-corrida antes de apagar el workflow viejo.
