---
title: "[Tema del informe]"
subtitle: "Investigación profunda"
date: "[YYYY-MM-DD]"
mode: "[quick|standard|deep|ultradeep]"
author: "investigacion-profunda"
---

<!--
ESTRATEGIA DE ENSAMBLAJE PROGRESIVO

Este informe se genera sección por sección con `create_file` (primera)
y `str_replace` (siguientes). Cada generación: ≤2.000 palabras.

POR QUÉ: Maneja límites de tokens de salida manteniendo calidad por sección.
RESULTADO: Informes de hasta ~20.000 palabras por ejecución.

ESTÁNDARES DE ESCRITURA (aplicar a CADA sección):
- PRECISIÓN: cada palabra elegida con intención
- ECONOMÍA: sin relleno, sin gramática rebuscada
- CLARIDAD: números exactos en frases ("23% reducción", no "mejoró significativamente")
- DIRECTO: declara hallazgos sin adornos
- ALTA SEÑAL: información densa, respeta al lector

ATRIBUCIÓN (CRÍTICO - PREVIENE FABRICACIÓN):
- TODA afirmación factual seguida por [N] en la misma frase
- Usar "Según [1]..." o "[1] reporta..."
- DISTINGUIR hecho de síntesis:
  ✅ "La mortalidad descendió 23% (p<0,01) en el grupo de tratamiento [1]."
  ❌ "Los estudios muestran que la mortalidad mejoró significativamente."
- SIN atribuciones vagas ("la investigación sugiere", "los expertos creen")
- ADMITIR incertidumbre: "No se encontraron fuentes para X" en vez de fabricar

ANTI-TRUNCAMIENTO:
- ❌ PROHIBIDO: "Contenido continúa...", "Debido a la longitud...", "[Secciones X-Y...]"
- ✅ REQUERIDO: Genera la sección COMPLETAMENTE
- El ensamblaje progresivo maneja longitud ilimitada
-->

## Resumen ejecutivo

[200-400 palabras. Síntesis de hallazgos clave, implicaciones, recomendaciones principales. Densa en datos, sin viñetas. Debe poder leerse de forma autónoma.]

## Introducción

[400-800 palabras. Establece contexto, alcance, audiencia, asunciones, metodología en alto nivel. Por qué importa este tema ahora.]

### Alcance

[Qué entra, qué no, por qué.]

### Asunciones

[Cualquier asunción de alto impacto hecha explícita aquí, no escondida.]

## Hallazgo 1: [Título descriptivo]

[600-2.000 palabras. Prosa primero (≥80%). Citas inmediatas [N]. Evidencia específica con cifras y fechas. Distinguir hecho de síntesis.]

## Hallazgo 2: [Título descriptivo]

[Igual que Hallazgo 1.]

## Hallazgo N: [Título descriptivo]

[Tantos hallazgos como la investigación justifique. Mínimo 4, máximo 8 típicamente.]

## Síntesis e implicaciones

[Insights que van MÁS ALLÁ del material fuente. Patrones, conexiones, implicaciones de segundo orden. Esta es la sección donde tu análisis aporta valor sobre y por encima de simplemente recopilar fuentes.]

## Limitaciones y caveats

[Honestidad intelectual: dónde es débil la evidencia, qué no se pudo verificar, qué sesgos podrían afectar al análisis, qué preguntas quedan abiertas.]

## Recomendaciones

[Acciones concretas, próximos pasos, investigación pendiente. Si el informe es para decisión, deja claro qué decisión recomienda y por qué.]

## Bibliografía

[CRÍTICO: TODA cita usada en el cuerpo aparece aquí, formateada:
[N] Autor/Org (Año). "Título". Publicación. URL (Recuperado: YYYY-MM-DD)

Sin marcadores, sin rangos, sin truncamientos. Cada entrada en su propia línea.]

## Anexo metodológico

### Modo y configuración

[Modo usado, fases ejecutadas, número de búsquedas, número de fuentes consultadas vs. citadas.]

### Estrategia de búsqueda

[Queries usadas, ángulos cubiertos, motores consultados.]

### Triangulación

[Cómo se verificaron afirmaciones contra múltiples fuentes independientes.]

### Adaptaciones del esquema

[Si la Fase 4.5 modificó el esquema, documentar qué cambió y por qué.]

### Bucles de crítica (si Deep/UltraDeep)

[Qué identificó la crítica, qué delta-búsquedas se hicieron, qué se reforzó.]

### Validación

[Resultado de validate_report.py y verify_citations.py.]
