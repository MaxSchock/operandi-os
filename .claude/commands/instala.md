---
description: Instala iAmasters OS de principio a fin sin que el usuario toque la terminal. Punto de entrada en lenguaje natural — se dispara con "instala esto", "instálamelo", "install this", "monta el OS", "set this up" o "/instala". Detecta el SO, ejecuta el installer técnico (Sinapsis + capa OS), verifica y sigue con el onboarding. Mac y Windows (Git Bash).
---

# /instala

El camino de instalación **más simple**: el usuario dice "instala esto" y tú te encargas de todo. No le mandes a abrir una terminal — lo ejecutas tú con la tool `Bash` (ya está permitido en `.claude/settings.json`).

## Cuándo se dispara

Además de `/instala`, dispara este flujo cuando el usuario diga (castellano o inglés):
- "instala esto" · "instálamelo" · "instala el OS" · "monta el sistema" · "configúrame esto"
- "install this" · "set this up" · "install the OS"
- Pegue la URL del repo `iamasters-academy/iamasters-os` pidiendo instalarlo

## Process

### Paso 0 · Confirmar (una línea)

> "Te instalo iAmasters OS ahora mismo (Sinapsis + capa OS, ~30s) y luego seguimos con tu setup. ¿Le doy?"

Espera un "sí/vamos/ok". Si el usuario ya dijo "instala esto", eso ES el OK — no vuelvas a preguntar, arranca.

### Paso 1 · Detectar entorno y ejecutar el installer

1. Detecta el SO con `Bash`: `uname -s` (Darwin/Linux → Mac/Linux; MINGW/MSYS/CYGWIN → Windows con Git Bash).
2. Ejecuta el installer técnico con la tool `Bash`:
   ```bash
   bash scripts/install.sh
   ```
   - Es **idempotente y reentrante**: si ya corrió antes, retoma solo lo pendiente. Si algo estaba `failed`, se puede relanzar sin miedo.
   - **Windows**: corre igual vía Git Bash (Claude Code ya lo requiere). Si `uname` no existe / `bash` no está disponible para Claude Code → dile:
     > "En Windows necesito Git Bash (viene con Git para Windows: https://git-scm.com/download/win). Instálalo y me dices, o abre una terminal Git Bash en esta carpeta y ejecuta `bash scripts/install.sh`."
3. **Parsea la salida estructurada** línea a línea:
   - `[OK] <fase>` → hecho
   - `[SKIP] <fase>` → ya estaba
   - `[WARN] <fase> · <motivo>` → siguió con limitación (menciónalo pero no bloquea)
   - `[ERROR] <fase> · <motivo>` → **bloqueante**: para, explícalo en castellano, propón el arreglo (p.ej. instalar Node.js ≥18) y ofrece reintentar con `bash scripts/install.sh --resume`. No sigas al Paso 3.

### Paso 2 · Verificar (sin fiarte del "parece que fue bien")

Lee `~/.claude/skills/_install-state.json` y confirma que `phases.prereqs` y `phases.sinapsis-engine` están en `status: "done"`. Si `sinapsis-engine.validation` reporta `hooks` sin cablear o falta algún check, díselo y relanza `--resume`.

> Nota: los hooks de Sinapsis solo se **activan al reiniciar** Claude Code (se enlazan en `SessionStart`). Aunque el install haya ido perfecto, el motor de aprendizaje entra en vigor en la **próxima** sesión. Avísale al final.

### Paso 3 · Seguir con el onboarding

Con las fases técnicas en `done`, continúa el flujo conversacional:
1. Invoca `/install` (orquesta las fases restantes: context-files, operator-state, welcome).
2. `/install` deriva al `meta-onboarding-wizard` para la entrevista por sub-fases.

### Paso 4 · Cierre

> "Listo. iAmasters OS instalado y validado ✅. Los hooks de Sinapsis se activan al reiniciar Claude Code. ¿Seguimos con tu onboarding ahora o lo dejamos para luego?"

## Lo que NO haces

- ❌ Mandar al usuario a la terminal por defecto (solo como fallback si `bash` no está en Windows)
- ❌ Crear archivos en `~/.claude/skills/` a mano para simular instalación
- ❌ Marcar fases como `done` tú mismo — de eso se encarga `install.sh`
- ❌ Seguir al onboarding si quedó un `[ERROR]` sin resolver
