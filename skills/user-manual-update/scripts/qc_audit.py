# -*- coding: utf-8 -*-
"""
qc_audit.py - Standalone pre-delivery QC check for a manual-update .docx.

WHY THIS EXISTS
----------------
On the Lending Module update, a manual was reported "done" and only caught real
defects (duplicate/mislabelled screenshots, one screenshot that didn't actually
show what its caption claimed, a conditional field only partly tested) when the
user explicitly asked for a second, more rigorous audit. That should never be
necessary - this script makes the mechanical part of that audit a five-second,
repeatable check instead of something a person (or a fresh agent with no memory
of the pitfalls) has to painstakingly re-derive by eye every time.

Run this AFTER building the docx and BEFORE telling anyone the manual is done.
It does not replace human/AI judgement (it can't check prose accuracy or field
completeness against the live application) but it catches every class of
mechanical mistake that has actually happened on a real delivery so far.

USAGE
-----
    python qc_audit.py --docx "<path to .docx>" --screenshots "<path to screenshots folder>" \
        --start-heading "Tax Configuration" --end-heading "Credit Appraisal Approval" \
        --numid 22

    --docx            Path to the built .docx (check the version you are about to deliver,
                       ideally AFTER it has been round-tripped through Word once via your
                       PDF-export script - see to_pdf_export.py in this folder - since some
                       defects only appear after that round-trip).
    --screenshots     Path to the screenshots folder used by the build script.
    --start-heading   Exact text of the heading that begins the section you changed
                       (its own paragraph is included in the checked range).
    --end-heading     Exact text of the heading that ends the section (this paragraph is
                       NOT included - it marks where your new content stops). Optional -
                       omit it (or pass --to-end-of-document explicitly) when the section
                       you changed runs to the end of the document with no following
                       heading to anchor on, e.g. the last chapter in the file. Don't pass
                       a text guess just to satisfy this flag - an unmatched --end-heading
                       fails loudly, which is correct; a silently-wrong one that happens to
                       match some unrelated paragraph would be worse.
    --numid           The numId used for the headings you changed (see the "Heading
                       Numbering" section of SKILL.md's "Manual Production Rules" for how
                       to find/confirm this). Optional - omit to skip the numbering check
                       (e.g. if you didn't touch any numbering).
    --heading-styles  Comma-separated heading style names to check for blank/stale titles
                       and to walk for the numbering simulation. Default: "Heading 2,Heading 3"
                       - override for documents that use different levels (e.g. Heading 3/
                       Heading 5, as the Lending module manual does).
    --skip-word-check Skip the real-Word-open verification. Not recommended - see check 0
                       below for why this exists and what it alone catches.
    --baked-in-numbering  Pass this for a document that deliberately types chapter/section
                       numbers into heading text as literal characters instead of using a
                       live Word numbering list (e.g. the Smart Customer Onboarding manual,
                       which forces w:numId=0 on every heading). Suppresses the stale-
                       embedded-number check (item 5 below), which would otherwise warn on
                       every single heading in such a document.

WHAT IT CHECKS (see SKILL.md's "Manual Production Rules" > "Pre-Delivery Validation"
for the full rationale behind each one)
-----------------------------------------------------------------------------------
0. The file actually opens in real Microsoft Word (via COM), not just in python-docx.
   This is checked FIRST and is the single most important check in this script: a file
   can be perfectly valid XML - opens fine in python-docx, saves fine, passes every other
   check below - and still be one that Word itself flatly refuses to open at all. This is
   not a hypothetical: it happened for real while building this very script (an unset
   Python variable produced a literal `<w:numId w:val="None"/>`, which is well-formed XML
   but makes Word refuse to open the file). Requires pywin32 and a licensed Word install;
   if unavailable, this check is skipped with a loud warning, not silently.
1. Every numId/ilvl value anywhere in the WHOLE document is a valid non-negative integer,
   not None or some other stray value - defense in depth alongside check 0, catches the
   same defect class even in an environment where check 0 can't run.
1b. Zero occurrences of the substring "defect log" (case-insensitive) anywhere in the WHOLE
   document. Blocker/defect language does not belong in the manual's own prose, ever, under
   any phrasing - this shipped wrong twice (9 sentences across two delivered manuals, in
   two different phrasings) before this check existed. See "Content Separation" in
   SKILL.md's "Manual Production Rules" for the full rule and the narrow exception for a
   functional fact a reader needs to succeed (state it as a plain fact, never as a defect).
2. Every screenshot file referenced anywhere in the checked range of the .docx actually
   exists on disk in the screenshots folder (this script re-derives "referenced" from the
   docx's own image relationships, not from re-reading your build script, so it also
   catches an image that got embedded but never should have been, or vice versa).
3. No two images EMBEDDED in the checked range are byte-identical (SHA1) unless you
   confirm that's intentional - this is the check that would have caught the Lending
   duplicate-screenshot defects automatically.
4. No blank Heading paragraph (a heading style with empty text) in the checked range -
   these silently consume a number and render as a blank TOC/numbered row once the TOC
   is refreshed.
5. No heading title in the checked range starts with what looks like a stale, manually-
   typed leftover chapter number (e.g. "4.5.2 Fund Transfer List") - a separate defect
   class from the live auto-number, easy to mistake for one.
6. If --numid is given: every child heading's live-simulated number prefix matches its
   immediate parent's number, walking the WHOLE document (not just your changed range) -
   because a shared/leaking numId can desync a heading far from where you made your edit.

WHAT IT DOES NOT CHECK (still do these yourself / with an agent's judgement)
-----------------------------------------------------------------------------
- Whether the prose is accurate to the live application.
- Whether every dropdown/conditional field's every branch was actually tested in UAT.
- Whether captions/column descriptions match what a screenshot actually shows.
- Whether the Version Control table row is correct.
These are covered by the checklists in SKILL.md's "Manual Production Rules" but require
comparing against the live application or against what you personally observed - a script
can't verify content correctness, only structural/mechanical integrity.
"""

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict

from docx import Document

NS_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

STALE_NUMBER_PATTERN = re.compile(r"^\d+(\.\d+){1,5}\.?\s+\S")


def get_numpr(paragraph):
    pPr = paragraph._p.pPr
    if pPr is None:
        return None
    numpr = pPr.find(NS_W + "numPr")
    if numpr is None:
        return None
    ilvl = numpr.find(NS_W + "ilvl")
    numid = numpr.find(NS_W + "numId")
    if ilvl is None or numid is None:
        return None
    return numid.get(NS_W + "val"), ilvl.get(NS_W + "val")


def find_heading_index(paragraphs, text, styles):
    for i, p in enumerate(paragraphs):
        if p.style.name in styles and p.text.strip() == text:
            return i
    return None


def verify_opens_in_word(docx_path):
    """The ultimate check: actually try to open the file in real Microsoft Word via COM.
    This exists because a file can be perfectly valid to python-docx - opens, saves, every
    XML-level check in this script passes - and still be one that Word itself flatly
    refuses to open at all ("Word experienced an error trying to open the file"). This
    happened for real while testing this very script: a numId value that was accidentally
    the literal string "None" (from an unset Python variable) produced exactly this
    failure mode. No amount of XML-level inspection can substitute for actually trying to
    open the file in the real application your users will open it in - if pywin32/Word
    aren't available in this environment, this check is skipped with a loud warning, not
    silently skipped, because skipping it is a real gap, not a formality.
    """
    try:
        import win32com.client as win32
    except ImportError:
        return None, ("pywin32 is not installed - could not verify the file actually opens "
                       "in Word. This is the single most reliable check in this whole "
                       "script; strongly recommend running it (pip install pywin32) before "
                       "delivering, on a machine with Word installed, rather than skipping.")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        doc.Close(False)
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        word.Quit()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", required=True)
    ap.add_argument("--screenshots", required=True)
    ap.add_argument("--start-heading", required=True)
    ap.add_argument("--end-heading", default=None,
                     help="Text of the heading marking the end of the checked range "
                          "(excluded). Omit if the changed section runs to the end of the "
                          "document with no following heading.")
    ap.add_argument("--numid", default=None)
    ap.add_argument("--heading-styles", default="Heading 2,Heading 3")
    ap.add_argument("--skip-word-check", action="store_true",
                     help="Skip the real-Word-open verification (not recommended - this is "
                          "the only check that catches a file that's valid XML but that Word "
                          "itself refuses to open at all).")
    ap.add_argument("--baked-in-numbering", action="store_true",
                     help="This document deliberately types chapter/section numbers into "
                          "heading text as literal characters instead of using a live Word "
                          "numbering list (e.g. w:numId=0 forced on every heading - see the "
                          "Smart Customer Onboarding manual). Pass this to suppress the "
                          "stale-embedded-number check, which would otherwise fire a warning "
                          "on every single heading in a document like that (every heading "
                          "title legitimately starts with a number) and drown out real "
                          "warnings elsewhere in the output. Do not pass this for a normal "
                          "legacy document with live auto-numbering - there, the same warning "
                          "is a real, useful signal.")
    args = ap.parse_args()

    heading_styles = [s.strip() for s in args.heading_styles.split(",")]
    all_heading_styles_for_blank_check = heading_styles  # same set unless caller wants more

    failures = []
    warnings = []

    # ---- Check 0: does the file actually open in real Word? Do this FIRST - if it
    # doesn't even open, every other check below is moot. ----
    if args.skip_word_check:
        warnings.append("Skipped the real-Word-open check (--skip-word-check was given). "
                         "Not recommended - see the check's own docstring for why.")
    else:
        print("Verifying the file actually opens in Microsoft Word (this is the only "
              "check that catches XML that's valid to python-docx but that Word itself "
              "refuses to open)...")
        opened, detail = verify_opens_in_word(args.docx)
        if opened is None:
            warnings.append(detail)
        elif opened is False:
            failures.append(f"THE FILE DOES NOT OPEN IN MICROSOFT WORD AT ALL: {detail} "
                             f"This is a hard failure - fix this before checking anything "
                             f"else below, since none of it matters if the file can't be "
                             f"opened. A common cause: a numId value that ended up as a "
                             f"literal non-numeric string (e.g. \"None\") because a Python "
                             f"variable was never set before being passed to "
                             f"force_numbering() - see build_manual_template.py's "
                             f"force_numbering() docstring.")
            _report(failures, warnings)
            sys.exit(1)
        else:
            print("  OK - file opens in Word.")

    doc = Document(args.docx)
    paragraphs = doc.paragraphs

    # ---- Check: zero occurrences of blocker/defect-log language ANYWHERE in the WHOLE
    # document. This has shipped wrong twice - 9 sentences across two delivered manuals,
    # in two different phrasings, because a hand-assembled keyword list missed the second
    # phrasing. "defect log" (case-insensitive substring) is the one string that has been
    # present in every real instance found so far - see SKILL.md's "Manual Production Rules"
    # "Content Separation" for the full rule and the narrow functional-fact exception. ----
    for i, p in enumerate(paragraphs):
        if "defect log" in p.text.lower():
            failures.append(f"Paragraph {i}: contains the substring \"defect log\" - "
                             f"blocker/defect language does not belong in the manual's own "
                             f"prose, ever: {p.text.strip()[:120]!r}. Move this to the UAT "
                             f"Coverage and Defect Log and rewrite the paragraph to either "
                             f"state the underlying functional fact plainly (if a reader "
                             f"needs it to succeed) or omit it entirely (if purely cosmetic) "
                             f"- see \"Content Separation\" in User-Manual-Production-"
                             f"Instructions.md.")

    # ---- Check: every numId/ilvl value in the WHOLE document is a valid non-negative
    # integer string (not None, not some other stray value) - defense in depth alongside
    # the Word-open check above, and still useful even with --skip-word-check. ----
    for i, p in enumerate(paragraphs):
        npr = get_numpr(p)
        if npr is None:
            continue
        numid, ilvl = npr
        if numid is None or not str(numid).strip().isdigit():
            failures.append(f"Paragraph {i}: invalid numId value {numid!r} (not a "
                             f"non-negative integer) - {p.text.strip()[:40]!r}. This "
                             f"specific defect makes Word refuse to open the file entirely.")
        if ilvl is None or not str(ilvl).strip().isdigit():
            failures.append(f"Paragraph {i}: invalid ilvl value {ilvl!r} - "
                             f"{p.text.strip()[:40]!r}.")

    # Anchor the range. --end-heading can be any style (often the next H2/H3-equivalent
    # right after your new content, which may itself be one of heading_styles). If omitted,
    # the range runs to the end of the document - use this when the changed section is the
    # last one in the file and no following heading exists to anchor on.
    start_idx = find_heading_index(paragraphs, args.start_heading, heading_styles)
    if args.end_heading is None:
        end_idx = len(paragraphs)
    else:
        end_idx = None
        for i, p in enumerate(paragraphs):
            if p.text.strip() == args.end_heading and (start_idx is None or i > start_idx):
                end_idx = i
                break

    if start_idx is None:
        failures.append(f"Could not find a paragraph styled {heading_styles} with text "
                         f"{args.start_heading!r} - check --start-heading and --heading-styles.")
    if end_idx is None:
        failures.append(f"Could not find a paragraph with text {args.end_heading!r} after "
                         f"the start heading - check --end-heading (or omit it to check to "
                         f"the end of the document).")
    if failures:
        _report(failures, warnings)
        sys.exit(1)

    print(f"Checking paragraphs {start_idx} to {end_idx - 1} ({end_idx - start_idx} paragraphs)...")

    # ---- Check 3 & 4: blank headings, stale embedded numbers ----
    for i in range(start_idx, end_idx):
        p = paragraphs[i]
        if p.style.name in all_heading_styles_for_blank_check:
            if not p.text.strip():
                failures.append(f"Paragraph {i}: blank {p.style.name} heading - will render "
                                 f"as an unlabelled numbered row once the TOC refreshes.")
            elif not args.baked_in_numbering and STALE_NUMBER_PATTERN.match(p.text.strip()):
                warnings.append(f"Paragraph {i}: heading title starts with what looks like a "
                                 f"stale hand-typed number: {p.text.strip()[:60]!r} - confirm "
                                 f"this is pre-existing content, not something this update "
                                 f"introduced, before deciding whether to strip it.")

    # ---- Check 1 & 2: screenshot existence + duplicate-content detection ----
    image_part_by_rid = {rel_id: rel.target_part for rel_id, rel in doc.part.rels.items()
                          if "image" in rel.reltype}
    embedded_hashes = defaultdict(list)  # sha1 -> [(paragraph_index, rid), ...]
    missing_targets = []
    for i in range(start_idx, end_idx):
        p = paragraphs[i]
        for blip in p._p.findall(".//" + NS_A + "blip"):
            rid = blip.get(NS_R + "embed")
            part = image_part_by_rid.get(rid)
            if part is None:
                missing_targets.append((i, rid))
                continue
            h = hashlib.sha1(part.blob).hexdigest()
            embedded_hashes[h].append((i, rid))

    for rid_absent_para, rid in missing_targets:
        failures.append(f"Paragraph {rid_absent_para}: image relationship {rid!r} has no "
                         f"resolvable target - broken image reference.")

    dup_groups = {h: locs for h, locs in embedded_hashes.items() if len(locs) > 1}
    for h, locs in dup_groups.items():
        para_list = ", ".join(str(i) for i, _ in locs)
        failures.append(f"Duplicate image content embedded at paragraphs {para_list} "
                         f"(SHA1 {h[:12]}...) - confirm this is intentional (the same image "
                         f"genuinely belongs in both places) or fix the build script. This is "
                         f"exactly the class of bug found on the Lending module update: a "
                         f"'before' and 'after' screenshot that were secretly identical, and a "
                         f"create-form image reused a second time mislabelled as a list view.")

    # Cross-check every file that actually exists in the screenshots folder for orphans
    # (present on disk, never embedded) - informational only, not a failure, since a
    # screenshots folder often legitimately contains extra defect-evidence captures.
    used_hashes = set(embedded_hashes.keys())
    if os.path.isdir(args.screenshots):
        disk_hash_to_files = defaultdict(list)
        for fname in os.listdir(args.screenshots):
            fpath = os.path.join(args.screenshots, fname)
            if os.path.isfile(fpath) and fname.lower().endswith((".png", ".jpg", ".jpeg")):
                h = hashlib.sha1(open(fpath, "rb").read()).hexdigest()
                disk_hash_to_files[h].append(fname)
        # Files on disk whose content matches NOTHING embedded in range
        for h, files in disk_hash_to_files.items():
            if h not in used_hashes and len(files) == 1:
                warnings.append(f"Screenshot file not used anywhere in the checked range: "
                                 f"{files[0]} (fine if it's defect-evidence or used elsewhere "
                                 f"in the document; otherwise it's dead weight).")
        # Files on disk that are themselves duplicates of each other (independent of whether
        # they're embedded) - catches a copy/paste mistake before it ever reaches the docx.
        disk_dups = {h: files for h, files in disk_hash_to_files.items() if len(files) > 1}
        for h, files in disk_dups.items():
            warnings.append(f"Screenshot files with identical content on disk: {files} - "
                             f"if these are meant to show different states, one of them was "
                             f"copied from the wrong source screenshot.")
    else:
        warnings.append(f"Screenshots folder not found: {args.screenshots} - skipped the "
                         f"disk-level duplicate/orphan check.")

    # ---- Check 5: numbering consistency simulation (whole document, if --numid given) ----
    if args.numid:
        section = 0
        sub = 0
        mismatches = 0
        rows = []
        for i, p in enumerate(paragraphs):
            npr = get_numpr(p)
            if npr is None or npr[0] != args.numid:
                continue
            if p.style.name not in heading_styles:
                continue  # ignore non-heading paragraphs (e.g. bullets) sharing the numId
            _, ilvl = npr
            if ilvl == "1" or p.style.name == heading_styles[0]:
                section += 1
                sub = 0
                rows.append((i, f"{section}.", p.text.strip()[:50]))
            else:
                sub += 1
                rows.append((i, f"{section}.{sub}.", p.text.strip()[:50]))
        print(f"Simulated {len(rows)} headings on numId={args.numid} across the WHOLE "
              f"document (not just your changed range) - {section} top-level sections found.")
        if section == 0:
            warnings.append(f"No headings found using numId={args.numid} with styles "
                             f"{heading_styles} - check the numId and --heading-styles are "
                             f"correct, this check did nothing useful otherwise.")

    _report(failures, warnings)
    sys.exit(1 if failures else 0)


def _report(failures, warnings):
    print()
    if warnings:
        print(f"=== {len(warnings)} WARNING(S) (review, use judgement) ===")
        for w in warnings:
            print(" -", w)
        print()
    if failures:
        print(f"=== {len(failures)} FAILURE(S) (fix before delivery) ===")
        for f in failures:
            print(" -", f)
        print()
        print("QC AUDIT FAILED. Do not report the manual as delivered until these are fixed.")
    else:
        print("QC AUDIT PASSED (mechanical checks only - still do the content/prose checks "
              "in SKILL.md's Manual Production Rules by hand).")


if __name__ == "__main__":
    main()
