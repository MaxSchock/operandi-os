#!/usr/bin/env python3
"""
Markdown → HTML estilo McKinsey

Convierte el informe MD a un HTML autocontenido con:
- Tipografía editorial (serif para títulos, sans para cuerpo)
- TOC autogenerado
- Citas [N] enlazadas a bibliografía
- Estilo imprimible
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    print("❌ Falta dependencia: pip install markdown", file=sys.stderr)
    sys.exit(2)


HTML_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "mckinsey_report_template.html"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extrae frontmatter YAML simple del MD."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    body = content[end + 3 :].lstrip("\n")

    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def build_toc(html_body: str) -> str:
    """Genera tabla de contenidos desde los H2 y H3."""
    headings = re.findall(
        r'<h([23])\s+id="([^"]+)">([^<]+)</h\1>', html_body
    )
    if not headings:
        return ""

    items = []
    for level, anchor, text in headings:
        cls = f"toc-h{level}"
        items.append(f'<li class="{cls}"><a href="#{anchor}">{text}</a></li>')
    return f'<nav class="toc"><h2>Índice</h2><ul>{"".join(items)}</ul></nav>'


def link_citations(html_body: str) -> str:
    """Convierte [N] en enlaces ancla a la bibliografía."""
    def replace(match):
        n = match.group(1)
        return f'<sup class="citation"><a href="#ref-{n}">[{n}]</a></sup>'

    # Solo procesar fuera de la bibliografía
    bib_match = re.search(r'<h2\s+id="bibliograf', html_body, re.IGNORECASE)
    if bib_match:
        body_part = html_body[: bib_match.start()]
        bib_part = html_body[bib_match.start():]
        body_part = re.sub(r"\[(\d+)\]", replace, body_part)

        # Separar bibliografía en párrafos individuales (estaba como un <p> con <br/>)
        # Buscar el bloque <p>...</p> que sigue al h2 de Bibliografía
        bib_part = re.sub(
            r'(<h2[^>]*>Bibliograf[íi]a</h2>)\s*<p[^>]*>(.*?)</p>',
            lambda m: m.group(1) + _split_bibliography(m.group(2)),
            bib_part,
            flags=re.DOTALL | re.IGNORECASE,
        )
        return body_part + bib_part
    return re.sub(r"\[(\d+)\]", replace, html_body)


def _split_bibliography(bib_html: str) -> str:
    """Convierte el bloque concatenado de bibliografía en <p id="ref-N"> individuales."""
    # Limpiar <br/> y dividir por entrada [N]
    text = re.sub(r"<br\s*/?>", "\n", bib_html)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    paragraphs = []
    for line in lines:
        m = re.match(r"\[(\d+)\]\s*(.*)", line)
        if m:
            n = m.group(1)
            paragraphs.append(f'<p id="ref-{n}">[{n}] {m.group(2)}</p>')
        else:
            # Línea continuación, anexar al párrafo previo
            if paragraphs:
                paragraphs[-1] = paragraphs[-1][:-4] + f" {line}</p>"
    return "\n".join(paragraphs)


def slugify_headings(html_body: str) -> str:
    """Añade id="..." a cada h2/h3 para enlaces internos."""
    def add_id(match):
        level = match.group(1)
        text = match.group(2)
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        return f'<h{level} id="{slug}">{text}</h{level}>'

    return re.sub(r"<h([23])>([^<]+)</h\1>", add_id, html_body)


DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<style>
  :root {
    --ink: #1a1a1a;
    --ink-soft: #444;
    --accent: #003a5d;
    --accent-soft: #5b8db2;
    --bg: #ffffff;
    --rule: #d8d8d8;
    --highlight-bg: #f5f1e8;
  }
  * { box-sizing: border-box; }
  body {
    font-family: "Georgia", "Source Serif Pro", serif;
    color: var(--ink);
    background: var(--bg);
    max-width: 820px;
    margin: 0 auto;
    padding: 60px 40px;
    line-height: 1.7;
    font-size: 17px;
  }
  header.cover {
    border-bottom: 3px double var(--accent);
    padding-bottom: 30px;
    margin-bottom: 40px;
  }
  header.cover h1 {
    font-size: 2.4em;
    margin: 0 0 10px;
    color: var(--accent);
    letter-spacing: -0.5px;
  }
  header.cover .meta {
    color: var(--ink-soft);
    font-family: "Helvetica Neue", "Arial", sans-serif;
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }
  h2 {
    font-family: "Helvetica Neue", "Arial", sans-serif;
    color: var(--accent);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin-top: 50px;
    font-size: 1.6em;
    font-weight: 600;
  }
  h3 {
    font-family: "Helvetica Neue", "Arial", sans-serif;
    color: var(--ink);
    margin-top: 35px;
    font-size: 1.2em;
    font-weight: 600;
  }
  p { margin: 1em 0; text-align: justify; }
  blockquote {
    border-left: 4px solid var(--accent);
    margin: 1.5em 0;
    padding: 0.5em 1.5em;
    background: var(--highlight-bg);
    font-style: italic;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.5em 0;
    font-size: 0.95em;
  }
  th, td {
    border: 1px solid var(--rule);
    padding: 10px 14px;
    text-align: left;
  }
  th {
    background: var(--accent);
    color: white;
    font-family: "Helvetica Neue", "Arial", sans-serif;
    font-weight: 600;
  }
  tr:nth-child(even) { background: #fafafa; }
  code {
    font-family: "SF Mono", "Monaco", monospace;
    background: #f0ede5;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.9em;
  }
  pre {
    background: #f0ede5;
    padding: 16px;
    border-radius: 5px;
    overflow-x: auto;
  }
  sup.citation a {
    color: var(--accent);
    text-decoration: none;
    font-weight: bold;
    padding: 0 2px;
  }
  sup.citation a:hover { text-decoration: underline; }
  nav.toc {
    background: #f9f7f1;
    border: 1px solid var(--rule);
    border-radius: 4px;
    padding: 20px 30px;
    margin: 30px 0;
    font-family: "Helvetica Neue", "Arial", sans-serif;
    font-size: 0.95em;
  }
  nav.toc h2 {
    margin-top: 0;
    border: none;
    padding: 0;
    font-size: 1.2em;
  }
  nav.toc ul { list-style: none; padding-left: 0; }
  nav.toc li { margin: 4px 0; }
  nav.toc li.toc-h3 { padding-left: 20px; font-size: 0.92em; color: var(--ink-soft); }
  nav.toc a { color: var(--accent); text-decoration: none; }
  nav.toc a:hover { text-decoration: underline; }
  .executive-summary {
    background: var(--highlight-bg);
    border-left: 5px solid var(--accent);
    padding: 25px 30px;
    margin: 30px 0;
  }
  footer {
    margin-top: 60px;
    padding-top: 20px;
    border-top: 1px solid var(--rule);
    color: var(--ink-soft);
    font-size: 0.85em;
    font-family: "Helvetica Neue", "Arial", sans-serif;
    text-align: center;
  }
  @media print {
    body { padding: 0; max-width: 100%; font-size: 11pt; }
    h2 { page-break-after: avoid; }
    nav.toc { page-break-after: always; }
    sup.citation a { color: var(--accent); }
  }
  @media (max-width: 600px) {
    body { padding: 30px 20px; font-size: 16px; }
    header.cover h1 { font-size: 1.8em; }
  }
</style>
</head>
<body>
<header class="cover">
  <h1>{{TITLE}}</h1>
  <p class="meta">{{SUBTITLE}} · {{DATE}} · Modo: {{MODE}} · {{SOURCES_COUNT}} fuentes · {{WORD_COUNT}} palabras</p>
</header>
{{TOC}}
<main>
{{CONTENT}}
</main>
<footer>
  Generado por la skill <strong>investigacion-profunda</strong> · {{GENERATED_AT}}
</footer>
</body>
</html>
"""


def convert(md_path: Path) -> Path:
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    fm, body_md = parse_frontmatter(content)

    md = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br"])
    html_body = md.convert(body_md)
    html_body = slugify_headings(html_body)
    html_body = link_citations(html_body)

    # Destacar resumen ejecutivo
    html_body = re.sub(
        r'(<h2[^>]*>Resumen ejecutivo</h2>)(.*?)(?=<h2)',
        r'\1<div class="executive-summary">\2</div>',
        html_body,
        flags=re.DOTALL | re.IGNORECASE,
    )

    toc = build_toc(html_body)
    word_count = len(body_md.split())
    sources_count = len(set(re.findall(r"\[(\d+)\]", body_md)))

    title = fm.get("title", md_path.stem.replace("_", " ").title())
    subtitle = fm.get("subtitle", "Informe de investigación")
    date = fm.get("date", datetime.now().strftime("%Y-%m-%d"))
    mode = fm.get("mode", "standard")

    # Cargar plantilla externa si existe, si no usar la embebida
    if HTML_TEMPLATE_PATH.exists():
        with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        template = DEFAULT_TEMPLATE

    output_html = (
        template
        .replace("{{TITLE}}", title)
        .replace("{{SUBTITLE}}", subtitle)
        .replace("{{DATE}}", date)
        .replace("{{MODE}}", mode)
        .replace("{{SOURCES_COUNT}}", str(sources_count))
        .replace("{{WORD_COUNT}}", f"{word_count:,}")
        .replace("{{TOC}}", toc)
        .replace("{{CONTENT}}", html_body)
        .replace("{{GENERATED_AT}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
    )

    out_path = md_path.with_suffix(".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"✓ HTML generado: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Markdown → HTML McKinsey")
    parser.add_argument("md_path", help="Ruta al archivo .md")
    args = parser.parse_args()

    md_path = Path(args.md_path)
    if not md_path.exists():
        print(f"❌ ERROR: No existe {md_path}", file=sys.stderr)
        sys.exit(2)

    convert(md_path)


if __name__ == "__main__":
    main()
