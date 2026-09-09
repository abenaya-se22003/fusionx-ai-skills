# -*- coding: utf-8 -*-
"""
to_pdf_export.py - Export a manual .docx to PDF via Word COM, with a forced field/TOC
refresh, and re-save the .docx so the refreshed TOC is part of the actual deliverable
(not just the PDF snapshot).

WHY VIA WORD COM, NOT A THIRD-PARTY CONVERTER
------------------------------------------------
The Table of Contents in these manuals is a real Word field, not static text. It does
not refresh on save via python-docx, and does not refresh from a plain Word open+re-save
either - it requires an explicit Fields.Update() / TablesOfContents.Update() call. A
third-party docx->PDF converter will render whatever stale TOC text is already baked in,
silently missing every heading you just added or renumbered.

This same COM round-trip is also the only way to catch a specific, nasty class of bug:
Word's own file writer can silently strip or discard invalid numbering.xml/numPr content
that python-docx and a same-session PDF render both tolerate. If your build script touched
heading numbering, ALWAYS re-open the .docx this script just saved (via python-docx) and
re-check it, rather than trusting the .docx you built moments before running this script.
See the "Heading Numbering" section of SKILL.md's "Manual Production Rules" for the full
story and qc_audit.py for a script that does this re-check for you.

USAGE
-----
    python to_pdf_export.py --src "<path to .docx>" [--dst "<path to .pdf>"]

    --dst defaults to the same path/name as --src with a .pdf extension.

REQUIREMENTS
------------
    pip install pywin32
    Microsoft Word must be installed and licensed on this machine (this drives the real
    Word application via COM automation - it is not a headless/server-side PDF renderer).
"""

import argparse
import os

import win32com.client as win32


def export(src, dst):
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(src)
        doc.Fields.Update()
        for toc in doc.TablesOfContents:
            toc.Update()
        doc.Save()  # persist the refreshed TOC/fields into the .docx deliverable itself
        doc.SaveAs(dst, FileFormat=17)  # wdFormatPDF
        doc.Close()
        print("PDF saved:", dst, os.path.getsize(dst))
    finally:
        word.Quit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="Path to the source .docx")
    ap.add_argument("--dst", default=None, help="Path to the output .pdf (default: same name as --src, .pdf extension)")
    args = ap.parse_args()

    dst = args.dst or (os.path.splitext(args.src)[0] + ".pdf")
    export(args.src, dst)
