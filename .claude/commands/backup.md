---
description: Copia de seguridad de todos tus datos (context, brand-context, projects, clients, loops, memoria Sinapsis) a iCloud/Dropbox/HOME. Uso — /backup
---

# /backup

Guarda todo lo irreemplazable del operador fuera del repo. Lo que git no protege (tu contenido es privado y está gitignored), esto sí.

## Primera vez — el usuario ELIGE su nube

Si `.env` no tiene `IAMASTERS_BACKUP_DIR` y no existen backups previos:

1. Ejecutar `bash scripts/backup.sh --where` para ver qué nubes hay en su máquina (iCloud, Google Drive, Dropbox, OneDrive).
2. Preguntar al usuario en lenguaje llano: "¿Dónde quieres tus copias de seguridad?" listando SOLO las nubes detectadas (+ opción "carpeta local"). Si solo hay una, proponla directamente.
3. Guardar su elección en `.env`: añadir línea `IAMASTERS_BACKUP_DIR=<ruta-base>/iAmasters-Backup`.
4. Seguir con el backup normal. Esta pregunta no se repite nunca más.

## Proceso

1. Ejecutar:
   ```bash
   bash scripts/backup.sh
   ```
2. Destino (en este orden): `IAMASTERS_BACKUP_DIR` del `.env` (la elección del usuario) → auto-detección iCloud → Google Drive → Dropbox → OneDrive → `~/iAmasters-Backup/`. Conserva los últimos 7 backups y borra los más antiguos.
3. Al terminar, di al usuario DÓNDE quedó guardado y cuánto ocupa, en una línea. Sin tecnicismos.
4. Si el script falla, muestra el error tal cual y sugiere `/doctor`.
5. Si el usuario quiere cambiar de nube más adelante ("mejor en Google Drive"): actualiza `IAMASTERS_BACKUP_DIR` en `.env` y avisa de que los backups antiguos siguen en la ubicación anterior.

## Qué incluye

- **Del repo**: `context/`, `brand-context/`, `projects/`, `clients/`, `loops/`, `.env`, skills propias y `settings.json`
- **De Sinapsis global** (`~/.claude/skills/`): operator-state, instincts, daily summaries, catalog, passive rules, install state

## Restaurar

Si el usuario pide restaurar ("restaura mis datos", "recupera el backup del día X", "me he cambiado de Mac"):

1. Lista los backups con `bash scripts/backup.sh --list` y confirma cuál quiere (el más reciente por defecto).
2. **Pide confirmación explícita** antes de copiar nada (vas a sobrescribir su estado actual).
3. Copia el contenido de `<backup>/repo/` sobre el repo y `<backup>/sinapsis/` sobre `~/.claude/skills/`.
4. Sugiere `/doctor` para verificar que todo quedó sano.

## Disparadores en lenguaje natural

"haz un backup", "copia de seguridad", "guarda mis datos", "backup", "respalda todo", "me cambio de ordenador" (este último → restaurar).

## Proactividad

En `/wrap-up`, si el backup más reciente tiene más de 7 días (o no existe ninguno), sugiere en una línea: "Hace más de una semana del último backup — ¿lanzo `/backup`? (30 segundos)". No insistas si dice que no.
