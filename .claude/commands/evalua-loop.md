---
description: "Evalúa un loop existente con automation-loop-engine: scorecard de 5 métricas, revisión de autonomía A0-A3 y próximos ajustes."
---

# /evalua-loop

Ejecuta el MODO EVALUACIÓN de `automation-loop-engine` sobre un loop existente.

## Uso

```text
/evalua-loop <nombre>
```

Ejemplo:

```text
/evalua-loop propuestas
```

## Proceso

1. Resolver `<nombre>` contra `loops/<nombre-kebab>/`.
2. Leer `loop-spec.md`, `REGLAS.md` y `loop-state.md` si existe.
3. Invocar la skill `automation-loop-engine` en **MODO EVALUACIÓN**.
4. Generar scorecard con 5 métricas:
   - First-Pass Yield.
   - Tasa de retrabajo.
   - Tiempo de ciclo.
   - Tasa de escalación.
   - Reglas/semana.
5. Decidir si toca:
   - Subir o bajar autonomía A0-A3.
   - Ajustar checklist.
   - Endurecer criterio de item listo.
   - Partir una estación en dos.
   - Matar o pausar el loop.
6. Actualizar `loops/_index.md` con última revisión y nivel A actual si el usuario aprueba los cambios.

Si el loop no existe, mostrar los loops disponibles y sugerir `/loops`.
