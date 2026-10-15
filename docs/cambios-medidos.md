# Cambios medidos

Todo cambio al sistema hecho para mejorar algo se registra con una métrica y se mide después. Una regla en prosa no baja la tasa de corrección (medido 14-10: 17-24 %), así que el control lo hacen un registro, un script y dos hooks.

## Cuándo se registra

Cualquier cambio de rendimiento en: arnés de Claude Code (CLAUDE.md, hooks, activador, reglas, skills, settings), prompts de Linus o de agentes de clientes, workflows de n8n, servicios del VPS. Un arreglo puntual sin efecto medible no se registra; se dice «sin medir porque <motivo>» en la respuesta.

## Cómo se añade

```
python3 scripts/cambios-medidos.py add --sistema arnes-os|linus|n8n:<cliente>|operandi-services|otro \
  --que "una frase" --ficheros "qué se tocó" --metrica tasa_correccion_semanal,reglas_por_prompt \
  --como-revertir "cómo deshacerlo" [--base metrica=valor] [--revisiones 7,14]
```

Si la métrica está en el catálogo y no pasas `--base`, mide el valor base en el momento. Las revisiones son +7 y +14 días. Antes de editar un fichero, copia previa en `~/.claude/backups/<fecha>/`.

Catálogo (`python3 scripts/cambios-medidos.py medir <métrica>`): `tasa_correccion_semanal`, `tokens_fijos_arranque`, `reglas_por_prompt`, `pct_inyecciones_entre_sesiones`, `banco_os`, `errores_n8n_7d:<workflow>`, `banco_linus`. Cualquier otra se escribe `manual:<descripción>` y se juzga a mano. Hoy sin medir desde local: `banco_os` (hasta que el paso 2 deje `banco/resultados/<corrida>/resumen.json` con `puntuacion_media`) y `errores_n8n_7d` (no hay clave de Supabase en local).

## Qué pasa los lunes

`scripts/mantenimiento-setup.sh` ejecuta `cambios-medidos.py check`: mide cada entrada con revisión vencida, compara con la base (cambio de menos del 5 % = ruido), escribe el resultado en la entrada y en `docs/medicion-setup/cambios-<fecha>.md`, y añade la tabla de abiertos al informe del lunes. Tras la última revisión el estado pasa solo a `mejora`, `sin_cambio`, `empeora` o `sin_medir`.

## Qué recuerda y qué bloquea

- `~/.claude/hooks/salud-os.py` pone un bloque `<cambios-medidos>` al arrancar con las entradas abiertas y vencidas.
- `~/.claude/hooks/guard-cambio-medido.py` (Stop) bloquea el cierre del turno si se editó un fichero del arnés o hubo un despliegue (`docker service update`, PUT/PATCH a `/api/v1/workflows/`, `git push` en repos de servicios) y en la sesión no hay entrada nueva ni la frase «sin medir porque». No salta por working-memory, session-logs ni ficheros de proyectos. Registro del guard: `~/.claude/session-env/guard-cambio-medido.log`.

## Cómo se cierra

```
python3 scripts/cambios-medidos.py close <id> <abierto|mejora|sin_cambio|empeora|revertido|sin_medir> "nota"
```

Estados: `abierto`, `mejora`, `sin_cambio`, `empeora`, `revertido`, `sin_medir`. Si empeora, se revierte con el `como_revertir` de la entrada y se cierra como `revertido`.
