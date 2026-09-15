# LOLC URS Format Standard
*Derived from four real LOLC files inspected at the raw .docx XML level, cross-checked against
each other rather than any single sample: Transaction Reversal – Interest Rollback URS V1.0
(most authoritative — furthest toward sign-off), the blank XX-Module and Master templates
(structural skeleton), and the Lending Module V0.1 draft (content-quality exemplar, but an early
draft, so some of its shortcuts — e.g. simplified table columns — are noted as draft-stage
variance rather than the target format). Where the V0.1 draft and the V1.0/template sources
disagreed, V1.0 and the templates won; those forks are called out explicitly below rather than
silently resolved, since a future pass with more samples may need to revisit them.*
*This is the authoritative LOLC URS format — always match this exactly, including the
formatting rules in the second half of this file, not just the section structure.*

---

## COVER PAGE (exact layout)

```
Proprietary and Confidential                              [LOLC logo, top-right of header]

[Module Name] – [Feature Title]

User Story Document

User Story for [Full Feature Name]

| Document Version | 1.0       |
| Release Date     | DD/MM/YYYY |
| Number of Pages  | [n]       |

LOLC Technologies
137, Rajagiriya Road, Rajagiriya. 10100
```

**Notes from the sample:**
- Header line always: "Proprietary and Confidential", centered, light grey, on every page
- Title: "[Module] – [Feature]" — large, blue, single rule beneath it
- Sub-title: "User Story Document"
- Sub-sub-title: "User Story for [Feature Name]"
- Version table uses a simple 2-column format: field | value, light-blue fill on the label column
- Company address: **137, Rajagiriya Road, Rajagiriya. 10100** — this is the current address.
  An older address ("852 Kotte Rd, Sri Jayawardenepura Kotte") appears in older URS samples and
  is now outdated; do not use it.
- Footer on every page (borderless 2-column table, not a tabbed paragraph): left = "User " + a
  live FILENAME field (not a hardcoded version string), right = "Page " + live PAGE field + " | "
  + live NUMPAGES field. ~10pt, muted grey-blue (`8496B0`/`222A35`).

---

## TABLE OF CONTENTS (exact section numbering)

```
[Module Name] – [Feature Title]                              [page]
Table of Content                                              [page]
List of Figures                                               [page]
List of Tables                                                [page]
1.    Document Control                                        [page]
1.1.  Document Information                                    [page]
1.2.  Revision History                                        [page]
1.3.  Definitions and Acronyms                                [page]
1.4.  Assumptions                                              [page]
1.5.  Risks                                                    [page]
1.6.  General Guide Line                                      [page]
2.    Open Questions                                           [page]
3.    Overview/Project Description                            [page]
4.    Flow Chart                                                [page]
5.    Scope                                                     [page]
5.1   What is in scope                                          [page]
5.2.  What is out of scope                                      [page]
6.    Epic: Narrative and Statement                             [page]
7.    Features/Stories                                          [page]
      7.1.  Story 01 ([Story Title])                            [page]
      7.2.  Story 02 ([Story Title], if applicable)              [page]
7.    Data Dictionary                                            [page]
8.    E2E Impact Identification Table                            [page]
9.    Diagrams and Examples                                      [page]
10.   Annexure                                                   [page]
11.   Test Scenarios                                             [page]
```

**Key observations (confirmed independently in two real files — Transaction Reversal V1.0 and the
Lending V0.1 draft — this is the current, correct numbering; do not "fix" it):**
- Section "7." appears twice: once for Features/Stories, once for Data Dictionary. Confirmed at
  the XML level in Transaction Reversal V1.0: the document numbers sections 1–7 (through
  Features/Stories) using one multilevel list (`numId=1`), then Data Dictionary onward using a
  *second*, independent multilevel list (`numId=13`) whose level-0 `w:start` is hardcoded to `7`
  in that file's `numbering.xml` — a real, mechanical quirk baked into the LOLC master template's
  numbering definitions, not a typo. **The start value is not always 7** — cross-checked against
  the Lending V0.1 draft, which has no standalone Flow Chart section, so its Features/Stories
  lands on section 6, and its second list's `w:start` is hardcoded to `6` to match. The rule is:
  the second list's start value always equals whatever number Features/Stories received in that
  specific document — reproduce it structurally (two real multilevel-list definitions, heading
  numbering not typed digits), with the second one's start value set to match Features/Stories'
  actual number, not a hardcoded 7.
- Story sub-numbering is the real section number, e.g. "7.1.", "7.2." — there is no legacy
  "6.1./6.2." numbering in the current format. (Older URS samples used "6.1." as a legacy
  artifact; that convention is retired — don't use it in new documents.)
- Section 1.6 "General Guide Line" is a required section — a 3-column guideline table distinct
  from Assumptions and Risks.
- Section 8 "E2E Impact Identification Table" is its own numbered section with a named,
  structured 3-column table — not folded into prose or left to the writer's judgment on shape.
- "List of Figures" and "List of Tables" are both required, immediately after the main Table of
  Contents, each listing captioned figures/tables with page numbers (e.g. "Figure 1 - Flowchart",
  "Table 1 - Data Dictionary", "Table 2 - E2E Impact Identification").
- "Table of Content", "List of Figures", and "List of Tables" never carry a section number
  themselves and always sit before Section 1's numbered sequence begins — a reported defect had
  "Table of Content" rendered as a numbered `1.1.` sub-heading under Document Control instead.
  Entries inside all three are real Word `TOC` fields (updatable, not typed dot-leader text) but
  render in plain text color, not the blue/underlined `Hyperlink` styling real samples use —
  explicit user decision, kept deliberately different from the samples here. See
  `docx-formatting.md`'s dedicated section for the full XML-verified detail.

### Front-matter spacing — reported defect, root-caused and verified against 3 independent sources

**A user reported wrong spacing in the ToC table, and between Table of Contents/List of
Figures/List of Tables.** Traced to a real, concrete defect in one source file, and confirmed
correct in three others — the blank XX-Module template, the blank Master template, and
Transaction Reversal V1.0 all independently agree on the exact same shape:

```
Table of Content  [Heading1]
  ↳ ToC field                          ← 0 empty paragraphs before next heading
List of Figures  [Heading1]
  ↳ field entries (Figure 1, Figure 2, ...)
  ↳ 1 empty paragraph                  ← the field's own closing-character artifact, not a manual Enter
List of Tables  [Heading1]             ← 0 empty paragraphs before this heading
  ↳ field entries (Table 1, Table 2, ...)
  ↳ 1 empty paragraph                  ← same artifact
  ↳ 2 empty paragraphs                 ← fixed small buffer before the next real section starts
Section 1 (Document Control / Document Information)
```

Every heading transition (ToC→List of Figures, List of Figures→List of Tables) has **zero** blank
paragraphs between them — they rely only on the heading style's own `spacing before="240"` twips
(12pt). The **only** blank paragraphs that belong in this region are: exactly one after each
field's entries (an artifact of where the field's closing character lives, not something you
insert deliberately), plus a fixed 2-paragraph buffer after the very last one, before the next
real section. That's the complete, non-arbitrary rule — not "roughly some spacing," a specific,
countable shape confirmed three ways.

**Lending V0.1 draft (the one defect, do not copy):** between the ToC field and `List of Figures`,
it has **eight** stacked empty paragraphs instead of zero — three carrying `Heading1` style, five
plain — almost certainly someone repeatedly pressing Enter while editing. It also **omits "List of
Tables" entirely.** Treat both as confirmed defects in that one draft, not a second valid pattern
to weigh against the other three sources.

**Always include List of Tables** — it's a required section (same as List of Figures), using the
same `TableofFigures` paragraph style but with the TOC field's category switch set to `\c "Table"`
instead of `\c "Figure"`, listing `Table 1 - Data Dictionary` and `Table 2 - E2E Impact
Identification` with page references.

**Entry spacing within each list (ToC entries, List of Figures/Tables entries):** confirmed from
`styles.xml` — `TOC1`/`TOC2`/`TOC3` use `spacing after="100"` twips (5pt) between entries;
`TableofFigures` uses `spacing after="0"` (entries sit flush against each other, no extra gap).
Don't add manual spacing between individual entries in either list — the style's built-in value is
already correct and is what a real Word-generated TOC/List-of-Figures field produces automatically
when using the native field, not a bullet or manual list.

---

## SECTION-BY-SECTION FORMAT

### Section 1.1 — Document Information

```
| Drafted By      | [BA Name]                  |
| Reviewed By     | [Name, or blank]            |
| Document Status | Draft                        |
| Client Name     | LOLC Technologies Pvt LTD    |
| Circulation     | Internal                     |
```
Note: "Pvt LTD" (not "Pvt Ltd") matches the sample's exact capitalization in this table; the
cover page and footer company name is just "LOLC Technologies" without a suffix.

### Section 1.2 — Revision History

```
| Revision Date | Updated By  | Version | Section(s) | Description   |
| YYYY-MM-DD    | [BA Name]   | 0.1     | All        | Initial Draft |
|               |             |         |            |               |
```
Note: the sample uses ISO-style `YYYY-MM-DD` in the Revision History date column specifically
(distinct from the DD/MM/YYYY used everywhere else in the document, including the cover page).
Match this — it's a real, deliberate distinction in the source, not an inconsistency to smooth over.

### Section 1.3 — Definitions and Acronyms

Simple 2-column table: Acronym | Definition
- Include only acronyms relevant to the scope
- No header row — just rows
- Exception, confirmed in a real sample: when the feature genuinely introduces no new
  acronyms/terms beyond common ones already covered elsewhere, plain text "N/A" (no table at all)
  is acceptable — don't force an empty or single-row table.
- Example format from the sample:
  ```
  | URS | User Requirement Specification |
  | UI  | User Interface                 |
  | CBS | Core Banking System             |
  | EOM | End of Month                    |
  ```

### Section 1.4 — Assumptions

Plain bullet list — confirmed real `w:numPr` bullet formatting (`numFmt="bullet"`, Wingdings `•`,
own list independent of the heading numbering), not decimal sub-numbers. (A tie-break note: one
real V0.1 draft used decimal sub-numbers like `1.4.1.` for this section specifically; the V1.0
sample's plain-bullet treatment — applied uniformly across Assumptions, Risks, Scope, and Test
Scenarios alike — is the more authoritative, internally-consistent convention and is what's
documented here.) Each assumption is a complete sentence. Examples from a real sample:
- "The account involved is Active and not in a restricted/dormant state at the time of reversal."
- "Standard maker-checker (dual authorization) is enforced on all Transaction Group Reversals, as
  per the existing Create Group Reversal / Confirm Group Reversal workflow."

### Section 1.5 — Risks

Same plain-bullet mechanism as Assumptions. Each risk is a sentence describing what could go
wrong. Examples from a real sample:
- "If the interest recalculation window is not capped, very old reversals could trigger
  recalculation across multiple already-closed accounting periods, causing reconciliation and
  audit complications."
- "WHT already deducted and remitted on capitalized credit interest may require separate
  tax-adjustment handling outside FusionX, which is a dependency risk."

### Section 1.6 — General Guide Line

3-column table: Category | Guideline / Comment | Applicability / Notes
Generate rows specific to the feature being documented — confirmed from the V1.0 sample, whose 6
rows (Maker-Checker Control, Blocking Consistency, No New GL Codes, Applicability, Audit &
Traceability, No UI Change) are entirely feature-specific, not boilerplate. Typical categories:
existing-functionality preservation, effective-date control, master data validation, range
validation, cycle/calendar validation, frequency handling, financial integrity, validation
messaging, audit & traceability, security & authorization, EOD/batch alignment, cross-UI system
consistency.

**Caution:** the blank org templates ship with a 7-row generic placeholder (Data Management,
Search, Input Validation, Workflow & Approvals, Audit & Traceability, Reporting & Dashboards,
Consistency & Usability). The V0.1 Lending draft left this exact placeholder text unedited —
it's a real gap seen in a real draft, not a valid alternative convention. Always replace it with
feature-specific rows; never leave the template placeholder text as the final content.

---

### Section 2 — Open Questions

```
| # | Date | Question | Owner | Status |
|---|------|----------|-------|--------|
|   |      |          |       |        |
```
Leave blank rows if no open questions at time of drafting. Give the "Question" column the most
width of the five — in the sample this table's columns were too narrow and "Status" wrapped
awkwardly onto two lines; don't repeat that — see column-width guidance below.

---

### Section 3 — Overview/Project Description

2–4 sentences. Describe:
1. What the feature/module does
2. What data it processes
3. What it produces/outputs
4. The business value (compliance, efficiency, accuracy)

---

### Section 4 — Flow Chart

A real embedded flowchart image (not a text placeholder) under a centered italic caption (style `Caption`, `44546A`, 9pt — not bold)
`Figure 1 - Flowchart`. The sample's flowchart is a top-to-bottom decision-tree style diagram
(rounded/diamond decision nodes, rectangular action nodes) covering the feature's main
conditional logic. Generate an equivalent diagram for the feature being documented — use the
Visualizer's `diagram` module. Only use `[Flow chart to be attached]` if the feature truly has no
decision flow worth diagramming, and flag this explicitly to the user rather than silently
omitting the figure (a silently-skipped Figure 1 leaves the List of Figures page number wrong).

---

### Section 5 — Scope

#### 5.1 What is in scope
Bullet list. Each item is a specific deliverable or capability included.
Start each with an action noun: "Validation enhancements for...", "Effective date behavior rules
for...", "Multiple due date change handling for..."

#### 5.2 What is out of scope
Bullet list. Each item is explicitly excluded.
Example: "Introduction of new Due Date Types", "Manual repayment adjustments", "Changes to
historical posted transactions"

---

### Section 6 — Epic: Narrative and Statement

```
| [Module Name] – [Feature] | |
|---|---|
| Who    | As a [Role] |
| Needs  | [Capability, stated tersely] |
| Product | In [System/Module Name] |
| ROI    | [Business value: compliance, efficiency, accuracy, etc.] |
```
Note: "Needs" in the sample is terse ("Strong validations and predictable due date behaviour"),
not a full "To do X for Y to ensure Z" sentence — match the terse style.

---

### Section 7 — Features/Stories

#### Story Format (verified against two real stories — Transaction Reversal V1.0 Story 03,
Lending Module V0.1 Story 01 — cross-checked against each other):

Each story uses a 2-column table with exactly these 6 rows, **all 6 numbered:**

```
7.1.1.  User & Function
7.1.2.  Action
7.1.3.  Result
7.1.4.  Pre-Conditions
7.1.5.  Trigger
7.1.6.  Expected
```

**Correction — all 6 row labels are numbered, not just the first — and this is not a
template-vs-samples fork, all three sources agree.** The rule used to say only "User & Function"
gets a number, based on checking only the *visible text* of the two real generated samples — since
rows 2–6 showed no typed digits, they were assumed unnumbered. Checking `numPr` presence directly
shows that was wrong: **the Master Template, Lending, and Transaction Reversal all independently
carry real `numPr` on all 6 row labels**, incrementing sequentially in document order. The only
defect found anywhere in any of the three is Transaction Reversal's row 0, which has real `numPr`
*and* also types `7.1.1.` redundantly as literal text alongside it.

**Content columns are also numbered on every row, not just Action's.** The Master Template
pre-sets a numbered-list slot in every row's content column (`7.1.1.1`, `7.1.2.1`, ... one per
row), not only the multi-point Action cell. Every row's content gets at least one real numbered
point; rows with multiple distinct points (Action almost always; occasionally Result/Trigger) get
more than one, each its own numbered paragraph.

**Mechanism — verified three ways, no typed digits required anywhere:** Lending's and Transaction
Reversal's real generated documents both prove the row-label numbering works by continuing the
**same list already used for section headings**, one level deeper (`ilvl=2`) — real, working,
already-in-production on all 6 rows, not a hypothetical. The Master Template shows the clean
version with zero typed-digit noise: each row label is the next sequential use of that same level
(1→2→3→4→5→6 in document order: User & Function, Action, Result, Pre-Conditions, Trigger,
Expected), with each row's content column one level deeper still (`ilvl=3`), auto-resetting to 1
whenever the row-label level advances — Word does this automatically, no manual reset needed. See
`docx-formatting.md`'s row-label section for the full implementation recipe and level-by-level
list structure (level 0 = section, 1 = story, 2 = row 1–6, 3 = content point within that row).

**Sub-points inside a cell are a real Word multilevel list, not typed digits.** Where a cell needs
several distinct points (this is normal for Action, common for Result/Trigger), each point is its
own paragraph carrying genuine `w:numPr` list numbering — confirmed directly from a real Action
cell (Transaction Reversal Story 03: 7 separate paragraphs, each with `numPr` at `ilvl=3`,
rendering as `7.3.2.1.`, `7.3.2.2.` ... via a decimal multilevel list, `lvlText`
`%1.%2.%3.%4.`). The digits are **not** present as literal text anywhere in the file — Word
generates them from the list definition. See `docx-formatting.md`'s "Numbered sub-points inside
story cells" section for the exact generation recipe (real list definition + `numPr`, never typed
digit strings). Typing `"7.3.2.1.  System shall..."` as literal text is the single most likely
cause of reported indentation/renumbering defects — it can't reproduce Word's own hanging-indent
math for that level, and it doesn't renumber when a point is added, removed, or reordered.

Every row's content column gets at least one such numbered point — including Result,
Pre-Conditions, Trigger, and Expected, which often only need one — not just Action. A single-point
cell is still a level-3 numbered paragraph, not a plain unnumbered sentence.

- **User & Function**: login/role context, then the navigation path on its own line (see below),
  then any note about existing-vs-new screen.
- **Action**: the most detailed cell in the document. Real samples use inline **bold** sub-headers
  to break it up when the content has natural sections — e.g. "Current Process" (what happens
  today) then "New System Behavior" (what changes) then an "Example Scenario" — but a single
  unbroken run of numbered points is equally valid when the story doesn't need that split. Cover
  every field touched, every Mandatory/Optional/Conditional designation, every validation and
  business rule, every sub-condition by type/status, file-naming conventions with a real example,
  and integration rules with other modules. Do not summarize.
- **Result**: what got created/changed/posted, as one or more points.
- **Pre-Conditions**: what must already be true.
- **Trigger**: what starts this — a button click (name it) or a system/automated trigger chained
  off another story (name the story and point number it chains from, e.g. "chained immediately
  after Story 7.2.2.3").
- **Expected**: one bullet per distinct output/outcome, each stated as *label — what it is/means*
  (e.g. "Corrected Accrual Ledger / Interest Correction Transaction — per impacted interest
  type.", "Audit Information — before/after values, differential, reversal reference, all
  recorded."). This is **not** a single consolidated sentence, and it is not a strict two-column
  Output Item/Description table either — both real samples use short bulleted label–description
  lines. Use as many bullets as there are distinct outputs; don't compress them into one sentence
  or artificially split one output into several bullets.

**Navigation path formatting:** on its own line inside User & Function or Trigger, e.g.
`Fusion X → Home → Lending Module → Settings → Credit Appraisal Definitions → Post Approval Edit
Permission Setting`. Color `002060` (dark navy — confirmed from real runs; this is **not** the
same blue as headings, `2F5496`). Not bold. The `→` arrow character specifically renders in Arial
even though the surrounding words stay Candara (verified — Candara's arrow glyph is avoided).

The leading `1.`, `2.`, `3.`... before "User & Function" in the left column is a story-level
counter, independent of the section numbering, incrementing once per story.

---

### Section "7" (second instance) — Data Dictionary

```
Table 1 - Data Dictionary
```

8-column table:
```
| Feature | Field Name | Data Type | Source / Retrieve From | Constraint / Description | Sample Data | Data Validation | Max Length |
```
This replaced the older 3-column (Field Name | M/O/C | Description) format. Group rows by
Feature/screen so related fields are adjacent. Example rows from the sample:

```
| Due Date Template | Template ID     | Alphanumeric | System Generated | Unique identifier for Due Date Template | DDT-000123 | Mandatory, Read-only | 20  |
| Due Date Template | Effective Date  | Date         | User Input        | Date from which the template becomes effective | 01-06-2026 | Mandatory, Cannot be blank | N/A |
| Audit              | Created By      | User ID      | System Captured   | User who created the record | USER001 | Mandatory | 30 |
```

**Column-width warning:** in the raw sample this 8-column table was given almost-even column
widths (roughly 770–1310 DXA each, against a 9000+ DXA table width). At that width, cells like
"Source / Retrieve From" and "Sample Data" wrap into a single word per line, which is the single
worst-looking element in that document. Don't repeat this — see the column-width proportions in
SKILL.md's DOCX FORMATTING section and give "Constraint / Description" the lion's share of the
width (around 28% of total).

**Draft-stage variance (do not follow):** the Lending Module V0.1 draft used a simpler 4-column
table (`Field/Button Name | Data Type | Mandatory Status | Preference`), grouped under a
full-width divider row per story (e.g. "Story 01 – Post-Approval Edit Permission Setting"), with
no named table style applied. This is an outlier against the other three sources — the V1.0
Transaction Reversal sample and both blank org templates all independently agree on the 8-column
form above. Treat the 4-column version as an early-draft shortcut, not the target format; use the
8-column form grouped by Feature.

After the table, add (if applicable): `Field reference: [source document / Excel sheet link]`

---

### Section 8 — E2E Impact Identification Table

```
Table 2 - E2E Impact Identification
```

3-column table, **header row centered** (the only table in the document where the header is
centered rather than left-aligned — this is deliberate in the sample):
```
| Area | What to Capture (BA Guidance) | Impact Description |
```

Example rows, taken verbatim from the V1.0 sample (Transaction Reversal):
```
| Primary Module          | The main functional area where the change is implemented | Account Module – Transaction Reversal |
| Upstream Touchpoints    | Systems or channels that send data into this module | Account Module – Teller Management (originating transactions), Batch Transaction processing |
| Downstream Touchpoints  | Systems or modules that receive or are affected by the output | GL Posting (interest correction entries via existing mapping), Interest Application Engine, Overdraft Management, Reports & Enquiries |
| Reporting / MIS Impact  | Business reports or balances that may change due to this update | Applied Credit Interest Details, Accrued Overdraft Interest Detail... |
| Batch / Scheduler Impact | Any business-known batch, EOD, or scheduled process | EOD Interest Accrual, scheduled Interest Application run |
| Customer Impact         | Will customers notice a change? (Yes/No + brief note) | Yes – customer's interest balance/GL entry may change... |
| Operational Impact      | Will branch or ops teams change how they work? | Yes – Maker/Approver see an informational notice on Create/Confirm... |
| E2E Validation Required | Is end-to-end testing needed across the above areas? | Yes – across Transaction Reversal, Interest Accrual/Application, GL Posting... |
```

**Row set — 8 rows, verified identically (same 8 Area categories) in both the V1.0 sample and the
Lending V0.1 draft:** Primary Module, Upstream Touchpoints, Downstream Touchpoints, Reporting/MIS
Impact, Batch/Scheduler Impact, Customer Impact, Operational Impact, E2E Validation Required.
**Do not use** the previously-documented 14-row set (Repayment Schedule Engine, Loan
Accounting/GL, Arrears & DPD Calculation, EOD/Batch Processing, Data Integrity, Audit &
Compliance, Security & Authorization, Validation & Messaging, etc.) — that list does not appear
in either real sample and was never verified against one; it was invented as a plausible-sounding
banking-domain elaboration. Ground every row's Impact Description in the module reference file's
"E2E Impact Notes" section or the scope statement — stating "None identified" is correct when true
(the V1.0 sample does this for Batch/Scheduler Impact and Customer Impact on a screen-only
feature). Those module-file bullets (e.g. "Repayment Schedule Engine", "GL / Loan Accounting") are
domain facts to fold into the relevant one of the 8 rows above (usually Downstream Touchpoints or
Reporting/MIS Impact) — not row names in their own right.

---

### Section 9 — Diagrams and Examples

Real embedded screenshots, each under a centered italic caption (style `Caption`, not bold) continuing the List of Figures
numbering (e.g. `Figure 2 – Due Date Template Setting`, following Figure 1's flow chart). Use
`[Diagrams and examples to be attached]` only if genuinely unavailable, and tell the user so they
can supply screenshots later.

---

### Section 10 — Annexure

```
10.1  Common Guide for FusionX
https://lolcgroupdev.atlassian.net/browse/PF-XXXXX  [Jira reference]
```
A linked or embedded "Common Guide For Development" document icon may also appear here in the
sample; a text link to the Jira/Confluence guide is sufficient for a generated draft.

---

### Section 11 — Test Scenarios

Bullet list, each as `[scenario] → [expected outcome]`. Example from the sample:
- "Update with past effective date → only status editable"
- "Attempt to save due date = 31 → validation error"
- "February schedule with due date 31 → adjusted to 28/29"

May be left as `[Test scenarios to be defined]` at V0.1 draft stage if the user prefers to defer it.

---

## WRITING RULES (from the sample)

1. **"Shall"** for mandatory system behaviours: "System shall validate...", "The file must be
   generated..."
2. **"Must"** used frequently (interchangeable with "shall" in LOLC style)
3. Navigation paths: `Home → FusionX → [Module] → [Sub-module] → [Action]` — color `002060` (dark
   navy, not the heading blue), not bold, when inside story User & Function/Trigger text; the `→`
   glyph specifically renders in Arial
4. File naming conventions stated explicitly with example: `CRBSIYYYYMMDDVVV.BBB` →
   `EX: CRBSI20260611280.014`
5. Field specs inside story Action cells use real Word multilevel list numbering rendering as
   legal-style points (7.1.2.1., 7.1.2.2.) — never type the digits as literal text (see
   `docx-formatting.md`)
6. Mandatory/Optional/Conditional stated in words in the Data Dictionary, not letter codes
7. ISO standard references included for codes where applicable
8. Company name: "LOLC Technologies" on the cover/footer; "LOLC Technologies Pvt LTD" in the
   Document Information table
9. Footer format: live FILENAME field on the left (prefixed "User "), "Page " + live PAGE field +
   " | " + live NUMPAGES field on the right — never hardcode the filename or page numbers
10. Dates: DD/MM/YYYY everywhere in the document body and cover page; the one sanctioned
    exception is the Revision History table's Revision Date column, which uses YYYY-MM-DD
11. Risks section lists specific risks related to the feature — not generic boilerplate
12. Open Questions table always present even if empty
13. General Guide Line (1.6) and E2E Impact Identification Table (Section 8) are both required —
    they were missing from pre-2026 templates; do not omit them

---

## FORMATTING RULES (reverse-engineered from the signed-off sample's raw XML)

These are not style suggestions — they were measured directly from the document's
`word/document.xml` and `word/styles.xml`, and they explain why output that "looks mostly right"
can still look inconsistent page to page. Full detail and the reasoning behind each rule is in
SKILL.md's DOCX FORMATTING section; the headline facts:

- **Body font is Candara at 22 half-points (11pt).** Confirmed from `docDefaults` interacting
  with per-run overrides — but the document's *theme* default is actually Calibri. Every Candara
  appearance in the real file is an explicit per-run override, not inherited from the theme. If a
  generator relies on theme inheritance instead of explicit per-run `font` properties, some runs
  (especially auto-generated ones like ToC entries or stray paragraph marks) will silently render
  in Calibri at the wrong color — this is very likely the exact "some pages differ" symptom being
  reported, and it's systematic, not random.
- **Heading colors are `2F5496`** (from the `Heading1`/`Heading2` style definitions) for in-body
  section headings; the **cover-page title** uses a different, brighter blue, `0070C0`. These are
  two distinct shades used in two distinct places — don't collapse them into one blue or swap
  them.
- **Table header shading uses two real mechanisms, not one.** Verified across all four real
  files: `GridTable4-Accent3` (Revision History, Open Questions, Data Dictionary, E2E Impact in
  the V1.0 sample) gives a dark grey `A5A5A5` fill with bold white text via the named style —
  apply it by style reference, no manual shading needed. Separately, `D5DCE4` (light blue) is a
  real, deliberate **manual** per-cell shading confirmed on the cover-table label column,
  Document Information label column (in both the V1.0 and V0.1 samples — the most universal case),
  General Guide Line's header row, and the Epic table's merged title row — these tables use base
  style `PlainTable1`/`TableGrid`, which has no built-in fill, so the shading is applied by hand on
  specifically those cells. Don't apply `D5DCE4` as a full table style, and don't apply it to
  value/body cells. Full detail and the exact table-by-table mapping is in `docx-formatting.md`'s
  Table styles section — an earlier pass on this skill incorrectly concluded `D5DCE4` was
  fabricated and should never be used; it is real, just not a `tblStyle`.
- **Column widths matter as much as color.** The sample's 8-column Data Dictionary table and
  several other wide tables were given nearly-even, too-narrow column widths (roughly 770–1310
  DXA per column against a content width of ~9000+ DXA), causing every multi-word header and
  most cell content to wrap into a vertical single-word ladder. This is the single most visually
  damaging defect in the sample and the most avoidable — give description-heavy columns
  (Constraint/Description, Impact Description, Question) the bulk of the width and keep
  short-value columns (Max Length, #, Status) narrow. See SKILL.md for exact proportions per table.
- **Address:** 137, Rajagiriya Road, Rajagiriya. 10100 is current. Don't use the older
  852 Kotte Rd address from earlier URS samples.

## COMPLETE SECTION ORDER (12 numbered sections, plus the duplicate "7." — current format)

```
Cover Page
Table of Contents
List of Figures
List of Tables
Section 1:  Document Control
  1.1  Document Information
  1.2  Revision History
  1.3  Definitions and Acronyms
  1.4  Assumptions
  1.5  Risks
  1.6  General Guide Line
Section 2:  Open Questions
Section 3:  Overview/Project Description
Section 4:  Flow Chart
Section 5:  Scope
  5.1  What is in scope
  5.2  What is out of scope
Section 6:  Epic: Narrative and Statement
Section 7:  Features/Stories
  7.1  Story 01
  7.2  Story 02 (if applicable)
Section 7:  Data Dictionary          ← numbering repeats "7." in the real samples; keep as-is
Section 8:  E2E Impact Identification Table
Section 9:  Diagrams and Examples
Section 10: Annexure
Section 11: Test Scenarios
```
