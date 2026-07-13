#!/usr/bin/env python3
"""
Validador de informes — comprueba que el informe cumple los estándares de calidad
antes de la entrega. 9 checks automáticos.
"""

import argparse
import re
import sys
from pathlib import Path


class ReportValidator:
    """Valida la calidad estructural del informe."""

    REQUIRED_SECTIONS = [
        ("resumen ejecutivo", r"##\s+Resumen\s+ejecutivo"),
        ("introducción", r"##\s+Introducci[óo]n"),
        ("hallazgos", r"##\s+(Hallazgo|An[áa]lisis)"),
        ("síntesis", r"##\s+S[íi]ntesis"),
        ("limitaciones", r"##\s+Limitaciones"),
        ("recomendaciones", r"##\s+Recomendaciones"),
        ("bibliografía", r"##\s+Bibliograf[íi]a"),
        ("metodología", r"##\s+(Anexo\s+)?(Metodolog[íi]a|Metodol[óo]gico)"),
    ]

    PLACEHOLDER_PATTERNS = [
        r"\bTBD\b",
        r"\bTODO\b",
        r"\[PLACEHOLDER\]",
        r"\[PENDIENTE\]",
        r"contenido continúa",
        r"due to length",
        r"\[Secciones?\s+\d+[-–]\d+\]",
        r"\.\.\.continúa\.\.\.",
        r"\betc\.\s*$",  # "etc." al final de línea sospechoso en bibliografía
        r"\[\d+[-–]\d+\]\s+Citas adicionales",
    ]

    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.content = self._read_report()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _read_report(self) -> str:
        try:
            with open(self.report_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ ERROR: No se puede leer el informe: {e}", file=sys.stderr)
            sys.exit(1)

    def validate(self) -> bool:
        print(f"\n{'='*60}")
        print(f"VALIDANDO INFORME: {self.report_path.name}")
        print(f"{'='*60}\n")

        checks = [
            ("Resumen ejecutivo (200-400 palabras)", self._check_executive_summary),
            ("Secciones obligatorias", self._check_required_sections),
            ("Formato de citas [N]", self._check_citation_format),
            ("Bibliografía completa", self._check_bibliography),
            ("Sin marcadores ni TODO", self._check_placeholders),
            ("Sin truncamientos", self._check_content_truncation),
            ("Conteo de palabras razonable", self._check_word_count),
            ("Mínimo 10 fuentes", self._check_source_count),
            ("Enlaces internos válidos", self._check_broken_references),
        ]

        passed = 0
        failed = 0
        for name, func in checks:
            try:
                ok = func()
                status = "✓" if ok else "✗"
                print(f"  {status} {name}")
                if ok:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ✗ {name} — error: {e}")
                failed += 1

        print(f"\n{'-'*60}")
        print(f"Resultado: {passed}/{len(checks)} checks pasados")
        if self.errors:
            print(f"\nErrores ({len(self.errors)}):")
            for err in self.errors:
                print(f"  • {err}")
        if self.warnings:
            print(f"\nAvisos ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  • {w}")
        print(f"{'='*60}\n")

        return failed == 0

    def _check_executive_summary(self) -> bool:
        match = re.search(
            r"##\s+Resumen\s+ejecutivo\s*\n+(.*?)(?=\n##\s|\Z)",
            self.content,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            self.errors.append("No se encontró sección 'Resumen ejecutivo'")
            return False
        text = match.group(1).strip()
        words = len(text.split())
        if words < 150 or words > 500:
            self.errors.append(
                f"Resumen ejecutivo: {words} palabras (esperado 200-400, tolerancia 150-500)"
            )
            return False
        return True

    def _check_required_sections(self) -> bool:
        all_present = True
        for name, pattern in self.REQUIRED_SECTIONS:
            if not re.search(pattern, self.content, re.IGNORECASE):
                self.errors.append(f"Sección obligatoria faltante: '{name}'")
                all_present = False
        return all_present

    def _check_citation_format(self) -> bool:
        # Buscar citas mal formadas: ej. (1), [1.], [N], etc.
        bad_patterns = [
            # Citas con paréntesis tipo (1), (2), (3) — pero NO años (19xx|20xx)
            (r"\(\s*(?!19\d\d|20\d\d)\d{1,3}\s*\)", "citas con paréntesis en vez de corchetes"),
            (r"\[\s*N\s*\]", "marcador [N] sin sustituir"),
        ]
        ok = True
        for pat, desc in bad_patterns:
            matches = re.findall(pat, self.content)
            if matches and len(matches) > 2:  # tolerar 1-2 falsos positivos
                self.warnings.append(f"Posibles {desc}: {len(matches)} casos")
        # Verificar que existen citas [N]
        cites = re.findall(r"\[(\d+)\]", self.content)
        if len(cites) < 5:
            self.errors.append(f"Solo {len(cites)} citas [N] encontradas (mínimo 5)")
            ok = False
        return ok

    def _check_bibliography(self) -> bool:
        # Extraer sección de bibliografía
        match = re.search(
            r"##\s+Bibliograf[íi]a\s*\n+(.*?)(?=\n##\s|\Z)",
            self.content,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            self.errors.append("Sección 'Bibliografía' no encontrada")
            return False

        bib_text = match.group(1)
        bib_entries = re.findall(r"^\s*\[(\d+)\]", bib_text, re.MULTILINE)
        bib_nums = set(int(n) for n in bib_entries)

        # Citas usadas en cuerpo (excluyendo bibliografía)
        body = self.content[: match.start()]
        body_cites = set(int(n) for n in re.findall(r"\[(\d+)\]", body))

        missing_in_bib = body_cites - bib_nums
        unused = bib_nums - body_cites

        ok = True
        if missing_in_bib:
            self.errors.append(
                f"Citas en cuerpo sin entrada en bibliografía: {sorted(missing_in_bib)}"
            )
            ok = False
        if unused:
            self.warnings.append(
                f"Entradas en bibliografía no citadas en cuerpo: {sorted(unused)}"
            )
        return ok

    def _check_placeholders(self) -> bool:
        found = []
        for pat in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pat, self.content, re.IGNORECASE)
            if matches:
                found.append(f"{pat}: {len(matches)}")
        if found:
            self.errors.append(f"Marcadores detectados: {'; '.join(found)}")
            return False
        return True

    def _check_content_truncation(self) -> bool:
        truncation_signals = [
            r"\[contenido omitido\]",
            r"\[continúa en siguiente parte\]",
            r"…\s*$",  # ellipsis al final del documento
        ]
        for pat in truncation_signals:
            if re.search(pat, self.content[-500:], re.IGNORECASE | re.MULTILINE):
                self.errors.append(f"Posible truncamiento detectado: {pat}")
                return False
        # Verificar que el doc no termine abruptamente en medio de una frase
        last_para = self.content.strip().split("\n")[-1].strip()
        if last_para and not last_para[-1] in ".!?)]\"'»":
            self.warnings.append(
                f"El documento termina sin puntuación de cierre: '...{last_para[-60:]}'"
            )
        return True

    def _check_word_count(self) -> bool:
        words = len(self.content.split())
        if words < 500:
            self.errors.append(f"Informe demasiado corto: {words} palabras (mínimo 500)")
            return False
        if words > 25000:
            self.warnings.append(f"Informe muy largo: {words} palabras (>25.000)")
        return True

    def _check_source_count(self) -> bool:
        match = re.search(
            r"##\s+Bibliograf[íi]a\s*\n+(.*?)(?=\n##\s|\Z)",
            self.content,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return False
        bib_entries = re.findall(r"^\s*\[(\d+)\]", match.group(1), re.MULTILINE)
        count = len(set(bib_entries))
        if count < 10:
            self.errors.append(f"Solo {count} fuentes en bibliografía (mínimo 10)")
            return False
        return True

    def _check_broken_references(self) -> bool:
        # Buscar markdown links rotos
        md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", self.content)
        broken = []
        for text, url in md_links:
            if url.startswith("#"):
                anchor = url[1:]
                # Verificar que el ancla existe (heading slugificado)
                if not re.search(
                    re.escape(anchor).replace("-", "[-\\s]"),
                    self.content,
                    re.IGNORECASE,
                ):
                    broken.append(url)
        if broken:
            self.warnings.append(f"Enlaces internos potencialmente rotos: {broken[:3]}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Validador de informes")
    parser.add_argument("--report", required=True, help="Ruta al informe .md")
    args = parser.parse_args()

    report = Path(args.report)
    if not report.exists():
        print(f"❌ ERROR: No existe {report}", file=sys.stderr)
        sys.exit(2)

    validator = ReportValidator(report)
    ok = validator.validate()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
