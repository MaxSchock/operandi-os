# Metodología de Investigación Profunda: pipeline de 8 fases

## Visión general

Este documento contiene la metodología detallada para conducir investigación profunda. Las 8 fases representan un enfoque completo para recopilar, verificar y sintetizar información desde múltiples fuentes.

**Adaptación a Claude.ai:** Donde el repo original usa `search-cli` por Bash y subagentes Task, aquí se usa `web_search` (búsqueda principal) y `web_fetch` (lectura profunda de URLs). El paralelismo se simula con múltiples llamadas a `web_search` con queries distintas.

---

## Fase 1: SCOPE — Encuadre de la investigación

**Objetivo:** Definir límites y criterios de éxito.

**Actividades:**
1. Descomponer la pregunta en componentes nucleares
2. Identificar perspectivas de los interesados
3. Definir límites de alcance (qué entra, qué no)
4. Establecer criterios de éxito
5. Listar asunciones clave a validar

**Aplicación de razonamiento extendido:** Antes de comprometerte con el alcance, explora múltiples formulaciones de la pregunta. ¿Es realmente sobre X o el usuario quiere saber Y?

**Salida:** Documento de alcance estructurado con límites.

---

## Fase 2: PLAN — Formulación de estrategia

**Objetivo:** Crear una hoja de ruta de investigación inteligente.

**Actividades:**
1. Identificar fuentes primarias y secundarias probables
2. Mapear dependencias de conocimiento (qué hay que entender primero)
3. Crear estrategia de queries de búsqueda con variantes
4. Planificar enfoque de triangulación
5. Estimar tiempo/esfuerzo por fase
6. Definir controles de calidad

**Salida:** Plan de investigación con caminos priorizados.

---

## Fase 3: RETRIEVE — Recopilación de información

**Objetivo:** Recolectar sistemáticamente información de múltiples fuentes.

### Estrategia de descomposición de queries

Antes de lanzar búsquedas, descompón la pregunta de investigación en **5-10 ángulos independientes**:

1. **Tema central (búsqueda semántica)** — Exploración basada en significado del concepto principal
2. **Detalles técnicos (keyword)** — Términos específicos, APIs, implementaciones
3. **Desarrollos recientes (filtrado por fecha)** — Qué hay nuevo en los últimos 12-18 meses
4. **Fuentes académicas (dominio específico)** — Papers, investigación, análisis formal
5. **Perspectivas alternativas (comparación)** — Enfoques rivales, críticas
6. **Fuentes estadísticas/datos** — Evidencia cuantitativa, métricas, benchmarks
7. **Análisis industrial** — Aplicaciones comerciales, tendencias de mercado
8. **Análisis crítico/limitaciones** — Problemas conocidos, modos de fallo, casos límite

### Protocolo de ejecución

**Paso 0: Obtener la fecha actual**

Antes de CUALQUIER búsqueda, recupera la fecha de hoy ejecutando `date +%Y-%m-%d` en bash_tool. Usa el año devuelto para todas las queries filtradas por fecha y comprobaciones de recencia. **NO asumas un año de tus datos de entrenamiento.**

**Paso 1: Lanzar búsquedas (paralelismo lógico)**

En Claude.ai no hay subagentes, pero puedes lanzar múltiples `web_search` consecutivas en un mismo turno. Cada query debe atacar un ángulo distinto:

```
- web_search("estado quantum computing 2026")
- web_search("quantum computing limitaciones challenges")
- web_search("quantum computing aplicaciones comerciales")
- web_search("quantum vs classical comparison benchmarks")
- web_search("quantum error correction research papers")
- web_search("quantum computing inversión venture capital")
```

**Paso 2: Profundizar con `web_fetch`**

De los resultados de `web_search`, identifica las 5-15 URLs más prometedoras (alta credibilidad, contenido sustancial) y úsalas con `web_fetch` para obtener el contenido completo. Esto sustituye a los Task subagents del repo original.

**Paso 3: Recopilar y organizar resultados**

A medida que llegan resultados:
1. Extrae pasajes clave con metadatos de la fuente (título, URL, fecha, credibilidad)
2. Registra cada fuente y evidencia en `sources.json` y `evidence.json` (ver más abajo)
3. Rastrea lagunas de información que emerjan
4. Persigue tangentes prometedoras con búsquedas adicionales dirigidas
5. Mantén diversidad de fuentes (mezcla académicas, industria, prensa, docs técnicos)
6. Monitoriza el umbral de calidad (ver patrón FFS abajo)

### Persistencia de evidencia (CRÍTICO)

Después de cada lote de recuperación, persiste la evidencia inmediatamente usando los scripts:

```bash
# Registrar fuente (devuelve source_id estable basado en hash)
python scripts/citation_manager.py register-source \
  --json '{"raw_url": "https://...", "title": "...", "source_type": "academic", "year": "2025"}' \
  --dir [carpeta]

# Persistir cada cita literal de esa fuente
python scripts/citation_manager.py add-evidence \
  --json '{"source_id": "abc123...", "quote": "texto exacto", "evidence_type": "direct_quote", "locator": "página 5"}' \
  --dir [carpeta]
```

**La evidencia NO debe vivir solo en el contexto del modelo** — debe persistirse en `evidence.json` antes de que comience la síntesis. Esto permite trazabilidad y que la validación post-hoc pueda cruzar afirmaciones contra evidencia.

### Patrón First Finish Search (FFS)

**Compleción adaptativa basada en umbral de calidad:**

Procede a la Fase 4 cuando se alcance el PRIMER umbral:

- **Quick:** 10+ fuentes con credibilidad media >60/100 O 2 minutos transcurridos
- **Standard:** 15+ fuentes con credibilidad media >60/100 O 5 minutos transcurridos
- **Deep:** 25+ fuentes con credibilidad media >70/100 O 10 minutos transcurridos
- **UltraDeep:** 30+ fuentes con credibilidad media >75/100 O 15 minutos transcurridos

### Estándares de calidad

**Diversidad de fuentes (mínimo):**
- 3 tipos de fuente (académica, industria, prensa, docs técnicos)
- Diversidad temporal (recientes 12-18 meses + fundacionales más antiguas)
- Diversidad de perspectivas (defensores + críticos + análisis neutro)
- Diversidad geográfica (no solo fuentes anglosajonas; busca también en español, EU, etc.)

**Rastreo de credibilidad:**
- Puntúa cada fuente 0-100 con `scripts/source_evaluator.py`
- Marca fuentes de baja credibilidad (<40) para verificación adicional
- Prioriza fuentes de alta credibilidad (>80) para afirmaciones nucleares

---

## Fase 4: TRIANGULATE — Verificación cruzada

**Objetivo:** Validar información a través de múltiples fuentes independientes.

**Actividades:**
1. Identificar afirmaciones que requieren verificación
2. Cruzar hechos contra 3+ fuentes
3. Marcar contradicciones o incertidumbres
4. Evaluar credibilidad de cada fuente
5. Distinguir consenso vs. debate
6. Documentar estado de verificación por afirmación

**Independencia de fuentes:** Tres artículos que citan el mismo paper original NO son tres fuentes independientes — son uno. Cuenta clusters de evidencia, no número bruto de URLs.

**Salida:** Matriz de verificación con estado por afirmación.

---

## Fase 4.5: OUTLINE REFINEMENT — Refino del esquema

**Cuándo ejecutar:** Solo en Standard/Deep/UltraDeep (Quick lo salta). Después de la Fase 4, antes de la Fase 5.

**Actividades:**

1. **Revisar alcance inicial vs. hallazgos reales**
   - Compara el alcance de la Fase 1 con los descubrimientos de las Fases 3-4
   - Identifica patrones inesperados o contradicciones
   - Marca ángulos infraexplorados que emergieron como críticos
   - Marca áreas sobreexploradas que resultaron menos importantes

2. **Evaluar necesidad de adaptación del esquema**

   **Señales para adaptar (CUALQUIERA dispara refino):**
   - Los hallazgos principales contradicen las asunciones iniciales
   - La evidencia revela un ángulo más importante que el inicialmente planeado
   - Emergió un subtema crítico que no estaba en el plan original
   - La pregunta original era demasiado amplia/estrecha para la evidencia disponible

3. **Refinar el esquema (si es necesario)**

   Actualiza la estructura para reflejar la evidencia:
   - Añade secciones para hallazgos inesperados pero importantes
   - Degrada/elimina secciones con evidencia insuficiente
   - Reordena secciones según fuerza de evidencia e importancia

4. **Llenado dirigido de lagunas (si hay lagunas mayores)**

   Lanza 2-3 búsquedas dirigidas para los ángulos recién identificados. Recuperación rápida (no reinicies la Fase 3 entera). Tiempo máximo: 2-5 minutos.

5. **Documentar la justificación**

   En el anexo metodológico: qué cambió, por qué (razones basadas en evidencia), qué búsquedas adicionales se hicieron.

**Estándares:** La adaptación debe estar dirigida por evidencia (cita fuentes específicas que provocaron el cambio). No más del 50% de reestructuración (si necesitas más, el alcance original estaba muy mal calibrado).

**Anti-patrones:**
- ❌ NO adaptes el esquema por especulación o "lo que sería interesante"
- ❌ NO añadas secciones sin evidencia ya recopilada
- ❌ NO abandones completamente la pregunta de investigación original
- ✅ SÍ adapta cuando la evidencia indica claramente mejor estructura
- ✅ SÍ documenta la justificación

---

## Fase 5: SYNTHESIZE — Análisis profundo

**Objetivo:** Conectar insights y generar entendimiento novedoso (no solo resumir).

**Actividades:**
1. Identificar patrones a través de fuentes
2. Mapear relaciones entre conceptos
3. Generar insights que van más allá del material fuente
4. Crear marcos conceptuales
5. Construir estructuras argumentales
6. Desarrollar jerarquías de evidencia

**Distingue fact vs. synthesis claramente** en la redacción:
- HECHO (de fuente): "Smith et al. (2024) reportan reducción del 23% en mortalidad [1]"
- SÍNTESIS (tuya): "Este patrón sugiere un mecanismo subyacente común con..."

**Salida:** Entendimiento sintetizado con insights generados.

---

## Fase 6: CRITIQUE — Aseguramiento de calidad

**Objetivo:** Evaluar rigurosamente la calidad de la investigación.

**Preguntas red team:**
- ¿Qué falta?
- ¿Qué podría estar mal?
- ¿Qué explicaciones alternativas existen?
- ¿Qué sesgos podrían estar presentes?
- ¿Qué contrafactuales deberían considerarse?

**Crítica multi-persona (solo Deep/UltraDeep):**
Simula 2-3 personas críticas relevantes al tema:
- **"Profesional escéptico"** — ¿Se fiaría alguien que hace esto a diario de estos hallazgos?
- **"Revisor adversarial"** — ¿Qué rechazaría un peer reviewer?
- **"Ingeniero de implementación"** — ¿Se pueden ejecutar realmente estas recomendaciones?

**Bucle de retorno por laguna crítica:**

Si la crítica identifica una laguna de conocimiento crítica (no solo un problema de redacción), **vuelve a la Fase 3** con "delta-queries" dirigidas antes de pasar a la Fase 7. Tiempo máximo: 3-5 minutos. Esto previene publicar informes con puntos ciegos conocidos.

**Salida:** Informe de crítica con recomendaciones de mejora.

---

## Fase 7: REFINE — Mejora iterativa

**Objetivo:** Abordar lagunas y reforzar áreas débiles.

**Actividades:**
1. Investigación adicional para lagunas identificadas
2. Reforzar argumentos débiles
3. Añadir perspectivas faltantes
4. Resolver contradicciones
5. Mejorar claridad
6. Verificar contenido revisado

**Salida:** Investigación reforzada con deficiencias abordadas.

---

## Fase 8: PACKAGE — Generación del informe

**Objetivo:** Entregar investigación profesional y accionable.

Ver `reference/report-assembly.md` para el protocolo detallado de generación progresiva.

**Resumen:**
1. Estructurar el informe con jerarquía clara
2. Escribir resumen ejecutivo (200-400 palabras)
3. Desarrollar secciones detalladas (una por una, persistiendo a disco)
4. Crear visualizaciones (tablas, diagramas en Markdown)
5. Compilar bibliografía COMPLETA
6. Añadir anexo metodológico
7. Ejecutar validación (ver `reference/quality-gates.md`)
8. Convertir a HTML estilo McKinsey con `scripts/md_to_html.py`

**Salida:** Informe completo en MD + HTML listo para usar.

---

## Características avanzadas

### Razonamiento por grafos

En lugar de pensamiento lineal, ramifica en múltiples caminos:
- Explora encuadres alternativos en paralelo
- Persigue tangentes que podrían ser relevantes
- Fusiona insights de diferentes ramas
- Retrocede y revisa cuando emerge información nueva

### Control de profundidad adaptativo

Ajusta automáticamente la profundidad de la investigación según:
- Complejidad de la información
- Disponibilidad de fuentes
- Restricciones de tiempo
- Niveles de confianza

### Inteligencia de citas

Gestión inteligente de citas:
- Rastrea la procedencia de cada afirmación
- Enlaza al original
- Evalúa credibilidad de la fuente
- Maneja fuentes contradictorias
- Genera bibliografías apropiadas
