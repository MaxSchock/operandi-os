# Sinapsis: por qué el aprendizaje automático no aprende

Diagnóstico verificado sobre el sistema vivo el 27-08-2026.

## El fallo raíz: observa herramientas, no al usuario

El hook que recoge los datos de aprendizaje (`sinapsis-learning/hooks/observe.sh`) **no captura ni una sola línea de lo que escribe Max**. Verificado: `grep -n "user_prompt|prompt|message|user"` sobre el hook devuelve cero coincidencias. Lo que registra es esto:

```
2026-05-12T08:31:27.463Z | Write | env-vars-never-hardcode
2026-05-12T09:18:39.569Z | Bash  | env-vars-never-hardcode
```

Herramienta y regla disparada. Nada más.

El motor que busca patrones (`_session-learner.sh`, 447 líneas) tiene cinco detectores, y los cinco miran secuencias de herramientas:

| Detector | Qué busca |
|---|---|
| PATTERN 1 | error → misma herramienta con éxito en 5 eventos |
| PATTERN 2 | Edit/Write sobre el mismo fichero en 10 eventos |
| PATTERN 3 | la misma secuencia de 3 herramientas dos veces |
| PATTERN 4 | el mismo error en propuestas de 3 días distintos |
| PATTERN 5 | secuencias de herramientas dentro de subagentes |

Ninguno lee una frase de Max. Las 596 correcciones de los últimos cuatro meses pasaron por delante de este motor y **no produjo ni una sola regla**. Por eso el log dice "no patterns" un día tras otro: está buscando en el sitio equivocado.

Las 41 reglas de conducta valiosas del sistema las escribí a mano, una a una, cuando Max me lo pidió expresamente.

## Las 125 propuestas acumuladas

| Tipo | Nº | Qué son en realidad |
|---|---:|---|
| `workflow_chain` | 106 | Secuencias de herramientas repetidas. Ruido |
| `user_correction` | 12 | Mal nombradas: son "edité dos veces el mismo fichero" (`correction-route-ts`, `correction-agent-loop-ts`). No hay corrección de Max en ninguna |
| `error_resolution` | 7 | `fix-bash`, `fix-edit`, `fix-read`, `fix-write`. Nada accionable |

Cero propuestas derivadas de lo que dijo el usuario. El pipeline `/evolve` que las procesa lleva sin ejecutarse desde el 03-07 (fecha de los `.bak-evolve` de los índices).

## Los instintos: 53, de los que sirven 2

- **41 nunca se han activado** (`occurrences: 0`).
- Los que sí disparan son los genéricos de fábrica, no lo aprendido de Max: `env-vars-never-hardcode` (10.883 activaciones desde mayo) y `git-commit-conventional` (563).
- Un instinto decaído (`pm2-restart-update-env-overwrites-process-env`, nivel draft) se sigue evaluando y ensuciando el log en cada comando.
- `_operator-state.json` marca `lastSynced: 2026-05-12` y `contextTokenEstimate: 0`. Lleva tres meses y medio sin sincronizarse.

## Las 31 reglas pasivas

Estas **sí funcionan**: el activador las inyecta cuando su patrón casa con el comando. Pero no llevan contador de activaciones (los campos son `id`, `trigger`, `inject`, `severity`, `category`, `tokens`), así que no hay forma de saber cuáles sirven y cuáles no. No se puede mejorar lo que no se mide.

*(Nota: en una lectura anterior interpreté ese "0" como que no se activaban nunca. Es falso: el campo no existe, que es distinto. Verificado leyendo el activador.)*

## El punto de inyección es el equivocado

Todos los mecanismos de Sinapsis cuelgan de `PreToolUse`: se disparan cuando ya he decidido qué herramienta usar y con qué argumentos. Llegan tarde para todo lo que no sea un comando concreto, y son ciegos a lo que Max acaba de pedir.

`UserPromptSubmit` — el punto donde una regla llegaría **antes** de razonar, y donde se puede leer lo que Max escribe — no está usado en ninguno de los tres ficheros de configuración. Verificado.

## Veredicto por componente

| Componente | Estado | Decisión |
|---|---|---|
| Reglas pasivas (31) | Funcionan, sin medición | **Conservar**, añadir contador |
| Instintos: los 2 de fábrica | Funcionan | **Conservar** |
| Instintos: los 41 muertos | Nunca disparan (patrón mal definido) | **Rediseñar el disparo o jubilar** |
| Instinto decaído | Ruido en cada comando | **Retirar** |
| `session-learner` | Ciego al usuario | **Reescribir el detector o jubilarlo**: la señal está en los mensajes de Max |
| 125 propuestas | Ruido de secuencias | **Descartar** con backup |
| `/evolve` | Sin correr desde el 03-07 | Depende de qué pase con el learner |
| `_operator-state.json` | Sin sincronizar desde el 12-05 | **Resincronizar o retirar** |
