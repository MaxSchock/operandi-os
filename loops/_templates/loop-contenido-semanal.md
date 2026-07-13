# Plantilla · Contenido semanal

Automatiza la conversión de una clase, vídeo, post largo o transcripción en 5-8 piezas
multiplataforma listas para revisión. Pensada para operadores, formadores, agencias y
creadores que publican cada semana. Tiempo estimado de personalización: 10 minutos.

```text
LOOP CANVAS — contenido semanal            v1.0 · [PERSONALIZA: fecha de creación] · Diseñado por: [PERSONALIZA: usuario] + Claude

1 · OBJETIVO Y "HECHO"
   Produce: 5-8 piezas multiplataforma listas para revisar a partir de 1 contenido fuente semanal.
   Hecho cuando: cada pieza pasa `tool-output-verifier` con score ≥7, respeta el register del `brand-context/voice/voice-profile.md`, tiene CTA y queda empaquetada en `projects/contenido/<fecha>/`.

2 · DISPARADOR
   [x] Manual por lote ("procesa la cola")
   [x] Programado: lunes a primera hora vía tarea programada de Claude Desktop [PERSONALIZA: hora exacta]
   [ ] Por evento: [PERSONALIZA: nueva fuente añadida a la cola, si aplica]

3 · COLA DE ENTRADA
   Vive en: `loops/contenido-semanal/cola.md`
   Un item está LISTO cuando tiene: URL, transcripción o ruta accesible + plataformas destino marcadas + register de voz elegido [PERSONALIZA: A/B/C].

4 · ESTACIONES (3–7, en orden)
   E1 Ingesta y desglose : fuente semanal → ideas atómicas con citas o marcas de origen
   E2 Mapeo de formatos : ideas atómicas → idea + formato + plataforma usando `marketing-content-repurposing`
   E3 Redacción por pieza : mapa de piezas + voice profile → borrador por plataforma usando `marketing-copywriting`
   E4 Humanización : piezas con score <7 → versión ajustada usando `tool-humanizer`
   E5 Verificación : piezas redactadas → checklist y score usando `tool-output-verifier`
   E6 Empaquetado : piezas verificadas → carpeta `projects/contenido/<fecha>/` + línea de estado por pieza

5 · OPERARIO POR ESTACIÓN
   E1 → Claude con la fuente accesible y contexto del OS
   E2 → skill `marketing-content-repurposing`
   E3 → skill `marketing-copywriting`
   E4 → skill `tool-humanizer`
   E5 → skill `tool-output-verifier`
   E6 → Claude
   Checker de E3 → `tool-output-verifier`, separado de `marketing-copywriting`.

6 · VERIFICACIÓN AUTOMÁTICA (el checklist, máx. 5 criterios binarios)
   ☐ La pieza coincide con el register elegido del voice profile
   ☐ La longitud cumple el límite de la plataforma destino
   ☐ No hay datos, cifras, promesas ni citas inventadas
   ☐ Hay CTA concreto y coherente con la plataforma
   ☐ Score humanizer/verifier ≥7
   Auto-corrección: máx. 3 intentos antes de escalar.

7 · COMPUERTAS HUMANAS
   Estación E5 → nivel A1 — el usuario aprueba antes de publicar o programar cualquier pieza.
   Estación E3 → nivel A1 inicial; puede proponerse A2 tras 10 piezas seguidas limpias.
   Innegociables (siempre humanas): salida a cliente · dinero · irreversibles · compromisos · publicación con marca.
   [PERSONALIZA: otras compuertas propias de tu CONFIG]

8 · CONDICIONES DE PARADA
   Presupuesto por item: máx. 3 autocorrecciones por pieza o 45 minutos por fuente.
   Escala al usuario si: fuente ilegible · plataforma destino no marcada · conflicto con voice profile · dato no verificable.
   Kill switch: "pausa el loop de contenido semanal" → no se procesa ninguna fuente nueva y lo abierto queda congelado.

9 · MÉTRICAS Y APRENDIZAJE
   Se mide: first-pass yield · retrabajo · tiempo de ciclo por pieza · escalaciones · reglas/semana
   Estado del loop vive en: `loops/contenido-semanal/loop-state.md`
   Reglas aprendidas viven en: `loops/contenido-semanal/REGLAS.md` (toda corrección del usuario → regla numerada)
   Revisión: semanal, 15 min — [PERSONALIZA: día y hora]
```

## Primer lote piloto

Procesa 3 fuentes o 3 piezas derivadas en A1. Observa: qué piezas pasan a la primera, dónde
aparecen inventos o desajustes de voz, cuánto tarda cada pieza y qué correcciones del usuario
se repiten para convertirlas en reglas.
