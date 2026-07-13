# Automatizaciones: cómo hacer que el OS trabaje solo

Esta guía es para miembros que usan iAmasters OS desde Claude Desktop o Claude Code y quieren dejar tareas repetitivas funcionando con menos fricción. No necesitas terminal para entenderla: piensa en rutinas, loops y compuertas humanas.

La idea no es automatizarlo todo desde el primer día. La idea es convertir primero las tareas repetibles en sistemas pequeños, verificables y con una pausa humana antes de cualquier acción sensible.

## Los 3 niveles de automatización

### 1. Dentro de una sesión

Usa `/loop <intervalo> <instrucción>` cuando quieres que Claude vigile algo mientras la sesión está abierta.

Ejemplos:

- `/loop 15min revisa si ya está listo el informe y resume cambios`
- `/loop 30min comprueba el estado del brief activo y avísame si falta input`
- `/loop 1h revisa esta carpeta de entregables y detecta nuevos archivos`

Este nivel sirve para vigilancia, polling y seguimiento temporal. Depende de que la sesión siga abierta.

### 2. Recurrente en tu Mac o PC

Usa las tareas programadas de la app de Claude cuando quieres que una instrucción se ejecute de forma recurrente en tu máquina.

Flujo genérico:

1. Abre la app de Claude.
2. Ve a `Routines`.
3. Crea una rutina nueva con `New routine`.
4. Elige ejecución local.
5. Escribe una instrucción clara.
6. Define horario y frecuencia.
7. Guarda la rutina.

La app debe estar abierta para que una rutina local pueda trabajar con archivos de tu máquina.

### 3. En la nube

Usa rutinas remotas cuando no quieres depender de tu ordenador.

Este nivel sirve para tareas sobre repositorios, webs o fuentes accesibles desde internet. No lo uses para tareas que necesiten archivos locales, carpetas privadas o contexto que solo vive en tu máquina.

Regla práctica: si la tarea necesita leer `context/`, `clients/`, `projects/` o archivos locales, empieza con rutina local.

## Qué automatizar primero

Empieza por loops con disparador programado que ya viven en `loops/`.

Antes de automatizar, lee la guía de diseño en [`docs/loop-engineering.md`](loop-engineering.md). Ahí está el criterio para pasar de "prompt suelto" a "sistema repetible".

Buenas primeras candidatas:

- Revisión semanal.
- Repaso de prioridades.
- Triaje de leads.
- Preparación de informes de cliente.
- Reciclaje semanal de contenido.

Evita empezar por publicación en redes, emails a clientes, cambios de precios, propuestas, contratos o producción. Todo eso requiere compuerta humana.

## Ejemplo: programar revisión semanal

Objetivo: cada viernes, Claude prepara la revisión semanal sin que tengas que acordarte.

### Paso 1 · Ejecuta el loop manualmente

Abre Claude y escribe:

```text
Corre el loop de revisión semanal.
```

Si el OS te pide contexto, responde lo mínimo necesario. Al terminar, revisa si el resultado es útil, concreto y accionable.

### Paso 2 · Evalúa el resultado

No lo automatices todavía si:

- Pide demasiadas aclaraciones.
- Mezcla prioridades viejas con nuevas.
- No distingue decisiones tomadas de asuntos pendientes.
- Te obliga a reescribir casi todo.

Primero ajusta el loop y vuelve a correrlo manualmente.

### Paso 3 · Crea la rutina

En la app:

1. `Routines`.
2. `New routine`.
3. Tipo local.
4. Horario: viernes por la mañana.
5. Instrucción:

```text
Corre el loop de revisión semanal de iAmasters OS. Usa el contexto del repo actual, revisa prioridades, decisiones y proyectos activos, y prepara un resumen para aprobación humana. No publiques ni envíes nada.
```

### Paso 4 · Revisa la primera ejecución automática

La primera vez, quédate cerca. Comprueba que leyó los archivos correctos, respetó las compuertas humanas, propuso acciones realistas y dejó claro qué requiere decisión tuya.

## Reglas de seguridad

Nunca programes nada que publique, envíe, facture, cambie credenciales o modifique datos de clientes sin compuerta humana.

Los 3 peajes obligatorios:

1. **Revisión humana** antes de publicar o enviar.
2. **Confirmación explícita** antes de modificar datos sensibles.
3. **Registro de decisión** cuando el cambio afecte a estrategia, cliente, precio, alcance o riesgo.

Empieza siempre con la versión manual del loop. Automatiza solo cuando el FPY aguante: si el primer resultado útil cae por debajo de lo aceptable, no es una rutina, es deuda operativa disfrazada.

## Plantilla de instrucción segura

```text
Ejecuta [nombre del loop].
Prepara el resultado en borrador.
No publiques, no envíes, no modifiques archivos críticos y no contactes con clientes.
Separa claramente:
- Hechos encontrados
- Propuesta de acción
- Decisiones que requieren aprobación humana
```
