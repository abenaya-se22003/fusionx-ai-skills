#!/usr/bin/env python3
"""
extract_docx.py — Generic extractor for LOLC CBS "Master Data and API Requirements"
Word documents. Walks the document body in true reading order (paragraphs and
tables interleaved), and emits a structured JSON with:

  - headings: every Heading-styled paragraph, in order
  - sections: every table, split into logical sub-sections whenever a "new header
    row" is detected mid-table (some source documents embed two logically distinct
    tables — e.g. a field listing followed by an API activity listing — inside one
    physical Word table with no paragraph break between them). Each section carries
    its nearest preceding heading as context, its header row, and its data rows as
    both a list-of-lists and a list-of-dicts (keyed by header).
  - is_field_table is set True for any section whose header row contains a cell
    matching /field\\s*name/i — this is the primary table the skill should treat as
    "the fields to map".

Usage:
    python extract_docx.py "<path-to-docx>" --out fields_extracted.json
"""
import argparse
import json
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

# Header vocabulary seen across LOLC CBS master-data/API requirement docs.
# A row is treated as a header boundary (start of a new logical section) if at
# least 2 of its non-empty cell texts match an entry here (case-insensitive,
# substring match either direction).
HEADER_HINTS = [
    "field name", "screen id", "mobile screen", "section", "sub-screen", "sub screen",
    "ui control", "api id", "activity", "minimum request context",
    "minimum required response", "usage", "scenario", "expected behaviour",
    "expected behavior", "category", "recommended mechanism", "examples",
    "data area", "primary mechanism", "purpose", "journey area",
    "representative data", "document title", "scope", "important note",
]

FIELD_NAME_RE = re.compile(r"field\s*name", re.IGNORECASE)
API_HINT_RE = re.compile(r"api\s*id", re.IGNORECASE)


def iter_block_items(document):
    parent_elm = document.element.body
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield "paragraph", Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield "table", Table(child, document)


def cell_text(cell):
    return " ".join(cell.text.split())


def looks_like_header(row_texts, prev_header):
    non_empty = [t for t in row_texts if t.strip()]
    if not non_empty:
        return False
    hits = 0
    for t in non_empty:
        tl = t.strip().lower()
        for hint in HEADER_HINTS:
            if hint in tl or tl in hint:
                hits += 1
                break
    if hits >= 2 and row_texts != prev_header:
        return True
    return False


def split_table_into_sections(table, table_index, context_heading, context_paragraph):
    sections = []
    rows = table.rows
    if not rows:
        return sections

    def row_texts(row):
        return [cell_text(c) for c in row.cells]

    header = row_texts(rows[0])
    current_rows = []
    sub_idx = 0

    for row in rows[1:]:
        texts = row_texts(row)
        if looks_like_header(texts, header):
            sections.append(build_section(table_index, sub_idx, context_heading, context_paragraph, header, current_rows))
            sub_idx += 1
            header = texts
            current_rows = []
            continue
        current_rows.append(texts)

    sections.append(build_section(table_index, sub_idx, context_heading, context_paragraph, header, current_rows))
    return sections


def build_section(table_index, sub_idx, context_heading, context_paragraph, header, data_rows):
    is_field_table = any(FIELD_NAME_RE.search(h or "") for h in header)
    is_api_hint_table = any(API_HINT_RE.search(h or "") for h in header)
    rows_as_dicts = []
    for r in data_rows:
        d = {}
        for i, h in enumerate(header):
            key = h if h else f"col_{i+1}"
            val = r[i] if i < len(r) else ""
            d[key] = val
        rows_as_dicts.append(d)
    return {
        "table_index": table_index,
        "sub_section_index": sub_idx,
        "context_heading": context_heading,
        "context_paragraph": context_paragraph,
        "header": header,
        "is_field_table": is_field_table,
        "is_api_hint_table": is_api_hint_table,
        "num_rows": len(data_rows),
        "rows": rows_as_dicts,
        "rows_raw": data_rows,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx_path")
    ap.add_argument("--out", required=True, help="Output JSON path")
    args = ap.parse_args()

    doc = Document(args.docx_path)

    headings = []
    sections = []
    current_heading = None
    last_paragraph_text = None
    table_index = -1

    for kind, item in iter_block_items(doc):
        if kind == "paragraph":
            text = item.text.strip()
            style_name = (item.style.name if item.style else "") or ""
            if text and style_name.lower().startswith("heading"):
                level = re.sub(r"[^0-9]", "", style_name) or "0"
                current_heading = text
                headings.append({"level": int(level) if level else 0, "text": text})
            elif text:
                last_paragraph_text = text
        else:
            table_index += 1
            secs = split_table_into_sections(item, table_index, current_heading, last_paragraph_text)
            sections.extend(secs)
            last_paragraph_text = None

    field_sections = [s for s in sections if s["is_field_table"]]
    api_hint_sections = [s for s in sections if s["is_api_hint_table"]]

    out = {
        "source_docx": args.docx_path,
        "num_tables": table_index + 1,
        "num_sections": len(sections),
        "headings": headings,
        "sections": sections,
        "field_table_indices": [(s["table_index"], s["sub_section_index"]) for s in field_sections],
        "api_hint_table_indices": [(s["table_index"], s["sub_section_index"]) for s in api_hint_sections],
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    total_field_rows = sum(s["num_rows"] for s in field_sections)
    print(f"Tables found: {table_index + 1} -> split into {len(sections)} logical sections")
    print(f"Field-listing sections: {len(field_sections)} ({total_field_rows} field rows total)")
    print(f"API-hint sections: {len(api_hint_sections)}")
    for s in field_sections:
        print(f"  field table[{s['table_index']}.{s['sub_section_index']}] under '{s['context_heading']}': "
              f"header={s['header']} rows={s['num_rows']}")
    print(f"Saved -> {args.out}")


if __name__ == "__main__":
    main()
