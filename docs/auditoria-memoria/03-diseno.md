# Diseño: memoria que se activa sola y aprende sola

Objetivo de Max (27-08): *"que el sistema vaya aprendiendo solo y creando solo sus skills, y decida por su cuenta qué coger. Yo me quiero centrar en trabajar y olvidarme del setup."*

Eso exige cerrar un bucle que hoy está partido en dos sitios distintos.

## El bucle, hoy

```
Max corrige  →  [NADA]  →  Claude escribe la regla si Max lo pide  →  el fichero se queda quieto  →  Max vuelve a corregir
                  ↑                                                              ↑
            no se captura                                        nada la vuelve a leer
```

Los dos eslabones rotos están medidos: el motor de aprendizaje no lee lo que escribe Max (`02c-sinapsis.md`), y el 51% de los fallos ocurren con la regla ya escrita (`01-incidentes.md`).

## El bucle, propuesto

```
Max corrige → CAPTURA → DESTILADOR → ESCRITURA CON DESTINO → ACTIVACIÓN → GATE
                (ya existe)   (nuevo)        (nuevo)          (nuevo)    (ampliar)
                                    ↖                            ↙
                                      MEDICIÓN Y AUTO-AJUSTE (nuevo)
```

---

## 1 · Captura — ya existe, no hay que construirla

El hook `chat-hook-on-stop.sh` lleva desde mayo volcando cada sesión al vault (`_wiki/raw/chat-history/`, 322 chats). Esta auditoría se ha hecho con ese corpus. La materia prima estaba; lo que faltaba era alguien leyéndola.

**Acción:** ninguna. Se reutiliza.

## 2 · Destilador — el eslabón que no existe

Al cerrar cada sesión, un proceso lee los mensajes de Max de esa sesión y extrae los incidentes: qué corrigió, qué regla estaba detrás, si esa regla ya existía. Es exactamente el análisis de la Sesión 1, reducido a una sesión.

- **Dónde**: hook `Stop`, en segundo plano, sin bloquear el cierre.
- **Cómo**: `claude -p` en modo headless con el prompt de extracción ya validado hoy sobre 319 chats (596 incidentes, 6/6 en el spot-check). Devuelve JSON.
- **Coste**: una llamada barata por sesión. El detector actual de Sinapsis (`_session-learner.sh`, 447 líneas de heurísticas sobre secuencias de herramientas) queda sustituido: lleva meses devolviendo "no patterns" porque busca donde no está la señal.

## 3 · Escritura con destino — una regla sin trigger no se guarda

Hoy una regla nueva es un `.md` más en un cajón de 123, del que 62 ni siquiera están enlazados. A partir de ahora, al nacer, cada regla lleva:

```yaml
nivel: irrompible | contextual | referencia
trigger: cuándo debe aparecer (patrón sobre el prompt, el cliente o la herramienta)
estado: prueba | activa | archivada
reincidencias: 0
ultima_activacion: null
```

Sin `trigger` no se escribe: sería otra línea muerta. Antes de crear, el destilador busca la regla existente más parecida y **actualiza en vez de duplicar**.

Los tres niveles, con tratamiento distinto (hoy los 74 KB compiten todos al mismo nivel de prioridad, que es como no tener prioridades):

| Nivel | Cuántas | Dónde vive | Cómo llega |
|---|---|---|---|
| **Irrompible** | 5-8 | En contexto siempre | Además, gate técnico que bloquea |
| **Contextual** | ~70 | Fuera del contexto base | Inyectada por el activador cuando toca |
| **Referencia** | ~40 | Fuera del contexto base | Recuperada bajo demanda del índice |

## 4 · Activación — inyectar antes de razonar, no después

Todo lo que hay hoy cuelga de `PreToolUse`: llega cuando ya he decidido. El punto correcto es `UserPromptSubmit`, hoy sin usar en ninguno de los tres ficheros de configuración.

El activador, a partir del texto de Max y del cliente detectado, recupera del índice las reglas cuyo trigger casa y las inyecta antes de que yo empiece a pensar.

**Reutiliza lo que ya existe**: la base SQLite con FTS5 (`context/.memory-index/memory.db`) y su `ingest.py` funcionan. Hoy indexan 3 ficheros y 61 fragmentos porque nadie escribió el `corpus.yaml` real (solo está el `.example`). Ampliar el corpus a las 123 reglas, los 226 session-logs y el vault convierte una herramienta muerta en el motor del sistema.

## 5 · Gates — para lo que no puede depender de que me acuerde

55 de los 596 incidentes eran bloqueables por un hook. Son los caros: envíos, borrados, cruces de entidad. Ya existe el patrón (`~/.claude/hooks/guard-email-send.py`), solo hay que extenderlo:

| Gate | Qué bloquea | Incidentes que cubre |
|---|---|---|
| Envío externo | Enviar sin haber leído el hilo real en esta sesión; usar la cuenta de otra entidad | 32 posteriores a la regla, 12 graves |
| Borrado | `rm`, DELETE, DROP, vaciados sin backup con marca de tiempo previo | 3 posteriores, 3 graves |
| Deliverable | PDF a cliente sin copia en Downloads + Drive; documento en el idioma equivocado | parte de los 63 de deliverables |

Un gate no recuerda: impide. Es la diferencia entre las trece reglas que se repiten y la de secretos, que no se repite nunca.

## 6 · Medición y auto-ajuste — aquí está el "aprende solo"

Cada regla lleva su contador. El sistema se reordena solo con dos disparadores:

- **Una regla contextual que reincide 3 veces → sube a gate o a irrompible.** Si recordarla no funciona, deja de recordarse y pasa a bloquearse.
- **Una regla que no se activa en 60 días → baja a referencia; a los 120, se archiva.** Con backup, y sin borrar nada del histórico.

Esto es lo que hace que el sistema no engorde: hoy solo sabe añadir. La regla de olor del cierre de sesión ("si MEMORY.md pasa de 17 KB es que se usa como informe") pasa de ser un recordatorio que se ignora a una poda automática.

**Y es el antídoto contra el envenenamiento**: una regla mal destilada nace en estado `prueba`, no se activa, y se archiva sola a los 60 días. El coste de un error del destilador es cero.

## 7 · Skills que se crean solas

Distinto del bucle de reglas, y con el umbral más alto a propósito.

Cuando el destilador detecta que un **procedimiento de trabajo** (no una corrección) se ha repetido 3 o más veces en sesiones distintas — mismo objetivo, mismos pasos, mismo cliente — genera una skill en borrador en `.claude/skills/`, con los pasos reales extraídos de las sesiones donde se hizo. Se anuncia en el arranque siguiente en una línea; se usa desde el primer momento; si no se invoca en 90 días, se archiva sola.

Umbral alto porque una skill mala cuesta contexto en cada sesión, mientras que una regla mala en estado prueba no cuesta nada.

## Presupuesto de contexto

| | Hoy | Objetivo |
|---|---:|---:|
| `~/.claude/CLAUDE.md` | 37 KB | ~12 KB (identidad, irrompibles, rutas críticas) |
| `iamasters-os/CLAUDE.md` | 17 KB | ~8 KB |
| `MEMORY.md` | 19 KB | ~4 KB (índice real, no informe) |
| Inyección dinámica por turno | 0 | 1-3 KB, solo lo que aplica |
| **Total fijo** | **74 KB** | **~24 KB** |

Lo que sale del contexto fijo no se pierde: pasa a estar disponible bajo demanda, que es donde sirve.

## Orden de implementación

Por impacto medido, no por comodidad:

1. **Gates** (envío, borrado, deliverable) — cubren los 55 incidentes más caros y no dependen de nada más.
2. **Índice completo** — `corpus.yaml` real con las 123 reglas, session-logs y vault. Desbloquea el recall (73 incidentes).
3. **Activador `UserPromptSubmit`** — inyección contextual (75 incidentes) y la mayor parte de los 388 de "mejor razonamiento", que es donde muerde la sobrecarga.
4. **Destilador en `Stop`** — cierra el bucle de aprendizaje.
5. **Migración de las 123 reglas** a nivel + trigger, y poda de lo muerto (con backup).
6. **Medición y auto-ajuste**, y después la generación de skills.

## Verificación

1. **Replay**: 10 incidentes reales de causa "inyección" o "recall". Reproducir el prompt original en sesión limpia; la regla que faltó debe aparecer antes de mi primera acción. Éxito = 10/10.
2. **Gates**: cada uno probado intentando la acción prohibida contra un canario propio. Nunca contra un contacto real.
3. **Contexto**: medir tokens de arranque antes y después. Si no baja de 74 KB, el rediseño falló en su premisa.
4. **Bucle cerrado**: provocar una corrección en una sesión de prueba y comprobar que al día siguiente la regla existe, tiene trigger y se activa sin que nadie la escriba a mano.
5. **Reincidencia**: el contador queda en marcha. La métrica real se lee a las dos semanas.
