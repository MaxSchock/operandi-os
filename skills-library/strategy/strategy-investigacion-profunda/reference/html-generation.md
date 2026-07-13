# Generación HTML estilo McKinsey

## Visión general

El informe se entrega en dos formatos:
1. **Markdown** — fuente de verdad, editable, versionable
2. **HTML estilo McKinsey** — visualización ejecutiva, listo para presentar

El HTML se genera automáticamente desde el MD usando `scripts/md_to_html.py`.

---

## Uso

```bash
python scripts/md_to_html.py projects/investigacion/<YYYY-MM-DD>/<tema-slug>/informe_*.md
# Genera informe_*.html en la misma carpeta
```

El script:
1. Lee el MD
2. Parsea frontmatter YAML (título, autor, fecha, modo)
3. Convierte Markdown a HTML con la librería `markdown` de Python
4. Inyecta el resultado en la plantilla `templates/mckinsey_report_template.html`
5. Genera tabla de contenidos automática desde los H2/H3
6. Procesa citas [N] como links anclados a la bibliografía
7. Guarda el HTML final

---

## Características de estilo

**Diseño:**
- Tipografía serif para títulos (estilo McKinsey/HBR)
- Tipografía sans-serif para cuerpo (legibilidad)
- Paleta sobria: negro/grises sobre blanco, acento azul oscuro para citas
- Sangrías y espaciado generosos
- Saltos de página CSS (`page-break-before`) para imprimir limpio

**Elementos especiales:**
- Resumen ejecutivo destacado con borde lateral
- Citas [1] convertidas en hipervínculos a la entrada de bibliografía
- Bibliografía con anclas de retorno (↩) a las menciones en cuerpo
- Tabla de contenidos colapsable
- Bloques de "Hallazgo" con numeración visual destacada

**Responsive:**
- Móvil: tipografía adaptada, TOC colapsado por defecto
- Imprimible: márgenes A4, sin elementos interactivos

---

## Plantilla

Ver `templates/mckinsey_report_template.html` para el HTML base. Variables disponibles:

| Variable | Descripción |
|----------|-------------|
| `{{TITLE}}` | Título del informe |
| `{{SUBTITLE}}` | Subtítulo opcional |
| `{{DATE}}` | Fecha de generación |
| `{{MODE}}` | Modo usado (quick/standard/deep/ultradeep) |
| `{{SOURCES_COUNT}}` | Número de fuentes |
| `{{WORD_COUNT}}` | Palabras totales |
| `{{TOC}}` | Tabla de contenidos generada |
| `{{CONTENT}}` | HTML del cuerpo |
| `{{GENERATED_AT}}` | Timestamp de generación |

---

## Verificación post-conversión

Después de generar HTML:

```bash
python scripts/verify_html.py projects/investigacion/<YYYY-MM-DD>/<tema-slug>/informe_*.html
```

**Comprueba:**
- HTML válido (sin etiquetas mal cerradas)
- Todas las citas en cuerpo enlazan a entrada de bibliografía
- Sin enlaces internos rotos
- TOC genera correctamente

---

## Personalización

Si el usuario pide una variación de estilo (corporativo distinto, paleta diferente), edita directamente `templates/mckinsey_report_template.html`. El CSS está embebido en `<style>` al inicio para que el HTML sea autocontenido y portable.
