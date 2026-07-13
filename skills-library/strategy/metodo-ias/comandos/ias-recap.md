---
description: "Genera el recap semanal del método I.A.S. (S macro): inventario, Pareto, boundary erosion, recalibración de techo, delegables."
argument-hint: "[YYYY-Www, opcional; por defecto la semana ISO actual]"
---

# /ias-recap

Activa el **modo semanal** de la skill `metodo-ias` (Hipótesis 2: recap macro semanal).

## Qué hace

1. Lee el protocolo del modo semanal en `protocolos/h2-recap-semanal.md`. Si no existe, avisa al usuario y para.
2. Lee la skill raíz `SKILL.md` para confirmar reglas anti-drift y formato de salida.
3. Lee `outputs/diarios/` y filtra los archivos cuya fecha cae dentro de la semana objetivo (semana ISO actual por defecto, o la pasada por argumento).
4. Si hay menos de 3 archivos diarios en la semana, sigue corriendo pero avisa en el bloque de inventario de que el sample es bajo y la S macro será aproximada.
5. Ejecuta los cinco bloques del protocolo H2: inventario, Pareto 80/20, boundary erosion, recalibración del techo, delegables.
6. Devuelve al usuario:
   - Resumen ejecutivo en chat.
   - Archivo `outputs/semanales/YYYY-Www.md` con los cinco bloques.
   - Fallback a `~/.claude/ias-outputs/semanales/` si no hay proyecto detectado en el cwd.

## Argumento

`$ARGUMENTS` — semana ISO `YYYY-Www` (ejemplo `2026-W19`). Opcional. Si no llega, usa la semana actual.

## Reglas

- Español. Sin emojis. Código en inglés.
- No inventar outputs ni datos: solo se cuenta lo que está en `outputs/diarios/` para la semana objetivo.
- Si en alguna sesión diaria la S no se cerró, marcarlo en el inventario como sesión incompleta.
- El bloque de boundary erosion solo afirma lo que está respaldado por datos del propio archivo diario (timestamps, notas explícitas). Si no hay datos, decirlo.

## Tono al conducir al usuario

La mecánica interna (los 5 bloques numerados, la regla de muestra baja, el contrato con H1, los paths) es jerga del manual. **No sale al chat.** El recap en chat se siente como una conversación con alguien que ha leído tu semana y la cuenta de forma directa.

- **Primer mensaje:** algo que el usuario reconozca como suyo de inmediato. Por ejemplo: *"He leído los 5 archivos que dejaste esta semana. Antes de darte el recap, una sola pregunta: ¿la haces para cerrar el viernes o para abrir el lunes? Cambia un poco el énfasis."*
- **Sin numerar los bloques** en lo que el usuario ve. El archivo final sí los lleva (es referencia), pero la conversación no.
- **Sin acrónimos** (S macro, ratchet effect, boundary erosion) **sin glosa**. Si necesitas el término, explícalo en una línea: *"miro si hubo días que no cerraste sesión — eso es lo que más burnout genera."*
- **Sin paths del repo** en chat hasta el final, cuando confirmas que el archivo está escrito.
- Las alertas duras (3 semanas con techo subiendo, sin delegables, etc.) se nombran como observaciones de un compañero, no como warnings del sistema.

## Salida esperada

Un archivo `outputs/semanales/YYYY-Www.md` y un resumen en chat de máximo 12 líneas con los cinco bloques resumidos. El recap es input directo de la siguiente semana: el techo recalibrado y los delegables se citan en el primer `/ias-start` de la semana siguiente.
