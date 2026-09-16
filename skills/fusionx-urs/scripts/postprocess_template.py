"""
Post-processing template for LOLC URS .docx files generated via docx-js (generate.js/main.js/
content*.js) — run this AFTER node generation, before delivery. Fixes structural gaps docx-js
cannot produce natively. Copy into the project's build/ folder as postprocess.py, along with
theme1.xml from this same scripts/ folder, and adjust only the DOCX_PATH default below (or pass
the path as argv[1]) — everything else is generic and should not need rewriting per project.

Usage: python postprocess.py <path-to-generated.docx>

Full rationale for every fix below lives in references/docx-formatting.md — read it before changing
any of this. Each fix here exists because a specific, confirmed real defect was found (via direct
Word-COM measurement, not assumption); don't remove one because it "looks unnecessary" without
re-testing.

Required companion step for any document with a Table of Content: get_page_numbers.ps1 +
patch_page_numbers.py (this same scripts/ folder) MUST run after this script, via a read-only
Word-COM pass, before delivery — this script alone can only fill the ToC/LoF/LoT cache with a
placeholder page number, since real pagination requires an actual layout engine (Word), which
nothing in this pipeline has. See docx-formatting.md's "Table of Content / List of Figures / List
of Tables must be genuine, live, updatable Word fields" section.

IMPORTANT: if this script changes anything that affects page layout (as the table-padding fixes
below do), pagination shifts and any previously-computed page-number mapping becomes stale — always
run get_page_numbers.ps1 fresh AFTER this script's final output is in place, not before.
"""
import zipfile, os, sys, re

path = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "OUTPUT_FILENAME_HERE.docx"
)

with zipfile.ZipFile(path) as z:
    doc = z.read("word/document.xml").decode("utf-8")
    footer = z.read("word/footer1.xml").decode("utf-8")
    header = z.read("word/header1.xml").decode("utf-8")
    header_rels = z.read("word/_rels/header1.xml.rels").decode("utf-8")
    styles = z.read("word/styles.xml").decode("utf-8")
    settings = z.read("word/settings.xml").decode("utf-8")
    app = z.read("docProps/app.xml").decode("utf-8")
    content_types = z.read("[Content_Types].xml").decode("utf-8")
    doc_rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    zip_namelist = z.namelist()

# --- word/theme/theme1.xml: docx-js emits NO theme part at all. Confirmed as the root cause of two
# separate defects: (1) any w:themeColor/w:themeFill reference (e.g. GridTable4-Accent3's header
# fill) resolves against Word's own built-in default Office theme instead of a real theme — that
# default theme's accent3 is GREEN, not the real files' grey; (2) with theme attributes present but
# no theme part, cell-margin inheritance for themed table styles can also fail to resolve (see the
# GridTable4-Accent3 tblCellMar note below). Inject a real theme1.xml (copy theme1.xml from this
# same scripts/ folder — extracted verbatim from a real reference file) rather than stripping theme
# attributes to work around its absence. ---
THEME_PATH = os.path.join(os.path.dirname(__file__), "theme1.xml")
if "word/theme/theme1.xml" not in zip_namelist:
    with open(THEME_PATH, "rb") as f:
        theme1_xml = f.read()
    if 'PartName="/word/theme/theme1.xml"' not in content_types:
        theme_override = (
            '<Override PartName="/word/theme/theme1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        )
        content_types = content_types.replace("</Types>", theme_override + "</Types>")
    if 'Target="theme/theme1.xml"' not in doc_rels:
        existing_ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', doc_rels)]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        theme_rel = (
            f'<Relationship Id="rId{next_id}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" '
            'Target="theme/theme1.xml"/>'
        )
        doc_rels = doc_rels.replace("</Relationships>", theme_rel + "</Relationships>")
    print("word/theme/theme1.xml: injected (was completely absent) + registered in [Content_Types].xml and document.xml.rels")
else:
    theme1_xml = None

# --- docProps/app.xml: docx-js leaves Application/LinksUpToDate empty; real files have them set ---
if '<Application>' not in app:
    extra = ('<Application>Microsoft Office Word</Application>'
             '<DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop>'
             '<LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc>'
             '<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>')
    if app.rstrip().endswith('/>'):
        app = re.sub(r'/>\s*$', '>' + extra + '</Properties>', app.rstrip())
    else:
        app = app.replace('</Properties>', extra + '</Properties>')
    print("docProps/app.xml: populated Application/LinksUpToDate (was empty)")

# --- styles.xml: GridTable4-Accent3 needs its full definition injected, including real theme
# attributes (not literal-color-only fallbacks — that was a workaround, superseded by the theme1.xml
# injection above) AND an explicit <w:tblCellMar> directly on its own tblPr. The tblCellMar is not
# optional polish: even with the style otherwise byte-identical to a real file's (confirmed by
# direct diff) and a real theme part present, a table styled "Grid Table 4 - Accent 3" still
# resolved 0pt cell padding via Word's own COM object model in this document, while the same style
# correctly resolves the real file's 5.4pt (inherited via TableNormal there). Root mechanism not
# fully understood — Word's built-in "Grid Table" style family does not reliably inherit tblCellMar
# through basedOn the way "Table Grid" does, even when definitions are otherwise identical to a real
# file that inherits it correctly. Ruled out first, confirmed to make no difference on their own:
# missing <w:pPr> (added, no effect — the "Table Grid" fix below needed this but this style already
# had it), the tblLook legacy w:val hex bitmask (added, no effect), w:cnfStyle on header row/cells
# (added, no effect). The explicit tblCellMar is what actually works — confirmed by direct
# before/after Word-COM Cell.LeftPadding measurement. Don't remove it as "redundant with
# TableNormal" without re-testing with an actual Cell.LeftPadding query, not just visual inspection
# or XML-structural checks (neither would catch this). ---
GRIDTABLE4_STYLE_XML = (
    '<w:style w:type="table" w:styleId="GridTable4-Accent3"><w:name w:val="Grid Table 4 Accent 3"/>'
    '<w:basedOn w:val="TableNormal"/><w:uiPriority w:val="49"/>'
    '<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:tblPr><w:tblStyleRowBandSize w:val="1"/><w:tblStyleColBandSize w:val="1"/>'
    '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
    '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar>'
    '<w:tblBorders>'
    '<w:top w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '<w:left w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '<w:right w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="C9C9C9" w:themeColor="accent3" w:themeTint="99"/>'
    '</w:tblBorders></w:tblPr>'
    '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/><w:color w:val="FFFFFF" w:themeColor="background1"/></w:rPr>'
    '<w:tblPr/><w:tcPr><w:tcBorders>'
    '<w:top w:val="single" w:sz="4" w:space="0" w:color="A5A5A5" w:themeColor="accent3"/>'
    '<w:left w:val="single" w:sz="4" w:space="0" w:color="A5A5A5" w:themeColor="accent3"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="A5A5A5" w:themeColor="accent3"/>'
    '<w:right w:val="single" w:sz="4" w:space="0" w:color="A5A5A5" w:themeColor="accent3"/>'
    '<w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tcBorders>'
    '<w:shd w:val="clear" w:color="auto" w:fill="A5A5A5" w:themeFill="accent3"/></w:tcPr></w:tblStylePr>'
    '<w:tblStylePr w:type="lastRow"><w:rPr><w:b/><w:bCs/></w:rPr><w:tblPr/><w:tcPr><w:tcBorders>'
    '<w:top w:val="double" w:sz="4" w:space="0" w:color="A5A5A5" w:themeColor="accent3"/>'
    '</w:tcBorders></w:tcPr></w:tblStylePr>'
    '<w:tblStylePr w:type="firstCol"><w:rPr><w:b/><w:bCs/></w:rPr></w:tblStylePr>'
    '<w:tblStylePr w:type="lastCol"><w:rPr><w:b/><w:bCs/></w:rPr></w:tblStylePr>'
    '<w:tblStylePr w:type="band1Vert"><w:tblPr/><w:tcPr>'
    '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED" w:themeFill="accent3" w:themeFillTint="33"/>'
    '</w:tcPr></w:tblStylePr>'
    '<w:tblStylePr w:type="band1Horz"><w:tblPr/><w:tcPr>'
    '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED" w:themeFill="accent3" w:themeFillTint="33"/>'
    '</w:tcPr></w:tblStylePr></w:style>'
)
if 'w:styleId="GridTable4-Accent3"' not in styles:
    assert styles.endswith("</w:styles>"), "unexpected styles.xml tail"
    styles = styles[:-len("</w:styles>")] + GRIDTABLE4_STYLE_XML + "</w:styles>"
    print("styles.xml: injected GridTable4-Accent3 table style definition")

# --- styles.xml: TOC1/TOC2/TableofFigures also need their definitions injected, same reason as
# GridTable4-Accent3 above — docx-js sets pStyle references but never defines the styles, so Word
# falls back to a generic built-in latent style missing the real file's TOC2 indent (ind left=220,
# the actual source of the visible "1." vs "1.1." indent step). Without this every ToC/LoF/LoT
# entry renders flush left regardless of level. ---
TOC_STYLES_XML = (
    '<w:style w:type="paragraph" w:styleId="TOC1"><w:name w:val="toc 1"/>'
    '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:autoRedefine/>'
    '<w:uiPriority w:val="39"/><w:unhideWhenUsed/>'
    '<w:pPr><w:spacing w:after="100"/></w:pPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="TOC2"><w:name w:val="toc 2"/>'
    '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:autoRedefine/>'
    '<w:uiPriority w:val="39"/><w:unhideWhenUsed/>'
    '<w:pPr><w:spacing w:after="100"/><w:ind w:left="220"/></w:pPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="TableofFigures"><w:name w:val="table of figures"/>'
    '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
    '<w:uiPriority w:val="99"/><w:unhideWhenUsed/>'
    '<w:pPr><w:spacing w:after="0"/></w:pPr></w:style>'
)
if 'w:styleId="TOC1"' not in styles:
    assert styles.endswith("</w:styles>"), "unexpected styles.xml tail"
    styles = styles[:-len("</w:styles>")] + TOC_STYLES_XML + "</w:styles>"
    print("styles.xml: injected TOC1/TOC2/TableofFigures style definitions")

# --- styles.xml: TableGrid needs its own definition injected too, same bug class, different
# symptom: with no definition present, Word's fallback for this by-name-resolved built-in style
# does not reliably pick up the real 108-twip (5.4pt) default cell margin inherited via TableNormal
# — confirmed by direct measurement (Word-COM PDF export + PyMuPDF bounding-box comparison): a real
# file's cell text sits 5.4pt from the cell's left border; this generator's undefined-TableGrid
# version measured ~0.6pt, functionally zero padding. check_no_cell_margins() cannot catch this — it
# only confirms no EXPLICIT tcMar/tblCellMar override exists; it can't detect that the IMPLICIT
# default margin isn't being inherited at all. Inject verbatim (borders only — no tcMar of its own;
# the margin comes purely from the basedOn=TableNormal chain, which works correctly for this
# specific style family once TableGrid itself is present). ---
TABLEGRID_STYLE_XML = (
    '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
    '<w:basedOn w:val="TableNormal"/><w:uiPriority w:val="59"/>'
    '<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
    '<w:tblPr><w:tblBorders>'
    '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
    '</w:tblBorders></w:tblPr></w:style>'
)
if 'w:styleId="TableGrid"' not in styles:
    assert styles.endswith("</w:styles>"), "unexpected styles.xml tail"
    styles = styles[:-len("</w:styles>")] + TABLEGRID_STYLE_XML + "</w:styles>"
    print("styles.xml: injected TableGrid table style definition")

# --- styles.xml: TableNormal (the actual foundational "w:default=1" table style everything else is
# basedOn) must also be injected — without it there is nothing for TableGrid (or any other style) to
# inherit real cell padding from, regardless of which named style is referenced. Its own tblCellMar
# (top=0, left=108, bottom=0, right=108 twips = 5.4pt) is the true source of every real table's
# default cell padding. Injecting this fixes TableGrid-styled tables completely on its own;
# GridTable4-Accent3 needed its own explicit tblCellMar too (see above) despite also being
# basedOn=TableNormal — inherited padding through this specific built-in style family did not
# reliably resolve even with TableNormal present and correct. ---
TABLENORMAL_STYLE_XML = (
    '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/>'
    '<w:uiPriority w:val="99"/><w:semiHidden/><w:unhideWhenUsed/>'
    '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar>'
    '<w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
    '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/>'
    '</w:tblCellMar></w:tblPr></w:style>'
)
if 'w:styleId="TableNormal"' not in styles:
    assert styles.endswith("</w:styles>"), "unexpected styles.xml tail"
    styles = styles[:-len("</w:styles>")] + TABLENORMAL_STYLE_XML + "</w:styles>"
    print("styles.xml: injected TableNormal table style definition (the actual source of real cell padding)")

# --- document.xml: docx-js emits <w:tblLook> with only the newer boolean attributes (w:firstRow=
# "true" etc, ST_OnOff "true"/"false"), while every real file's tblLook also carries the legacy hex
# bitmask (w:val="04A0" style) and uses "1"/"0" for the booleans. Does not by itself fix cell
# padding (tested in isolation, no effect — see the GridTable4-Accent3 tblCellMar note above for the
# actual padding fix) but it's a real, confirmed structural gap worth closing on its own merits —
# every real reference file has the legacy attribute. ---
def fix_tbllook(text, label):
    pat = re.compile(
        r'<w:tblLook w:firstRow="(true|false)" w:lastRow="(true|false)" '
        r'w:firstColumn="(true|false)" w:lastColumn="(true|false)" '
        r'w:noHBand="(true|false)" w:noVBand="(true|false)"/>'
    )
    def repl(m):
        vals = [1 if g == "true" else 0 for g in m.groups()]
        first_row, last_row, first_col, last_col, no_h, no_v = vals
        # Verified against a real file's own tblLook (w:val="04A0" for firstRow=1, lastRow=0,
        # firstColumn=1, lastColumn=0, noHBand=0, noVBand=1): 0x04A0 = 0x0400(noVBand) +
        # 0x0080(firstColumn) + 0x0020(firstRow) — confirms these exact bit positions, not guessed.
        bitmask = (first_row * 0x0020) | (last_row * 0x0040) | (first_col * 0x0080) \
                  | (last_col * 0x0100) | (no_h * 0x0200) | (no_v * 0x0400)
        return (
            f'<w:tblLook w:val="{bitmask:04X}" w:firstRow="{first_row}" w:lastRow="{last_row}" '
            f'w:firstColumn="{first_col}" w:lastColumn="{last_col}" w:noHBand="{no_h}" w:noVBand="{no_v}"/>'
        )
    new_text, count = pat.subn(repl, text)
    print(f"{label}: normalized {count} tblLook element(s) to include the legacy w:val bitmask (matches real files)")
    return new_text

doc = fix_tbllook(doc, "document.xml")

# --- header1.xml: docx-js's relationship-ID generator can start at rId0 instead of rId1 when the
# header has only one relationship (e.g. a single logo image). Word does not reliably open a file
# referencing rId0 at all ("Word experienced an error trying to open the file") — renumber. ---
if "rId0" in header:
    assert header.count('r:embed="rId0"') == 1, header.count('r:embed="rId0"')
    header = header.replace('r:embed="rId0"', 'r:embed="rId1"')
    assert header_rels.count('Id="rId0"') == 1, header_rels.count('Id="rId0"')
    header_rels = header_rels.replace('Id="rId0"', 'Id="rId1"')
    print("header1.xml / header1.xml.rels: renumbered rId0 -> rId1")

# --- document.xml / footer1.xml: docx-js's SimpleField (PAGE/NUMPAGES/SEQ/DOCPROPERTY) emits
# <w:fldSimple> nested inside a <w:r>, which is invalid OOXML (fldSimple may only be a direct child
# of w:p or w:hyperlink). Word tolerates it on open but rebuilds the displayed run from default
# formatting on recalculation — confirmed via Word-COM PDF export: a footer's DOCPROPERTY Title
# field rendered in default black body text instead of its intended small muted-grey style, a
# defect invisible to any XML-only check. Rewrite every fldSimple-in-run into the real file's own
# shape: explicit begin/instrText/separate/text/end run sequence, each run carrying its own matching
# rPr, all as direct paragraph siblings. ---
RPR = r'<w:rPr>(?:(?!</w:rPr>).)*?</w:rPr>'
fld_pat = re.compile(
    r'<w:r>(?:' + RPR + r')?<w:fldSimple w:instr="([^"]*)">'
    r'(?:<w:r>(?:' + RPR + r')?<w:t([^>]*)>((?:(?!</w:t>).)*?)</w:t></w:r>)?'
    r'</w:fldSimple></w:r>', re.S)

def patch(text, rpr, label):
    def repl(m):
        instr, t_attrs, value = m.group(1), m.group(2) or ' xml:space="preserve"', m.group(3) or ""
        return (
            f'<w:r><w:rPr>{rpr}</w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:t{t_attrs}>{value}</w:t></w:r>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
        )
    new_text, count = fld_pat.subn(repl, text)
    print(f"{label}: rewrote {count} fldSimple-in-run field(s) into explicit fldChar sequences")
    return new_text

# Adjust these two rPr strings to match this project's actual caption/footer formatting.
CAPTION_RPR = ('<w:rFonts w:ascii="Candara" w:hAnsi="Candara" w:cs="Candara" w:eastAsia="Candara"/>'
               '<w:i/><w:iCs/><w:color w:val="44546A"/><w:sz w:val="18"/><w:szCs w:val="18"/>')
FOOTER_RPR = ('<w:rFonts w:ascii="Candara" w:hAnsi="Candara" w:cs="Candara" w:eastAsia="Candara"/>'
              '<w:color w:val="8496B0"/><w:sz w:val="18"/><w:szCs w:val="18"/>')

doc = patch(doc, CAPTION_RPR, "document.xml")
footer = patch(footer, FOOTER_RPR, "footer1.xml")

# --- document.xml: docx-js's Table constructor defaults `borders` to {} (truthy) when omitted, so
# it always emits a default <w:tblBorders> even when none was requested — this silently overrides a
# named table style's own borders (direct formatting beats style in the OOXML cascade). Strip the
# default tblBorders only from tables using GridTable4-Accent3 (which should rely on the style's own
# C9C9C9 borders); leave TableGrid/PlainTable1-styled tables, which DO want an explicit override,
# untouched. ---
def strip_default_borders(text, label):
    count = 0
    def repl(m):
        nonlocal count
        tblpr = m.group(0)
        if "GridTable4-Accent3" not in tblpr:
            return tblpr
        count += 1
        return re.sub(r'<w:tblBorders>.*?</w:tblBorders>', '', tblpr, flags=re.S)
    new_text = re.sub(r'<w:tblPr>.*?</w:tblPr>', repl, text, flags=re.S)
    print(f"{label}: stripped default tblBorders from {count} GridTable4-Accent3 table(s)")
    return new_text

doc = strip_default_borders(doc, "document.xml")

# =================================================================================================
# Table of Content / List of Figures / List of Tables: bookmark every heading/caption, fill the
# fields' cache with real entries, keep the fields genuinely live and updatable.
#
# Full history and reasoning: docx-formatting.md, "Table of Content / List of Figures / List of
# Tables must be genuine, live, updatable Word fields". Do not strip the outer field to static text
# — explicit, repeated user requirement is that right-click > Update Field must work after future
# edits, same as a TOC inserted by hand in Word. Two things needed fixing, both compatible with
# staying live: (1) docx-js wraps the field in a <w:sdt> content control a native Word TOC field
# never has; strip only that wrapper. (2) the field's w:dirty="true" flag is only correct while the
# cache is empty/stale — clear it once the cache below is genuinely filled with real content, never
# before (clearing it while the cache is still a placeholder breaks auto-population entirely).
# =================================================================================================
with zipfile.ZipFile(path) as z:
    num_bytes = z.read("word/numbering.xml")
import xml.etree.ElementTree as ET
Wns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
num_root = ET.fromstring(num_bytes)
numid_to_abs = {}
for n in num_root.findall(f"{Wns}num"):
    ref = n.find(f"{Wns}abstractNumId")
    if ref is not None:
        numid_to_abs[n.get(f"{Wns}numId")] = ref.get(f"{Wns}val")
level_start = {}
for absnum in num_root.findall(f"{Wns}abstractNum"):
    absid = absnum.get(f"{Wns}abstractNumId")
    for lvl in absnum.findall(f"{Wns}lvl"):
        start_el = lvl.find(f"{Wns}start")
        level_start[(absid, lvl.get(f"{Wns}ilvl"))] = int(start_el.get(f"{Wns}val")) if start_el is not None else 1

FRONT_MATTER_LABELS = {"Table of Content", "List of Figures", "List of Tables"}
PARA_PAT = re.compile(r'<w:p(?:\s[^>]*)?(?<!/)>.*?</w:p>', re.S)

counters = {}  # numId -> [level0_count, level1_count]
def numbered_text(numid, ilvl, text):
    absid = numid_to_abs.get(numid)
    key0 = (absid, "0")
    if numid not in counters:
        counters[numid] = [level_start.get(key0, 1) - 1, 0]
    c = counters[numid]
    if ilvl == "0":
        c[0] += 1
        c[1] = level_start.get((absid, "1"), 1) - 1
        return f"{c[0]}. {text}"
    else:
        c[1] += 1
        return f"{c[0]}.{c[1]}. {text}"

bookmark_id = [0]
def next_bookmark():
    bookmark_id[0] += 1
    return f"_Toc{bookmark_id[0]}"

toc_entries = []   # (bookmark, style_level, display_text)
lof_entries = []   # (bookmark, display_text)
lot_entries = []   # (bookmark, display_text)

def get_text(frag):
    return "".join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', frag))

def wrap_with_bookmark(frag, name):
    bid = bookmark_id[0]
    bm_start = f'<w:bookmarkStart w:id="{bid}" w:name="{name}"/>'
    bm_end = f'<w:bookmarkEnd w:id="{bid}"/>'
    ppr_m = re.search(r'</w:pPr>', frag)
    insert_at = ppr_m.end() if ppr_m else frag.index(">") + 1
    frag = frag[:insert_at] + bm_start + frag[insert_at:]
    close_idx = frag.rindex("</w:p>")
    frag = frag[:close_idx] + bm_end + frag[close_idx:]
    return frag

# Adjust the caption-detection color ("44546A") if this project's captions use a different color.
def classify_and_bookmark(m):
    frag = m.group(0)
    text = get_text(frag).strip()
    if not text:
        return frag
    style_m = re.search(r'<w:pStyle w:val="(Heading1|Heading2)"/>', frag)
    is_caption = ('w:val="44546A"' in frag and "<w:i/>" in frag
                  and (text.startswith("Figure ") or text.startswith("Table ")))
    if style_m:
        name = next_bookmark()
        style_level = style_m.group(1)
        if text in FRONT_MATTER_LABELS:
            display = text
        else:
            numpr_m = re.search(r'<w:numPr><w:ilvl w:val="(\d)"/><w:numId w:val="(\d+)"/></w:numPr>', frag)
            if numpr_m:
                display = numbered_text(numpr_m.group(2), numpr_m.group(1), text)
            else:
                display = text
        toc_entries.append((name, style_level, display))
        return wrap_with_bookmark(frag, name)
    if is_caption:
        name = next_bookmark()
        (lof_entries if text.startswith("Figure ") else lot_entries).append((name, text))
        return wrap_with_bookmark(frag, name)
    return frag

doc = PARA_PAT.sub(classify_and_bookmark, doc)
print(f"document.xml: added {len(toc_entries)} heading + {len(lof_entries)} figure + {len(lot_entries)} table bookmark(s)")

# Every run here MUST carry explicit w:ascii/w:hAnsi (not just w:cs) — a real file's own cache only
# sets w:cs, which is not enough for this skill's own check_fonts().
TAB_XML = '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9016"/></w:tabs>'
def entry_paragraph(style, anchor, display):
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{TAB_XML}<w:rPr><w:noProof/></w:rPr></w:pPr>'
        f'<w:hyperlink w:anchor="{anchor}" w:history="1">'
        f'<w:r><w:rPr><w:rFonts w:ascii="Candara" w:hAnsi="Candara" w:cs="Candara" w:eastAsia="Candara"/><w:noProof/><w:color w:val="000000"/></w:rPr><w:t xml:space="preserve">{display}</w:t></w:r>'
        f'<w:r><w:rPr><w:noProof/><w:webHidden/></w:rPr><w:tab/></w:r>'
        f'<w:r><w:rPr><w:noProof/><w:webHidden/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r><w:rPr><w:noProof/><w:webHidden/></w:rPr><w:instrText xml:space="preserve"> PAGEREF {anchor} \\h </w:instrText></w:r>'
        f'<w:r><w:rPr><w:noProof/><w:webHidden/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r><w:rPr><w:rFonts w:ascii="Candara" w:hAnsi="Candara" w:cs="Candara" w:eastAsia="Candara"/><w:noProof/><w:webHidden/></w:rPr><w:t>1</w:t></w:r>'
        f'<w:r><w:rPr><w:noProof/><w:webHidden/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
        f'</w:hyperlink></w:p>'
    )

toc_cache = "".join(entry_paragraph("TOC1" if lvl == "Heading1" else "TOC2", a, d) for a, lvl, d in toc_entries)
lof_cache = "".join(entry_paragraph("TableofFigures", a, d) for a, d in lof_entries)
lot_cache = "".join(entry_paragraph("TableofFigures", a, d) for a, d in lot_entries)

EMPTY_CACHE_PAT = re.compile(r'(<w:fldChar w:fldCharType="separate"/></w:r></w:p>)(<w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>)')
def fill_caches(text):
    order = [toc_cache, lof_cache, lot_cache]
    idx = [0]
    def repl(m):
        i = idx[0]
        idx[0] += 1
        cache = order[i] if i < len(order) else ""
        return m.group(1) + cache + m.group(2)
    return EMPTY_CACHE_PAT.sub(repl, text)
doc = fill_caches(doc)
print("document.xml: filled TOC/LoF/LoT field caches with real hyperlink+PAGEREF entries")

# Strip docx-js's <w:sdt> content-control wrapper (a native Word TOC field never has one), clear
# the now-stale-no-more w:dirty flag, and fold the field's begin/instrText/separate (docx-js puts
# these in their own bare, <w:t>-less paragraph before the first entry) into the FIRST entry
# paragraph, and its lone end fldChar (own bare paragraph after the last entry) into the LAST entry
# paragraph — eliminates two paragraphs that would otherwise render as unexplained blank lines and
# get flagged by check_front_matter's spacer-counting.
SDT_PAT = re.compile(
    r'<w:sdt><w:sdtPr><w:alias w:val="[^"]*"/></w:sdtPr><w:sdtContent>(.*?)</w:sdtContent></w:sdt>',
    re.S,
)
FIRST_FIELD_PARA_PAT = re.compile(
    r'^<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/>'
    r'<w:instrText([^>]*)>([^<]*)</w:instrText>'
    r'<w:fldChar w:fldCharType="separate"/></w:r></w:p>'
)
LAST_FIELD_PARA = '<w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'

def merge_field_boundaries(m):
    body = m.group(1)
    fm = FIRST_FIELD_PARA_PAT.match(body)
    if not fm:
        return m.group(0)
    instr_attrs, instr_text = fm.group(1), fm.group(2)
    body = body[fm.end():]
    begin_runs = (
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r><w:instrText{instr_attrs}>{instr_text}</w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    )
    body, n = re.subn(r'</w:pPr>', lambda pm: pm.group(0) + begin_runs, body, count=1)
    # docx-js 9.7 can emit the first cached ToC entry without a pPr element. The
    # older build this script was originally paired with always emitted one, but
    # that is not an OOXML requirement. Create an empty pPr and anchor the live
    # field immediately after it; otherwise a clean install fails before QC.
    if n == 0:
        body, n = re.subn(
            r'(<w:p(?:\s[^>]*)?>)',
            lambda pm: pm.group(1) + '<w:pPr/>' + begin_runs,
            body,
            count=1,
        )
    assert n == 1, "could not locate first ToC entry paragraph to anchor the field begin"
    if body.endswith(LAST_FIELD_PARA):
        body = body[: -len(LAST_FIELD_PARA)]
        end_run = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        last_close = body.rindex("</w:p>")
        body = body[:last_close] + end_run + body[last_close:]
    return body

sdt_count_before = doc.count("<w:sdt>")
doc = SDT_PAT.sub(merge_field_boundaries, doc)
print(f"document.xml: unwrapped {sdt_count_before} TOC/LoF/LoT content-control(s), merged field begin/end markers into first/last entry paragraphs, cleared dirty flag — field(s) remain live and updatable")

tmp = path + ".tmp"
with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = doc.encode("utf-8")
        elif item.filename == "word/footer1.xml":
            data = footer.encode("utf-8")
        elif item.filename == "word/header1.xml":
            data = header.encode("utf-8")
        elif item.filename == "word/_rels/header1.xml.rels":
            data = header_rels.encode("utf-8")
        elif item.filename == "word/styles.xml":
            data = styles.encode("utf-8")
        elif item.filename == "word/settings.xml":
            data = settings.encode("utf-8")
        elif item.filename == "docProps/app.xml":
            data = app.encode("utf-8")
        elif item.filename == "[Content_Types].xml":
            data = content_types.encode("utf-8")
        elif item.filename == "word/_rels/document.xml.rels":
            data = doc_rels.encode("utf-8")
        zout.writestr(item, data)
    if theme1_xml is not None:
        zout.writestr("word/theme/theme1.xml", theme1_xml)
os.replace(tmp, path)
print("applied to", path)
print()
print("REQUIRED NEXT STEP: run get_page_numbers.ps1 then patch_page_numbers.py (this same scripts/")
print("folder) via a read-only Word-COM pass before delivery — the ToC/LoF/LoT page numbers above")
print("are still placeholders.")
