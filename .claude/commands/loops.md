---
description: Lista los loops del operador, candidatos pendientes del radar y estado resumido. Lee loops/_index.md y las carpetas de loops sin modificar nada.
---

# /loops

Lista los loops diseñados en `loops/` y los candidatos pendientes detectados por radar.

## Uso

```text
/loops
```

## Proceso

1. Leer `loops/_index.md` si existe.
2. Listar carpetas `loops/<nombre-kebab>/`, excluyendo `_templates/`.
3. Para cada loop:
   - Mostrar nombre.
   - Mostrar objetivo.
   - Mostrar disparador.
   - Mostrar nivel A actual.
   - Si `loop-state.md` existe y contiene conteo de items procesados, mostrarlo.
   - Marcar si falta `loop-spec.md` o `REGLAS.md`.
4. Mostrar candidatos pendientes del radar si `loops/_index.md` tiene sección `## Candidatos detectados`.

## Si no hay loops

Responder:

> Aún no hay loops creados. Para crear el primero, dime algo como:
> "diseña el loop de propuestas" o "convierte este proceso repetitivo en un sistema".
> Se activará la skill `automation-loop-engine` y rellenaremos el Loop Canvas.

No crear archivos desde este comando. Solo lectura.
