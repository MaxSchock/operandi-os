# Ensamblaje del Informe: Generación Progresiva

## Requisitos de longitud por modo

| Modo | Palabras objetivo | Descripción |
|------|-------------------|-------------|
| Quick | 2.000-4.000 | Umbral de calidad base |
| Standard | 4.000-8.000 | Análisis comprehensivo |
| Deep | 8.000-15.000 | Investigación exhaustiva |
| UltraDeep | 15.000-20.000+ | Rigor máximo |

---

## Salvaguardas de tokens de salida

**Límite práctico en Claude.ai:** ~20.000 palabras totales por ejecución antes de empezar a saturar el contexto.

**Estrategia:**
- Objetivo ≤20.000 palabras totales
- Cada generación individual (cada llamada a `create_file` o `str_replace`) ≤2.000 palabras
- Reportes >20.000 palabras requieren múltiples ejecuciones de la skill

---

## Generación progresiva por secciones

**Estrategia central:** Genera y escribe cada sección individualmente con `create_file` (primera sección) y `str_replace` (siguientes). Esto permite informes de longitud ilimitada manteniendo cada generación manejable.

### Fase 8.1: Setup inicial

```bash
# Inicializar el run con el citation_manager
python scripts/citation_manager.py init-run \
  --out-dir projects/investigacion/<YYYY-MM-DD>/<tema-slug> \
  --query "[pregunta de investigación]" \
  --mode [quick|standard|deep|ultradeep]
# Crea: run_manifest.json, sources.json, evidence.json, claims.json
```

### Fase 8.2: Registro de fuentes

A medida que encuentres fuentes durante la Fase 3:

```bash
python scripts/citation_manager.py register-source \
  --json '{"raw_url": "https://...", "title": "Título del artículo", "source_type": "academic", "year": "2025", "author": "Apellido et al."}' \
  --dir projects/investigacion/<YYYY-MM-DD>/<tema-slug>
# Devuelve source_id estable (hash sha256). Sobrevive a renumeraciones.
```

### Fase 8.3: Asignación de números de cita

Después de registrar TODAS las fuentes (al final de la Fase 4 o tras la 4.5):

```bash
python scripts/citation_manager.py assign-display-numbers \
  --dir projects/investigacion/<YYYY-MM-DD>/<tema-slug>
# Mapea source_ids estables a [1], [2], [3]... para renderizar
```

La identidad de las fuentes es estable a lo largo de ediciones. Los números de display se derivan en tiempo de render, nunca se almacenan en estado. Esto permite continuaciones sin romper la numeración.

### Fase 8.4: Bucle de generación de secciones

**Patrón:** Generar sección → escribir/append a archivo → siguiente sección.
Cada llamada contiene UNA sección (≤2.000 palabras).

**Secuencia obligatoria:**

1. **Resumen ejecutivo** (200-400 palabras)
   - Tool: `create_file` con frontmatter YAML + Resumen Ejecutivo
   - Rastrea citas usadas

2. **Introducción** (400-800 palabras)
   - Tool: `str_replace` para añadir
   - Alcance, metodología, asunciones declaradas

3. **Hallazgo 1 a N** (600-2.000 palabras cada uno)
   - Tool: `str_replace` para añadir
   - Una llamada por hallazgo
   - Cada hallazgo: prosa primero (≥80%), citas inmediatas [N]

4. **Síntesis e implicaciones**
   - Insights propios MÁS ALLÁ de lo que dicen las fuentes
   - Marca claramente: "Esto sugiere..." (síntesis) vs. "[1] reporta..." (hecho)

5. **Limitaciones y caveats**
   - Contraevidencia, lagunas, incertidumbres
   - Honestidad intelectual

6. **Recomendaciones**
   - Acciones inmediatas, próximos pasos, investigación pendiente

7. **Bibliografía** (CRÍTICO)
   - TODA cita del citations_used
   - SIN rangos, SIN marcadores, SIN truncamiento
   - Formato: `[N] Autor/Org (Año). "Título". Publicación. URL (Recuperado: Fecha)`

8. **Anexo metodológico**
   - Proceso de investigación, fases ejecutadas, enfoque de verificación
   - Cualquier adaptación de esquema documentada

---

## Organización de archivos

**1. Carpeta dedicada:**
- Ubicación: `projects/investigacion/<YYYY-MM-DD>/<tema-slug>/`
- Nombre limpio (sin caracteres especiales, usa guiones bajos)

**2. Convención de nombres:**
Todos los archivos comparten base:
- `informe_20260525_quantum_computing.md`
- `informe_20260525_quantum_computing.html`

**3. Artefactos auxiliares en la misma carpeta:**
- `sources.json` — registro de fuentes
- `evidence.json` — evidencias persistidas
- `claims.json` — afirmaciones atómicas
- `run_manifest.json` — manifiesto de la ejecución

---

## Palabras por sección

**CRÍTICO:** Ninguna llamada individual a `str_replace` o `create_file` debe exceder ~2.000 palabras.

Ejemplo: 10 hallazgos × 1.500 palabras = 15.000 palabras totales
- Cada llamada: 1.500 palabras (bajo el límite)
- Archivo crece a 15.000 palabras
- Ninguna llamada individual excede límites

---

## Conversión a HTML

Una vez completo el MD y validado:

```bash
python scripts/md_to_html.py projects/investigacion/<YYYY-MM-DD>/<tema-slug>/informe_*.md
# Genera informe_*.html en la misma carpeta con estilo McKinsey
```

Ver `reference/html-generation.md` para detalles del estilo.

---

## Presentación final al usuario

Al finalizar, usa `present_files` con la lista de archivos generados:

```
present_files([
  "projects/investigacion/<YYYY-MM-DD>/<tema-slug>/informe_*.html",  # primero el HTML (más visual)
  "projects/investigacion/<YYYY-MM-DD>/<tema-slug>/informe_*.md",
  "projects/investigacion/<YYYY-MM-DD>/<tema-slug>/sources.json",
  "projects/investigacion/<YYYY-MM-DD>/<tema-slug>/evidence.json"
])
```

Da un resumen breve al usuario: tema, modo, número de fuentes, palabras totales, hallazgos clave (1-2 líneas). Sin postámbulo extenso — el usuario abrirá el HTML para leerlo.
