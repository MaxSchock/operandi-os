# Plantillas de loops

Estas plantillas son puntos de partida para montar loops recurrentes con
`automation-loop-engine`. Cada una ya trae el Loop Canvas de 9 campos rellenado al
80% y marca con `[PERSONALIZA: ...]` lo que depende de tu negocio, tus herramientas
o tus límites.

## Cómo usarlas

Dile a Claude algo como:

```text
Monta el loop de propuestas desde la plantilla.
```

La skill debe:

1. Copiar la plantilla elegida a `loops/<nombre>/loop-spec.md`.
2. Preguntarte solo los huecos `[PERSONALIZA: ...]`.
3. Generar `REGLAS.md` y `loop-state.md`.
4. Registrar el loop en `loops/_index.md`.
5. Proponer un lote piloto de 3 items en A1.

## Plantillas disponibles

| Plantilla | Para qué sirve |
|---|---|
| `loop-contenido-semanal.md` | Convierte un contenido fuente semanal en 5-8 piezas multiplataforma listas para revisar. |
| `loop-propuestas.md` | Transforma solicitudes de cliente en propuestas listas para revisión humana. |
| `loop-triaje-leads.md` | Enriquece leads, los puntúa contra ICP y prepara una primera respuesta. |
| `loop-informe-cliente.md` | Genera informes periódicos por cliente desde notas y métricas del OS multi-cliente. |
| `loop-revision-semanal.md` | Revisa todos los loops activos, sus métricas y las decisiones de autonomía. |
