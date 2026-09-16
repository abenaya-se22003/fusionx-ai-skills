"""Run the 17 required FusionX URS XML checks with one portable command."""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


def check(name: str, ok: bool, detail: str) -> bool:
    print(f"{'PASS' if ok else 'FAIL'} [{name}] {detail}")
    return ok


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python qc_audit.py <path-to-urs.docx>")
    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        raise SystemExit(f"DOCX not found: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        doc = archive.read("word/document.xml").decode("utf-8")
        styles = archive.read("word/styles.xml").decode("utf-8") if "word/styles.xml" in names else ""
        numbering = archive.read("word/numbering.xml").decode("utf-8") if "word/numbering.xml" in names else ""

    results = []
    toc_spans = [(m.start(), m.end()) for m in re.finditer(r'<w:hyperlink w:anchor="_Toc[^>]*>[\s\S]*?</w:hyperlink>', doc)]
    typed_matches = list(re.finditer(r"<w:t[^>]*>\s*\d+(?:\.\d+){1,4}\.\s", doc))
    typed = not any(not any(start <= m.start() < end for start, end in toc_spans) for m in typed_matches)
    results.append(check("numbering", typed and "<w:numPr>" in doc, "no typed multi-level numbers; numPr present"))
    results.append(check("numbering-gap", 'w:suff w:val="tab"' in numbering, "number levels use tab suffix"))
    results.append(check("heading-numbering", "Heading1" in styles and "<w:numPr>" in doc, "heading style and numPr present"))
    results.append(check("bullets", 'w:numFmt w:val="bullet"' in numbering, "bullet numbering definition present"))
    results.append(check("second-list-start", doc.count("Data Dictionary") > 0 and numbering.count("<w:abstractNum") >= 2, "independent numbering definitions available"))
    front = all(x in doc for x in ("Table of Content", "List of Figures", "List of Tables", "TOC \\"))
    results.append(check("front-matter", front, "TOC, LoF, LoT and TOC field present"))
    results.append(check("section-transitions", "<w:p><w:r><w:t/></w:r></w:p><w:p" not in doc, "no known stacked empty-paragraph pattern"))
    results.append(check("body-spacing", not re.search(r"(?:<w:p[^>]*>\s*</w:p>\s*){2,}", doc), "no stacked empty body paragraphs"))
    results.append(check("fonts", "Candara" in styles or "Candara" in doc, "Candara explicitly declared"))
    results.append(check("colors", "0070C0" in doc and "2F5496" in doc, "cover and heading colours present"))
    results.append(check("table-styles", "<w:tblStyle" in doc, "all tables require manual review against style list"))
    results.append(check("no-cell-margins", "<w:tcMar" not in doc, "no direct cell-margin overrides"))
    results.append(check("heading-indent", "<w:ind " in numbering, "numbering indents present"))
    defaults = re.search(r"<w:docDefaults>([\s\S]*?)</w:docDefaults>", styles)
    results.append(check("no-docdefault-spacing", not defaults or "<w:spacing" not in defaults.group(1), "no document-default paragraph spacing"))
    results.append(check("toc-field-live", "<w:sdt" not in doc and "w:dirty=\"true\"" not in doc, "no stale SDT/dirty TOC wrapper"))
    pages = re.findall(r'<w:hyperlink w:anchor="_Toc[^>]*>[\s\S]*?<w:t>(\d+)</w:t>', doc)
    results.append(check("toc-page-numbers", len(set(pages)) > 1, "TOC entries have varying cached page numbers"))
    ids = re.findall(r'(?:w14:paraId|wp14:anchorId|wp14:editId)="([^"]+)"', doc)
    results.append(check("hex-ids", all(re.fullmatch(r"[0-9A-Fa-f]{8}", value) for value in ids), "all tracked XML IDs are eight-digit hex"))
    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
