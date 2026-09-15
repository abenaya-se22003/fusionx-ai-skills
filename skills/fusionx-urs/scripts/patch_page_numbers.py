import zipfile, re, os, sys

# Real page numbers for the ToC/LoF/LoT PAGEREF cache can only come from an actual layout
# engine (Word) — nothing in generate.js/main.js/content*.js/postprocess.py can know where a
# paragraph lands on a page. postprocess.py fills the cache with placeholder "1" for every
# entry; this script is the required second phase: read real per-bookmark page numbers computed
# by Word (via Word-COM, .Fields.Update(), NO .Save() on the docx — see docx-formatting.md's
# Word-COM warning) and patch them into the already-generated file in place.
#
# Usage: python patch_page_numbers.py <docx_path> <mapping_file>
# mapping_file: one "_TocN=page" per line — produce it with get_page_numbers.ps1 in this same
# scripts/ folder, then run this script.

path = os.path.abspath(sys.argv[1])
mapping_file = sys.argv[2]

pagerefs = {}
with open(mapping_file, encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line or "=" not in line:
            continue
        anchor, val = line.split("=", 1)
        pagerefs[anchor.strip()] = val.strip()

with zipfile.ZipFile(path) as z:
    doc = z.read("word/document.xml").decode("utf-8")

HYPERLINK_PAT = re.compile(
    r'<w:hyperlink w:anchor="(?P<anchor>_Toc\d+)"[^>]*>.*?</w:hyperlink>', re.S
)
PLACEHOLDER_PAT = re.compile(
    r'(<w:fldChar w:fldCharType="separate"/></w:r><w:r><w:rPr>.*?</w:rPr><w:t>)1(</w:t>)',
    re.S,
)

patched = 0
missing = []

def patch_block(m):
    global patched
    anchor = m.group("anchor")
    block = m.group(0)
    if anchor not in pagerefs:
        missing.append(anchor)
        return block
    real = pagerefs[anchor]
    new_block, n = PLACEHOLDER_PAT.subn(lambda pm: pm.group(1) + real + pm.group(2), block, count=1)
    if n == 1:
        patched += 1
        return new_block
    return block

doc = HYPERLINK_PAT.sub(patch_block, doc)

if missing:
    print(f"WARNING: {len(missing)} anchor(s) in the document had no real page number supplied: {missing}")
print(f"document.xml: patched {patched} ToC/LoF/LoT entries with real Word-computed page numbers")

tmp = path + ".tmp"
with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            data = doc.encode("utf-8")
        zout.writestr(item, data)
os.replace(tmp, path)
print("applied to", path)
