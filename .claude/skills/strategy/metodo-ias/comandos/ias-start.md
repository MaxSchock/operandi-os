---
description: "Abre una sesión diaria con el método I.A.S. Conduce el checklist H1 de Intención antes de ejecutar Acción."
argument-hint: "[descripción breve del activo a producir, opcional]"
---

# /ias-start

Activa el **modo diario** de la skill `metodo-ias` (Hipótesis 1: planificación previa exhaustiva).

## Qué hace

1. Lee el protocolo del modo diario en `protocolos/h1-planificacion.md`. Si el archivo no existe, avisa al usuario y para.
2. Lee la skill raíz `SKILL.md` para confirmar reglas anti-drift y formato de salida.
3. Ejecuta el checklist de la fase I tal como lo define `protocolos/h1-planificacion.md`. Verde/rojo por cada ítem. No avanza a A hasta que la I esté completa.
4. Registra el bloque de **decisiones congeladas** que el agente de fase A no puede reabrir.
5. Devuelve al usuario:
   - Resumen del checklist en chat.
   - Archivo `outputs/diarios/YYYY-MM-DD-{slug}.md` con la estructura de 8 secciones definida en `protocolos/h1-planificacion.md` (las 6 primeras rellenas al cerrar I; `resultado` y `lecciones` se completan al final de la sesión).
   - Si no hay carpeta `outputs/` en el cwd y no hay proyecto detectado, fallback a `~/.claude/ias-outputs/diarios/`.

## Argumento

`$ARGUMENTS` — descripción breve del activo a producir en esta sesión. Opcional. Si no llega, la skill lo pide en el primer paso del checklist.

## Reglas

- Español. Sin emojis. Código en inglés.
- No inventar inputs. Si falta un input, marcarlo como `[pendiente]` y pedirlo al usuario.
- No iniciar la fase A si quedan ítems en rojo en la fase I.
- Decisiones congeladas son inmutables durante A. Si el agente intenta reabrir una, la skill bloquea y avisa.

## Tono al conducir al usuario

La mecánica interna (gate verde/rojo, 6 dimensiones, 8 secciones, paths del repo, contrato H1↔H2) es jerga del manual. **No sale nunca al chat.** Quien usa la skill ve una conversación humana, no un protocolo.

- **Primer mensaje:** una frase corta que aporta valor o pide lo mínimo necesario para aportarlo. Nunca "modo activado", "soy el protocolo", "voy a conducirte por...".
- **Repreguntas:** como una persona experta. Si una respuesta es vaga, repreguntar concretamente, no anunciar "esto es rojo, falla la dimensión 3".
- **Sin acrónimos internos** (H1, fase I, fase A, gate, slug) en lo que ve el usuario.
- **Sin paths del repo** en chat. El archivo se escribe; el path se nombra al final cuando se confirma que está hecho.
- Las reglas duras se aplican **silenciosamente**. El usuario percibe el resultado (no se avanza hasta que está claro), no el mecanismo.

Ejemplo correcto de arranque: *"Antes de meterte con el agente, dime qué vas a producir hoy. El entregable concreto, para quién y cuándo. Eso te ahorra que la IA te pregunte 15 detalles a mitad de la sesión."*

Ejemplo incorrecto: *"Activado /ias-start. Modo diario H1. Te conduzco por el checklist verde/rojo de 6 dimensiones. Regla dura: un solo rojo bloquea el paso a A."*

## Salida esperada

Un archivo `outputs/diarios/YYYY-MM-DD-{slug}.md` y un resumen en chat de máximo 8 líneas con el estado del checklist y las decisiones congeladas. La fase A se ejecuta a continuación dentro de la misma sesión, registrando incidencias en el mismo archivo. La fase S se cierra al final de la sesión y queda lista para que `/ias-recap` la lea al final de la semana.
