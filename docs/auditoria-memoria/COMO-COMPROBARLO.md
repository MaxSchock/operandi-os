# Cómo comprobar que la memoria nueva funciona

Cuatro comprobaciones, de la más rápida a la más lenta.

## 1. Ahora mismo (10 segundos): los gates

Pídeme en cualquier sesión que borre algo real o que mande un WhatsApp sin haber leído el hilo.
Verás en pantalla un bloque que empieza por `BLOQUEADO por guard-borrado` o
`BLOQUEADO por guard-envio-externo`, con la salida indicada. Antes no pasaba nada.

Si de verdad quieres que se ejecute:
- borrado: `touch /tmp/claude-destructive-consent`
- envío: `touch /tmp/claude-send-consent`
- mensaje largo: `touch /tmp/claude-mensaje-largo-consent`
(valen 10 minutos y un solo uso)

**Añadidos el 09-09**, que convierten en barrera las seis reglas que más reincidían:

- `guard-mensaje-corto.py` — pídeme que le mande a Jonas un WhatsApp de tres párrafos, o uno que
  acabe en "avísame si necesitas algo". No sale. El tope son 600 caracteres, que es el percentil 95
  de tus 9.952 mensajes reales: salta con lo raro, no con lo normal.
- `guard-repaso-canales.py` — abre una sesión por la mañana con un "buenos días" a secas. No podré
  contestarte hasta haber mirado los canales, y el bloqueo dice cuáles me faltan.
- `guard-respuesta.py` (punto 4) — pídeme que revise algo y mira si afirmo cómo está sin haber
  abierto nada. Esa respuesta no llega a salir.

Lo que ves cuando saltan queda apuntado, para poder recalibrarlos después:
```bash
tail ~/.claude/session-env/guard-mensaje-corto.log
tail ~/.claude/session-env/guard-repaso-canales.log
tail ~/.claude/session-env/guard-respuesta.log
```

## 2. En el día a día: lo que deberías dejar de ver

- Dejo de preguntarte por la cuenta correcta cuando nombras un cliente (sé que Suritec es KIsult).
- Dejo de pedirte datos que ya me diste en otra sesión.
- Los documentos salen en el idioma y el nivel del cliente sin que lo recuerdes.
- Las horas salen como cifra cerrada, no como horquilla.

Si vuelvo a fallar en algo de eso, es señal de que falta un disparador. Dímelo y se añade en un minuto.

## 3. Mañana: el aprendizaje solo

Al arrancar la primera sesión del día, el destilador procesa las sesiones cerradas ayer.

```bash
cat ~/.claude/session-env/destilador/destilador.log
```
Una línea por sesión: `<id> | incidentes=N nuevas=N repetidas=N`.

Y las reglas que haya escrito solo:
```bash
ls -lt ~/.claude/projects/-home-max-iamasters-os/memory/feedback*.md | head -5
grep -l "estado: prueba" ~/.claude/projects/-home-max-iamasters-os/memory/feedback*.md
```

## 4. Qué reglas se te activaron en una sesión

```bash
cat ~/.claude/session-env/activaciones-*.jsonl | tail -20
```

## Y si algo se rompe

Todo lo tocado tiene copia:
```bash
ls ~/.claude/backups/auditoria-memoria-20260827-194031/
```
Para volver atrás del todo: copiar de ahí `settings.json`, `CLAUDE.global.md`, `memory/` y `skills/`.

Para desactivar solo una pieza sin tocar el resto, quita su línea de `~/.claude/settings.json`:
`activador-reglas.py`, `guard-borrado.py`, `guard-envio-externo.py`, `guard-mensaje-corto.py`,
`guard-respuesta.py`, `guard-repaso-canales.py`, `destilador.py`, `salud-os.py`.

Y desde el 09-09 los hooks se versionan en `sinapsis-state` junto a las reglas, así que también se
recuperan de ahí: antes sobrevivía la norma escrita y desaparecía el código que la hace cumplir.
