---
description: Deshace la última actualización del OS si algo se rompió. Restaura código y datos desde el backup automático de update.sh. Uso — /restaura
---

# /restaura

Botón de "deshacer" de `/actualiza`. Si tras actualizar algo va mal, esto devuelve el OS exactamente a como estaba antes — código Y datos.

## Proceso

1. Confirmar con el usuario qué pasa ("¿qué se rompió tras actualizar?") — si el problema es menor, quizá `/doctor` lo arregla sin rollback. Ofrécelo primero.
2. Si procede el rollback, mostrar los backups disponibles:
   ```bash
   bash scripts/rollback.sh --list
   ```
3. **Confirmación explícita** del usuario para restaurar (por defecto, el más reciente).
4. Ejecutar:
   ```bash
   bash scripts/rollback.sh --yes
   ```
   (o `--from <nombre>` si eligió uno concreto)
5. El script ya guarda un snapshot del estado actual ANTES de restaurar (en `.backup/pre-rollback-*`), así que el rollback también es reversible. Díselo al usuario: "si esto era un error, también se puede deshacer".
6. Al terminar, ejecuta `/doctor` para verificar salud y resume en 2 líneas qué versión quedó activa.

## Qué hace por debajo

- Devuelve el código del OS al commit previo a la última actualización (`git reset --hard`, solo afecta archivos del sistema — tus datos están fuera de git)
- Restaura `context/`, `brand-context/`, `projects/`, `clients/`, skills y settings desde el backup que `update.sh` creó automáticamente

## Disparadores en lenguaje natural

"deshaz la actualización", "vuelve a la versión anterior", "el update ha roto algo", "restaura el OS", "rollback", "esto antes funcionaba".
