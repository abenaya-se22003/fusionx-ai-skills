# -*- coding: utf-8 -*-
"""
build_manual_template.py - Starting template for a module manual update build script.

READ THIS FIRST
----------------
This is not a script you run as-is. Copy it into a new module's working folder
(e.g. `<Module>-Manual-Update/build_<module>_v<N>.py`), fill in the CONFIG section, delete
the EXAMPLE CONTENT section, and write your own content using the helper functions below.
It exists so every new module update starts from the same proven, safety-checked
foundation instead of re-deriving the numbering rules from scratch (which took two entire
tickets' worth of hard-won lessons the first two times - see the "Heading Numbering"
section of SKILL.md's "Manual Production Rules" for the full story of what goes wrong
if you don't).

BEFORE YOU WRITE ANY CONTENT
------------------------------
1. Open the existing .docx and inspect the REAL style/numbering conventions of the
   section you're extending (see "Matching Existing Document Conventions" in
   SKILL.md's "Manual Production Rules"). Do not assume Heading 2/3, decimal numbering,
   or captioned images - every document so far has differed in at least one of these.
   Update HEADING_STYLE_L1 / HEADING_STYLE_L2 / FIELD_BULLET_STYLE / BODY_STYLE and
   USE_CAPTIONS below to match what you actually observe.
2. Run `check_numid_isolation()` (see below) on the numId used by the section you're
   about to extend, BEFORE deciding whether to reuse it directly or clone it. Only clone
   if the scan actually shows contamination - the Lending module's numId turned out to be
   genuinely isolated already, and cloning would have been unnecessary extra risk.
3. Capture the OLD paragraphs you intend to replace (if this is a full-refresh, not a
   pure addition) BEFORE inserting anything, using `doc.paragraphs[start_idx:end_idx]`,
   and only remove them at the very end, after all new content is inserted. See the
   EXAMPLE CONTENT section for the exact pattern.

AFTER BUILDING
--------------
1. Run to_pdf_export.py on the output .docx (this also refreshes the TOC and re-saves
   the .docx with that refresh applied).
2. Run qc_audit.py against the FRESHLY EXPORTED .docx (the one to_pdf_export.py just
   re-saved, not the one your build script produced a moment before - Word's own save can
   silently corrupt numbering that both python-docx and a same-session PDF tolerate).
3. Only then report the manual as delivered.
"""

import copy
import random

from docx import Document
from docx.shared import Emu
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# =====================================================================
# CONFIG - fill in for your module before running
# =====================================================================
SRC = r"PATH\TO\Original Module Manual.docx"
DST = r"PATH\TO\<Module>-Manual-Update\Module Manual vX.Y.docx"
SHOTS = r"PATH\TO\<Module>-Manual-Update\screenshots"

# The two heading levels you'll be writing at, e.g. ("Heading 2", "Heading 3") or, as on
# the Lending module, ("Heading 3", "Heading 5") - confirm the REAL pair from the existing
# document, don't assume Heading 2/3 by default.
HEADING_STYLE_L1 = "Heading 2"
HEADING_STYLE_L2 = "Heading 3"
FIELD_BULLET_STYLE = "List Paragraph"
BODY_STYLE = "Body Text"  # some documents use "Normal (Web)" instead - check first

# Does this document caption its screenshots ("Figure - ...") or drop them in bare? The
# Collateral and Accounts module manuals caption; the Lending module manual does not.
# Check the real convention (see point 1 above) - don't assume either way.
USE_CAPTIONS = True

FONT = None  # set to a font name (e.g. "Candara") only if the document's real styles
             # carry an explicit run-level font override - many documents (e.g. Lending)
             # have none, and inherit purely from the paragraph style, in which case leave
             # this as None and do not set r.font.name anywhere.

if SRC.startswith("PATH\\TO\\") or SRC.startswith("PATH/TO/"):
    raise SystemExit(
        "This is a template, not a runnable script as-is. Copy it into your module's "
        "working folder and fill in the CONFIG section (SRC/DST/SHOTS and the style names) "
        "before running it. See the module docstring at the top of this file."
    )

doc = Document(SRC)


# =====================================================================
# NUMBERING SAFETY TOOLKIT - the hard-won part, don't modify unless you
# understand exactly why each step exists (see the docstring references above)
# =====================================================================

def get_numpr(paragraph):
    pPr = paragraph._p.pPr
    if pPr is None:
        return None
    numpr = pPr.find(qn("w:numPr"))
    if numpr is None:
        return None
    ilvl = numpr.find(qn("w:ilvl"))
    numid = numpr.find(qn("w:numId"))
    if ilvl is None or numid is None:
        return None
    return numid.get(qn("w:val")), ilvl.get(qn("w:val"))


def check_numid_isolation(document, numid, edit_start_idx=None, edit_end_idx=None,
                           gap_tolerance=50):
    """Scan the WHOLE document for every paragraph using `numid` and report whether its
    usage forms ONE TIGHT, CONTIGUOUS block, vs. being scattered across unrelated,
    far-apart sections. Call this BEFORE deciding to reuse an existing numId directly.

    IMPORTANT - what "isolated" means here: a numId that continues past the exact section
    you're editing into the NEXT section (still contiguously, still the same list) is
    perfectly normal and safe - e.g. on the Lending module update, numId=22 correctly
    spanned Tax Configuration -> Credit Appraisal Definitions -> Credit Appraisal Approval
    as one continuous 3-chapter list, and only the first two of those three chapters were
    being edited. That is NOT contamination. Contamination looks like this instead: the
    same numId reappearing far away, with a huge index gap, attached to paragraphs whose
    text has nothing to do with the section you're editing (this is exactly what happened
    on the Accounts module update: numId=125/130/131 turned out to be GLOBAL shared
    child-counters used by dozens of unrelated sections scattered throughout the entire
    document). So: judge this by GAP SIZE and by reading the actual paragraph text at any
    reported gap, not merely by "did any usage fall outside my two edit-boundary
    headings."

    `edit_start_idx`/`edit_end_idx` are optional and only used to double check that your
    edit range itself falls within the numId's own contiguous span (a sanity check that
    you have the right numId at all) - they do NOT need to bound every single usage.
    `gap_tolerance` is the maximum paragraph-index gap between consecutive uses of this
    numId that still counts as "one contiguous block" - the default (50) comfortably
    covers a heading with a long run of body text/fields/screenshots underneath it before
    the next heading; a genuinely scattered/shared numId typically has gaps in the
    hundreds or thousands, not tens.

    Returns True if the usage looks like one contiguous block (safe to reuse directly),
    False if it looks scattered (use clone_isolated_abstract() instead). Always read the
    printed gap detail yourself before trusting the boolean - this is a heuristic, not a
    proof, and the paragraph text at each gap is the real evidence.
    """
    hits = []
    for i, p in enumerate(document.paragraphs):
        npr = get_numpr(p)
        if npr and npr[0] == str(numid):
            hits.append((i, p.style.name, p.text.strip()[:40]))
    if not hits:
        print(f"numId={numid}: not used anywhere - nothing to check (probably not the "
              f"right numId - double check).")
        return True

    idxs = [h[0] for h in hits]
    gaps = [(idxs[j], idxs[j + 1], idxs[j + 1] - idxs[j]) for j in range(len(idxs) - 1)]
    big_gaps = [g for g in gaps if g[2] > gap_tolerance]
    print(f"numId={numid}: {len(hits)} paragraphs, index range {idxs[0]}-{idxs[-1]}")

    if edit_start_idx is not None and not (idxs[0] <= edit_start_idx and edit_end_idx - 1 <= idxs[-1]):
        print(f"  WARNING: your stated edit range ({edit_start_idx}-{edit_end_idx}) is not "
              f"fully covered by this numId's own usage range - you may have the wrong "
              f"numId. Double check before proceeding either way.")

    if big_gaps:
        print(f"  {len(big_gaps)} gap(s) larger than {gap_tolerance} paragraphs found - "
              f"inspect these manually, they MAY indicate scattered/shared usage:")
        for start, end, size in big_gaps:
            start_text = next(h[2] for h in hits if h[0] == start)
            end_text = next(h[2] for h in hits if h[0] == end)
            print(f"   gap of {size} between paragraph {start} ({start_text!r}) and "
                  f"{end} ({end_text!r}) - read both paragraphs' context in the actual "
                  f"document before concluding either way.")
        print("  Do not trust this boolean alone - inspect the gaps above. If they're "
              "genuinely unrelated content, treat this numId as NOT safe to reuse "
              "directly and use clone_isolated_abstract() instead.")
        return False

    print("  Usage is one contiguous block - safe to reuse directly. Still worth a final "
          "visual spot-check of the rendered numbers after building.")
    return True


def clone_isolated_abstract(document, source_abstract_id, font=None):
    """Clone `source_abstract_id`'s level definitions into a brand-new abstractNumId that
    nothing else in the document references, and register a fresh numId pointing at it.
    Returns the new numId (str).

    Handles every schema/identity pitfall discovered on the Accounts module saga:
    - Gives the clone a FRESH random <w:nsid>/<w:tmpl> (a deepcopy otherwise retains the
      source's identity GUID, which two abstractNums must never share - Word's own writer
      will treat this as corrupt and silently regenerate the whole numbering.xml from
      near-empty defaults the next time it saves the file, discarding every custom
      numbering instance you added, with no error or warning).
    - Inserts the new <w:abstractNum> in the schema-required position (right after the
      last existing <w:abstractNum>, never after any <w:num> - CT_Numbering requires every
      abstractNum before every num).
    - Optionally forces the font of the auto-number glyph itself (via the abstract level's
      own w:rPr/w:rFonts, independent of the heading paragraph's own run font) to match
      the document's real heading font, if the source only carries a generic
      <w:rFonts w:hint="default"/>.
    """
    numbering_part_element = document.part.numbering_part.element

    source_abstract_el = None
    for an in numbering_part_element.findall(qn("w:abstractNum")):
        if an.get(qn("w:abstractNumId")) == str(source_abstract_id):
            source_abstract_el = an
            break
    assert source_abstract_el is not None, f"source abstractNum {source_abstract_id} not found"

    new_abstract_id = str(max(int(a.get(qn("w:abstractNumId"))) for a in
                               numbering_part_element.findall(qn("w:abstractNum"))) + 1)
    new_abstract_el = copy.deepcopy(source_abstract_el)
    new_abstract_el.set(qn("w:abstractNumId"), new_abstract_id)

    new_nsid = format(random.getrandbits(32), "08X")
    new_tmpl = format(random.getrandbits(32), "08X")
    for tag, val in (("w:nsid", new_nsid), ("w:tmpl", new_tmpl)):
        el = new_abstract_el.find(qn(tag))
        if el is not None:
            el.set(qn("w:val"), val)

    if font:
        for lvl in new_abstract_el.findall(qn("w:lvl")):
            if lvl.get(qn("w:ilvl")) in ("0", "1", "2", "3"):
                rPr = lvl.find(qn("w:rPr"))
                if rPr is None:
                    rPr = OxmlElement("w:rPr")
                    lvl.append(rPr)
                rFonts = rPr.find(qn("w:rFonts"))
                if rFonts is None:
                    rFonts = OxmlElement("w:rFonts")
                    rPr.append(rFonts)
                if rFonts.get(qn("w:hint")) is not None:
                    del rFonts.attrib[qn("w:hint")]
                rFonts.set(qn("w:ascii"), font)
                rFonts.set(qn("w:hAnsi"), font)

    existing_abstracts = numbering_part_element.findall(qn("w:abstractNum"))
    existing_abstracts[-1].addnext(new_abstract_el)

    new_numid = str(max(int(n.get(qn("w:numId"))) for n in
                         numbering_part_element.findall(qn("w:num"))) + 1)
    new_num_el = OxmlElement("w:num")
    new_num_el.set(qn("w:numId"), new_numid)
    abstract_ref = OxmlElement("w:abstractNumId")
    abstract_ref.set(qn("w:val"), new_abstract_id)
    new_num_el.append(abstract_ref)
    add_num_safely(numbering_part_element, new_num_el)

    print(f"cloned abstractNumId={source_abstract_id} -> new abstractNumId={new_abstract_id}, "
          f"new numId={new_numid}")
    return new_numid


def add_num_safely(numbering_part_element, num_el):
    """Insert a new <w:num> in the one schema-valid place: before the trailing
    <w:numIdMacAtCleanup> hint (if present), bumping that hint's own val to match -
    otherwise it names a smaller numId than what's now actually in the file, which is the
    same class of invalid state that makes Word discard the whole numbering.xml on save."""
    cleanup = numbering_part_element.find(qn("w:numIdMacAtCleanup"))
    if cleanup is not None:
        cleanup.addprevious(num_el)
        cleanup.set(qn("w:val"), num_el.get(qn("w:numId")))
    else:
        numbering_part_element.append(num_el)


def add_lvl_override(num_el, ilvl, start):
    lvl_override = OxmlElement("w:lvlOverride")
    lvl_override.set(qn("w:ilvl"), str(ilvl))
    start_override = OxmlElement("w:startOverride")
    start_override.set(qn("w:val"), str(start))
    lvl_override.append(start_override)
    num_el.append(lvl_override)


def force_numbering(paragraph, ilvl, numid):
    """Overwrite (or add) a paragraph's numPr in place. Only touches this one invisible
    property - the paragraph's own text/runs are untouched.

    w:numPr MUST precede w:rPr/w:ind/etc in CT_PPrBase's schema order (it belongs right
    after w:pStyle). Appending it at the end of pPr is tolerated by python-docx and by a
    same-session PDF render, but Word's own Save() strips it silently on the next
    open+save round-trip - a heading that had a correctly-set numPr moments earlier can
    render with NO number at all after the file round-trips through Word.

    CRITICAL - validated defensively on purpose: if `numid` is None (e.g. you forgot to
    set H1_NUMID/H2_NUMID/BULLET_NUMID before calling an insert_* helper), the naive code
    would silently write a literal `<w:numId w:val="None"/>` into the file. That is a
    FAR worse failure than the "silent strip on save" bug above: python-docx opens and
    saves a file with this in it without complaint, a plain python-docx-level check
    (including an earlier version of qc_audit.py) sees nothing wrong, and the file
    LOOKS completely fine - but Microsoft Word itself will flatly refuse to open the file
    at all ("Word experienced an error trying to open the file"), a hard, unrecoverable
    failure discovered only when someone actually double-clicks the delivered file. This
    was caught by accident while testing this exact template against real data - it is
    exactly the class of mistake this whole toolkit exists to prevent, so it is checked
    here explicitly rather than left to be rediscovered by whoever forgets to set a numId
    global next."""
    if numid is None or not str(numid).strip().isdigit():
        raise ValueError(
            f"force_numbering() called with an invalid numid={numid!r} (paragraph text: "
            f"{paragraph.text[:40]!r}). This must be a numeric string/int, e.g. from "
            f"check_numid_isolation()/clone_isolated_abstract(), or a numId you registered "
            f"yourself. A None or non-numeric value here produces a file that opens fine in "
            f"python-docx but that Microsoft Word will refuse to open at all - always fix "
            f"this here, never downstream. Did you forget to set H1_NUMID/H2_NUMID/"
            f"BULLET_NUMID before calling an insert_* helper?"
        )
    pPr = paragraph._p.get_or_add_pPr()
    existing = pPr.find(qn("w:numPr"))
    if existing is not None:
        pPr.remove(existing)
    numPr = OxmlElement("w:numPr")
    ilvl_el = OxmlElement("w:ilvl")
    ilvl_el.set(qn("w:val"), str(ilvl))
    numId_el = OxmlElement("w:numId")
    numId_el.set(qn("w:val"), str(numid))
    numPr.append(ilvl_el)
    numPr.append(numId_el)
    pStyle = pPr.find(qn("w:pStyle"))
    if pStyle is not None:
        pStyle.addnext(numPr)
    else:
        pPr.insert(0, numPr)


def repair_existing_numbering(document, admin_h1_text, master_numid,
                               l1_style=HEADING_STYLE_L1, l2_style=HEADING_STYLE_L2):
    """If (and only if) you determined via check_numid_isolation() that the existing
    numbering for this chapter is genuinely broken/contaminated (not just this update's
    new content, but pre-existing headings too), use this to force EVERY existing L1/L2
    heading from `admin_h1_text` onward onto one master numId. This is the "full repair"
    approach from the Accounts module saga - only reach for this if the isolation check
    actually showed contamination; most documents (e.g. Lending) don't need it."""
    admin_h1_index = None
    for i, p in enumerate(document.paragraphs):
        if p.style.name == "Heading 1" and p.text.strip() == admin_h1_text:
            admin_h1_index = i
            break
    assert admin_h1_index is not None, f"{admin_h1_text!r} H1 anchor not found"

    fixed_l1 = fixed_l2 = 0
    for i, p in enumerate(document.paragraphs):
        if i <= admin_h1_index:
            continue
        if p.style.name == l1_style:
            force_numbering(p, 1, master_numid)
            fixed_l1 += 1
        elif p.style.name == l2_style:
            force_numbering(p, 2, master_numid)
            fixed_l2 += 1
    print(f"repaired numbering on {fixed_l1} existing {l1_style} and {fixed_l2} existing "
          f"{l2_style} paragraphs under {admin_h1_text!r}")


def demote_blank_headings(document, start_idx, end_idx, normal_style="Normal (Web)",
                           heading_styles=(HEADING_STYLE_L1, HEADING_STYLE_L2)):
    """Pre-existing blank heading paragraphs silently consume a number and render as a
    blank TOC row once the TOC refreshes. CONFIRM WITH THE USER before running this - it
    changes previously "Done" content, even though it's a safe, additive-only change
    (demoting style, never touching text)."""
    count = 0
    for i in range(start_idx, end_idx):
        p = document.paragraphs[i]
        if p.style.name in heading_styles and not p.text.strip():
            p.style = document.styles[normal_style]
            count += 1
    print(f"demoted {count} blank heading paragraphs to {normal_style}")
    return count


# =====================================================================
# CONTENT HELPERS - use these to write your actual manual content.
# `anchor` must be set to the paragraph you're inserting everything before
# (see EXAMPLE CONTENT below for how to find/set it).
# =====================================================================
anchor = None  # set this in your own script before calling any insert_* helper
H1_NUMID = None  # set to the numId for HEADING_STYLE_L1, once determined/created
H2_NUMID = None  # set to the numId for HEADING_STYLE_L2 (often the same as H1_NUMID)
BULLET_NUMID = None  # set to a numId for field bullets (often a fresh, simple numId)


def insert_h1(text):
    p = anchor.insert_paragraph_before("")
    p.style = doc.styles[HEADING_STYLE_L1]
    force_numbering(p, 1, H1_NUMID)
    p.add_run(text)
    return p


def insert_h2(text):
    p = anchor.insert_paragraph_before("")
    p.style = doc.styles[HEADING_STYLE_L2]
    force_numbering(p, 2, H2_NUMID)
    p.add_run(text)
    return p


def insert_body(text):
    p = anchor.insert_paragraph_before("")
    p.style = doc.styles[BODY_STYLE]
    p.add_run(text)
    return p


def insert_bullet(text):
    p = anchor.insert_paragraph_before("")
    p.style = doc.styles[FIELD_BULLET_STYLE]
    force_numbering(p, 3, BULLET_NUMID)
    p.add_run(text)
    return p


def insert_field(name, description):
    insert_bullet(name)
    insert_body(description)


def insert_image(filename, caption=None):
    p = anchor.insert_paragraph_before("")
    p.style = doc.styles[BODY_STYLE]
    run = p.add_run()
    run.add_picture(f"{SHOTS}\\{filename}", width=Emu(5732145))
    if USE_CAPTIONS and caption:
        insert_body(caption)
    elif caption and not USE_CAPTIONS:
        print(f"WARNING: caption given for {filename} but USE_CAPTIONS is False for this "
              f"document - caption text dropped. Set USE_CAPTIONS=True if this document "
              f"actually does caption figures (double-check the real convention first).")
    return p


# =====================================================================
# EXAMPLE CONTENT - delete this whole section and write your own.
# This shows the required pattern for a full-refresh (replace existing content), the
# capture-before-insert-after-delete-at-the-end pattern that keeps paragraph indices safe.
# =====================================================================
if __name__ == "__main__":
    raise SystemExit(
        "This is a template, not a runnable script. Copy it into your module's working "
        "folder, fill in CONFIG, and replace this __main__ block with your own content. "
        "See the module docstring at the top of this file for the full recipe."
    )

    # --- example skeleton (unreachable, for reference only) ---
    # start_idx = end_idx = None
    # for i, p in enumerate(doc.paragraphs):
    #     if p.style.name == HEADING_STYLE_L1 and p.text.strip() == "Your Section":
    #         start_idx = i
    #     if p.style.name == HEADING_STYLE_L1 and p.text.strip() == "Next Section":
    #         end_idx = i
    #         break
    # anchor = doc.paragraphs[end_idx]
    # old_paragraphs = doc.paragraphs[start_idx:end_idx]
    #
    # check_numid_isolation(doc, "22", start_idx, end_idx)  # do this BEFORE deciding
    # H1_NUMID = H2_NUMID = "22"  # if isolated; else H1_NUMID = H2_NUMID = clone_isolated_abstract(doc, "116", font=FONT)
    #
    # insert_h1("Your Section")
    # insert_h2("A Screen")
    # insert_body("From this screen you will be able to...")
    # insert_image("your-screen_01_list.png")
    # insert_field("Code*", "Required.")
    # insert_image("your-screen_02_create-form.png")
    #
    # for p in old_paragraphs:
    #     p._p.getparent().remove(p._p)
    #
    # doc.save(DST)
