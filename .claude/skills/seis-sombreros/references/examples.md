# Ejemplos de aplicación

## Ejemplo 1 — Feature de producto (con anti-ancla + agentes paralelos)

**Input del usuario:** "Estoy decidiendo si añadir comentarios en hilo a mi SaaS de dietistas. Mis usuarios me lo piden, creo que es lo mejor."

### 🛡️ Fase 0 — Anti-Ancla

**Detección:** el usuario dice "creo que es lo mejor". Viene anclado en "sí, hay que hacerlo". Señal clara.

**Re-formulación pura:** "Tengo un SaaS de gestión de dietistas con 23 usuarios activos. 4 han pedido funcionalidad colaborativa. Necesito decidir cómo (o si) mejorar la comunicación dentro de la plataforma."

**Asunción fundacional:** "Los usuarios que piden features son representativos de la base total." Test de falsación: sería falso si los 4 son power users y los 19 restantes ni usan la mitad de las features actuales.

**Steel-man del opuesto:** "No añadir nada y dedicar esas 6 semanas a conseguir 20 usuarios más. Con 23 usuarios, cualquier feature nueva es optimización prematura. El problema real no es retención, es adquisición."

---

### Sombreros (ejecutados en paralelo, cada uno sin ver a los demás)

### ⚪ Blanco
**Verificados:** 4 peticiones sobre 23 usuarios activos (17%), no hay competidor con esta función, equipo de 1 dev.
**No verificados:** "aumentaría la retención" (sin datos), "todos lo quieren" (solo 4 de 23).
**Vacíos:** tiempo real de desarrollo, disposición a pagar más, churn actual.

### 🟡 Amarillo
1. Retención por engagement social — plausible: las features colaborativas aumentan uso diario en SaaS B2B.
2. Diferenciación competitiva — plausible: nadie en el nicho lo tiene.
3. Datos orgánicos — plausible: los hilos generan contenido aprovechable para recomendaciones.

### ⚫ Negro
1. Moderación legal — Alto/Alto — datos de salud son RGPD categoría especial, obligación de moderar contenido.
2. Scope creep — Alto/Alto — comentarios arrastran notificaciones, menciones, edición, borrado, reportes: 6-8 semanas mínimo.
3. Señal débil — Medio/Medio — 4/23 es 17%, muestra demasiado pequeña para decidir.
4. Coste de oportunidad — Alto/Alto — 6 semanas sin captar nuevos usuarios con solo 23 activos.

### 🟢 Verde
**Alt 1 — Canal externo** *(Marco: J-Eliminación)* — Slack/Discord gestionado por ti, coste cero, 1 hora. Insight: elimina el problema técnico por completo.
**Alt 2 — Mensajes 1:1 dietista↔paciente** *(Marco: E-SCAMPER/Eliminar)* — Sin hilo público, sin moderación legal, 1 semana. Insight: cubre la necesidad real sin el riesgo regulatorio.
**Alt 3 — Encuesta primero** *(Marco: D-Primeros principios)* — Antes de construir, validar con los 23 si pagarían más. Insight: la verdad irreductible es que no sabes si esto genera revenue.
**Alt 4 — Provocación: el SaaS sin pantalla** *(Marco: G-Random concept: "teléfono")* — ¿Y si la comunicación fuera por audio/voz integrado en vez de texto? Insight: los dietistas prefieren hablar, no escribir.
**Alt 5 — Doble down en adquisición** *(Marco: A-Inversión)* — ¿Qué garantizaría fracasar? Seguir añadiendo features para 23 usuarios. Insight: invertir las 6 semanas en marketing/ventas.

### 🔴 Rojo
- Esto huele a complacer a los más ruidosos.
- Entusiasmo por la Alt 2 (mensajes 1:1).
- "Todos lo piden" suena a excusa para no hacer lo incómodo: vender.
- Cansancio anticipado de leer "moderación RGPD".

### 🔵 Azul (síntesis)

**Mapa:** 4 usuarios sobre 23 piden feature compleja, sin datos de retención, riesgo legal alto, scope grande para un dev solo, coste de oportunidad crítico.

**Tensiones:** Amarillo vende diferenciación pero Negro la desmonta con coste real. Rojo confirma entusiasmo por alternativa más pequeña.

**Matriz:**

| Alternativa | Tiempo dev | Riesgo legal | Revenue potencial | Trade-off |
|---|---|---|---|---|
| Alt 1 (Slack) | Alto | Alto | Bajo | Sin control, fragmenta la experiencia |
| Alt 2 (1:1) | Alto | Alto | Medio | Cubre necesidad sin riesgo, pero no diferencia |
| Alt 3 (Encuesta) | Alto | Alto | Alto | Retrasa decisión, pero la basa en datos |
| Alt 5 (Adquisición) | N/A | Alto | Alto | Ignora petición de usuarios actuales |

**Recomendación:** Alt 3 (encuesta) esta semana + Alt 2 (mensajes 1:1) si la encuesta confirma demanda. Coste total: 1 semana.
**Plan B:** si la encuesta muestra <30% interés, pivotar a Alt 5 (adquisición pura).
**Métrica de revisión:** en 3 meses, si base supera 100 usuarios y >30% pide discusión grupal, reconsiderar hilos.

---

## Ejemplo 2 — Conflicto de equipo (resumen)

**Input:** "Mi colaborador no entregó a tiempo y me echa la culpa delante del cliente."
**Variante:** 3 (conflicto → Rojo primero)

Fase 0 detecta ancla en "quiero cortar la relación". Re-formula: "Necesito decidir cómo gestionar un incumplimiento de un colaborador que ha escalado públicamente."

Los 6 agentes operan en paralelo. El Rojo (ejecutado primero en la presentación pero en paralelo en la ejecución) captura rabia, traición y vergüenza sin justificaciones. El Blanco recoge fechas y mensajes. El Verde genera opciones desde conversación privada hasta salida limpia con cliente intacto.

Síntesis: conversación privada en 24h con 3 puntos preparados por escrito. Si no hay reconocimiento, salida ordenada en 48h.
