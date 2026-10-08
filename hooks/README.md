# hooks/

Git hooks para quien **desarrolla** este repo (no afectan a los miembros que instalan el OS).

## Activar

Una sola vez en tu clon:

```bash
git config core.hooksPath hooks
```

## `pre-commit`

Antes de cada commit:
1. **Bloquea secretos** hardcodeados (`API_KEY`, `SECRET`, `PASSWORD`, `PRIVATE_KEY`, tokens…). Incondicional.
2. **Avisa de archivos grandes** (>1 MB) y pide confirmación si hay terminal.

Idea original aportada por la comunidad (PR #10), adaptada y simplificada.
