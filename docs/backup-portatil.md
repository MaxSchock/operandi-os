# Copia de seguridad del portátil

Copia cifrada (restic) del WSL del ThinkPad al Object Storage de Contabo (S3, bucket `thinkpad-restic` en `https://eu2.contabostorage.com`; no hace falta ningún flag de bucket-lookup). Desde el 15-10-2026; antes iba al VPS por sftp. Diaria a las 23:30 con el cron de WSL. Retención: 7 diarias, 4 semanales, 6 mensuales. GitHub sigue siendo solo para el código.

**Qué entra:** `~/iamasters-os`, `~/.claude`, `~/.config`, `~/src`, `~/.ssh`, `~/backups`, `~/backups-linus` y el crontab (volcado a `~/.config/restic/crontab.txt`).

**Qué no entra (`~/.config/restic/excludes.txt`):** el `.git` de los repos con remoto en GitHub y sin commits pendientes (iamasters-os, dash-ro, openmontage, watch, skill-audit, hemmersbach/service); el `.git` de `_wiki`, operandi-services y hemmersbach SÍ entran porque tienen commits sin subir. Tampoco `node_modules`, venvs, `__pycache__`, `~/.cache`, cachés y sesiones temporales de `~/.claude`, `tools/codex` (reinstalable), chromium y `~/.banco-home` (copias de credenciales).

**Credenciales S3:** `~/.config/restic/contabo-s3.env` (variables `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`; el script lo carga solo). **Contraseña del repositorio:** `~/.config/restic/thinkpad.pass` (600) y `/root/secrets/restic-thinkpad.pass` en el VPS. Max la tiene además en su gestor de contraseñas. Sin ella la copia no se abre.

**Restaurar un fichero:**
```
set -a; . ~/.config/restic/contabo-s3.env; set +a
export RESTIC_REPOSITORY=s3:https://eu2.contabostorage.com/thinkpad-restic RESTIC_PASSWORD_FILE=~/.config/restic/thinkpad.pass
restic restore latest --tag thinkpad --include /home/max/.claude/CLAUDE.md --target ~/restaurado
```
`restic snapshots` lista las versiones; sustituye `latest` por un id para ir atrás.

**Portátil nuevo (todo):** 1) instalar restic (binario de github.com/restic/restic/releases) ; 2) escribir la contraseña en `~/.config/restic/thinkpad.pass` y las dos claves S3 en `~/.config/restic/contabo-s3.env` (de la cuenta de Contabo o del gestor de contraseñas de Max); 3) cargar el `.env` y exportar las dos variables de arriba; 4) `restic restore latest --tag thinkpad --target /`; 5) `crontab ~/.config/restic/crontab.txt` y reinstalar lo excluido (venvs con pip, `npm install`).

**Registro y avisos:** `~/.config/restic/ultimo.log` (fecha, resultado, tamaño añadido), `historial.log` y `ultimo-detalle.log`. Si no existe, tiene error o pasa de 48 h, `salud-os.py` lo avisa al abrir sesión. El script escribe «INICIO» al empezar y el resultado al salir (con `trap`), así que un fallo intermedio deja rastro y `salud-os.py` lo avisa. Script: `scripts/backup-portatil.sh` (`--dry-run` para ver el tamaño sin subir).

**Tamaño:** ver el final de este fichero.

## Tamaño

Primer snapshot (15-10-2026): 7,4 GiB leídos, 4,2 GiB en el repositorio del VPS (compresión 1,8x; lo gordo son las auditorías gz de Hemmersbach, que no comprimen). Las copias diarias añaden unos MB. Mientras estuvo en el VPS lo subió del 83 % al 87 % de disco.

Repositorio S3 el 15-10-2026: 4,17 GiB. Los snapshots se copiaron del VPS con `restic copy` (ids nuevos, mismas fechas).

**Copia antigua en el VPS:** borrada el 15-10-2026 a las 16:55 con OK de Max, tras comprobar en S3 los dos snapshots, `restic check --read-data-subset=5%` sin errores y un listado de ficheros. El VPS volvió al 82 %. Solo queda allí la contraseña en `/root/secrets/`.
