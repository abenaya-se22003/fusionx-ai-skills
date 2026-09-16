"""Run the 17 mandatory FusionX URS DOCX checks with one command.

The authoritative implementations live in references/docx-formatting.md so
the explanation and executable rule cannot silently diverge. This wrapper
extracts that maintained Python block, runs every check, and returns a
non-zero exit status on a reported failure or an unexpected checker error.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
from pathlib import Path


CHECKS = (
    "check_numbering", "check_numbering_gap", "check_heading_numbering",
    "check_bullets", "check_second_list_start", "check_body_spacing",
    "check_section_transitions", "check_front_matter", "check_fonts",
    "check_colors", "check_table_styles", "check_no_cell_margins",
    "check_heading_indent_progression", "check_no_docdefault_paragraph_spacing",
    "check_toc_field_live", "check_toc_page_numbers_real", "check_hex_ids",
)


def load_documented_checks() -> dict[str, object]:
    reference = Path(__file__).resolve().parents[1] / "references" / "docx-formatting.md"
    text = reference.read_text(encoding="utf-8")
    first_check = text.index("def check_numbering(docx_path):")
    block_start = text.rfind("```python", 0, first_check) + len("```python")
    # The example invocation follows the final checker; it must not execute.
    block_end = text.index("\npath = \"./outputs/", first_check)
    namespace: dict[str, object] = {"__name__": "urs_qc_checks"}
    exec(compile(text[block_start:block_end], str(reference), "exec"), namespace)
    missing = [name for name in CHECKS if not callable(namespace.get(name))]
    if missing:
        raise RuntimeError(f"Documented QC implementations missing: {', '.join(missing)}")
    return namespace


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python qc_audit.py <path-to-urs.docx>", file=sys.stderr)
        return 2
    docx = Path(sys.argv[1]).resolve()
    if not docx.is_file():
        print(f"DOCX not found: {docx}", file=sys.stderr)
        return 2

    try:
        checks = load_documented_checks()
    except Exception as exc:
        print(f"FAIL [qc-loader] Could not load documented checks: {exc}")
        return 1

    failures: list[str] = []
    for name in CHECKS:
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                checks[name](str(docx))  # type: ignore[index, operator]
        except Exception as exc:
            output.write(f"FAIL: {name} raised {type(exc).__name__}: {exc}\n")
        result = output.getvalue().rstrip()
        print(result)
        if re.search(r"(?:^|\n)FAIL(?:\b|:)", result):
            failures.append(name)

    if failures:
        print(f"FAIL [summary] {len(failures)}/17 required checks failed: {', '.join(failures)}")
        return 1
    print("PASS [summary] All 17 required DOCX checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
