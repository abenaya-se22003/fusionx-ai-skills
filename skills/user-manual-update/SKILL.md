---
name: user-manual-update
description: Use when a Jira ticket or user request asks to create or update a FusionX module user manual (Accounts, Cash, Collateral, Lending, SCO, Term Deposit, or a new module) by walking the live UAT application and producing a screenshot-led Word/PDF user guide.
---

# User Manual Update

## Overview

Orchestrates the full pipeline for turning a Jira ticket into a delivered
module user manual: scope → live UAT walkthrough → **Gate A** (coverage
validation) → docx build → export/QC → **Gate B** (content/formatting
validation) → delivery. This skill is self-contained — it does not depend on
any file outside this folder. Everything needed (coverage standard, manual
production rules, build/QC scripts, environment gotchas) lives here so it
works in any project it's dropped into, not just the one it was authored in.

## Read First, In Order

1. "Coverage Standard — UAT Walkthrough" below — how deep the UAT walkthrough
   must go. Default is full depth immediately, never a breadth-only/title-only
   pass.
2. "Manual Production Rules" below — what the manual document itself must
   contain: structure, hard content rules, numbering safety, screenshot rules,
   pre-delivery validation checklist.
3. `gotchas.md` (this skill folder) — operational/environment lessons learned
   across prior module updates that aren't written into the sections above.

Do not skip ahead to writing UAT steps or manual content without reading the
governing section for that phase first — each was written because skipping it
caused real, repeat-costing rework.

## Coverage Standard — UAT Walkthrough

Governs step 2 (Walk UAT) and what Gate A checks. **Default to full depth
immediately** — never a breadth-only/title-only pass that only checks entry
points, tile titles, or default/landing states. Never conclude a screen has
"no target content" from its name or menu label. Open it.

**Session and access:** drive the browser with `playwright-cli -s=<name>`
under this engagement's own named session, established per Workflow step 2
above (see `gotchas.md` for how to reuse/recover it and work around
click/rendering quirks). Keep the browser visible for login/MFA; wait for the
user to confirm login before touching authenticated screens. Don't enter
excluded systems/modules until explicitly authorized. Don't expose
credentials, tokens, or personal data in notes or screenshots.

**Cover every in-scope item:** dashboard/landing entry points; every
sidebar/top-nav process, parent menu, and nested menu item; every screen,
tab, accordion, card, modal, drawer, wizard step, sub-screen; every button,
icon button, link, row action, clickable field; search/filter/sort/pagination/
expand-collapse/reset/clear/cancel/back/close controls; add/create/save/
submit/resubmit/view/edit/update/delete/approve/reject/assign actions where
authorized; nested records (identifications, contacts, addresses, bank
accounts, tax IDs, relationships, key persons, POAs); empty/populated/
no-result/validation-error/success/pending/active/update/confirmation states;
every approval category the app exposes, not just the default queue. Test
both newly created records (validates the full creation lifecycle) and
existing populated UAT records (validates inquiry, historical display,
maintenance, nested-entry, downstream workflow) — if either type is
unavailable, document the gap and reason rather than treating one as
equivalent to the other.

**Dropdowns and selectable controls** (dropdown, radio group, segmented
control, switch, checkbox group, card selector, autocomplete, date/time
picker):
1. Open it. Record every static value exactly as displayed (capitalization,
   spelling).
2. Select every value at least once when it can change fields, validation,
   navigation, or workflow behavior — one representative value is only
   enough when the branch does **not** change the visible UI.
3. Follow and test every branch a selection creates; inspect fields/
   sub-screens that appear, disappear, become mandatory, or become enabled.
4. Distinguish static values from dynamic/master-data results. For dependent
   lookups (Bank→Branch→Product, Country→Province→District), document the
   dependency and test representative parent values — don't describe a
   temporary subset of a live lookup as a permanent complete list.
5. Capture an expanded-control screenshot when the values matter to the
   manual.

**Search and filtering** — for every search-criterion selector: record all
criteria; execute a valid matching value where test data exists; test a
valid value with no match; test blank input and record the validation
response; test clear/reset; verify result selection, Active/Pending tabs,
pagination, and the details shown after selecting a result.

**Transaction testing** — exercise creation and submission to completion
where the UI/authorization permit; exercise updates and resubmission where
permitted; exercise nested add/view/update/delete where present; exercise
every approval type on both approve and reject paths with suitable test
items, entering meaningful remarks where required; verify the resulting
status, queue, audit info, or confirmation message. Never click a
destructive control merely to inspect it — use a disposable UAT record or
stop at the confirmation dialog when mutation isn't authorized. Never perform
an irreversible/production-impacting action without clear authorization.

**Evidence capture** — screenshot every major screen/process entry point;
important initial/populated/review/confirmation/resulting states; expanded
dropdowns and branch-changing selectors; add/view/edit/delete/submit/approve/
reject/assignment-removal interfaces; nested-entry dialogs and completed
nested-entry tables; search criteria, representative results, filters,
relevant tabs. Capture continuously as you go — transient dropdown/dialog/
validation/confirmation states may not be reproducible later. Use descriptive
sequential filenames; exclude secrets/PII; keep bug-only screenshots separate
from the manual's evidence set.

**Defects and blockers** — record unexpected behavior with screen, steps,
expected vs. actual result, and evidence, kept in a separate log from the
manual. Before recording something as blocked, retry with more than one
input combination (different records, filter values, or a fresh session) so
the log reflects a reproducible defect, not a one-off fluke — note how many
attempts were made. Before recording an unexplained gap (e.g. a screen that
never returns data), inspect the underlying network request/response, not
just the rendered UI, so the log captures a root cause where possible. When a
blocker is found, tell the user and ask whether to keep investigating or stop
and document it as-is — don't silently decide either way. Continue with
unaffected branches instead of stopping the whole walkthrough.

## Workflow

0. **Check standing coverage.** Read `FLOWS-LOG.md` (repo root) for this
   module's current coverage status before starting — don't re-derive from
   scratch what a prior session already verified. **If `FLOWS-LOG.md` (or
   `AUDIT-LOG.md`) doesn't exist yet**, create both now from the templates in
   "Repo-Wide Audit Trail" below, and explicitly note in your first entry
   that this project has prior module-update history predating these two
   files (see each module's own `Session History - <date>.md` /
   `UAT Coverage and Defect Log.md` for that history) — do NOT backfill past
   sessions into these files from memory or by re-reading old module folders;
   they start tracking from the session that created them forward. Whoever
   runs this skill first is the one who creates them — there is no separate
   setup step.
1. **Scope.** The ticket's Done/not-done table is authoritative — only
   not-done rows are in scope; never touch/"improve" Done content as a side
   effect. Also compare the ticket against the live app's actual current
   screens, not just the ticket text — "Done" in the ticket has previously
   turned out to be stale, templated, or missing fields live. The existing
   `.docx` (never a PDF attached to the ticket) is the source of truth for
   structure. If more than one `.docx` in the module folder looks like a
   candidate (backup copies, a `~$`-prefixed Word lock file, a `(delivery)`
   suffix, mismatched version numbers in filenames), do not assume the
   newest-timestamped one is correct — confirm the authoritative file with
   the user before building on it.
2. **Walk UAT.** Before opening a browser, establish this engagement's own
   named `playwright-cli` session per `references/browser-session.md`
   Section 0: check `AUDIT-LOG.md` (repo root) for a previously recorded
   `Browser session: fx-um-<module-slug>-<tag>` line for this module's
   update; reuse it (after confirming via `playwright-cli list` that it's
   still open) if found. If not, mint one now (`<module-slug>` a short label
   for the module, e.g. `term-deposit`; `<tag>` a random/timestamp suffix)
   and record the line in `AUDIT-LOG.md` immediately, before opening the
   session — this is what keeps a concurrent update to a *different* module
   (or the same module from a separate conversation) from ever landing on
   this one's browser. Drive the browser with `playwright-cli -s=<name>`
   only — never a bare `playwright-cli` call, and never a
   project-specific test framework/agent that might also exist in the repo.
   Follow the full "Coverage Standard — UAT Walkthrough" below.
   Capture screenshots continuously, not at the end. Keep defect/blocker
   evidence in a separate log from the start.
3. **GATE A — Pre-Draft Coverage Validation.** Mandatory checkpoint, run
   before writing a single word of manual content. See "Gate A" below. Do not
   proceed to step 4 until every in-scope item is resolved to
   confirmed-complete / blocked / not-applicable — no blanks, no "probably
   covered."
4. **Inspect conventions.** Before writing content, open the existing docx and
   read the real OOXML of the section you're extending: heading style names,
   numbering setup, caption convention, field-bullet pattern. Never assume —
   every module documented so far has differed in at least one of these.
5. **Build.** Copy this skill's `scripts/build_manual_template.py` into
   `<Module>-Manual-Update/`, fill in CONFIG, write content with its helper
   functions. Follow its docstring's required operation order exactly. See
   "Manual Production Rules" below for structure/content requirements.
6. **GATE B — Post-Build Content & Formatting Validation.** Mandatory
   checkpoint, run after export, before delivery. See "Gate B" below. Do not
   proceed to step 7 until both the mechanical (`qc_audit.py`) and
   hand-verify layers pass clean.
7. **Deliver**, all inside `<Module>-Manual-Update/` (never loose in repo
   root): the versioned `.docx`/`.pdf`, `UAT Coverage and Defect Log.md`,
   `Outstanding Items and Blockers.md`, `Session History - <date>.md`,
   `screenshots/` (with a `defect-evidence/` subfolder kept out of the manual).
8. **Update the repo-wide audit trail.** Append an entry to `AUDIT-LOG.md`
   (repo root) summarizing this session, and update `FLOWS-LOG.md` (repo
   root) with the coverage status of every screen/flow touched. See "Repo-Wide
   Audit Trail" below — do this every session, not only when asked.

## Gate A — Pre-Draft Coverage Validation

Runs after UAT walkthrough (step 2), before any manual content is written
(step 4/5). Purpose: catch missing/incomplete data collection while you can
still go back to the live app cheaply — going back to UAT after the manual is
half-written is far more expensive than checking now.

**Do not self-grade this gate.** Dispatch a fresh subagent (`Agent` tool,
`subagent_type: general-purpose`, `run_in_background: false` — you need its
verdict before step 4, so it must block) to independently build and verify
the coverage table. A subagent sharing your own session's assumptions can't
catch what you missed; a fresh one starting cold has no stake in the
walkthrough already being "done" and no reason to rubber-stamp your prose.

Brief the subagent as a self-contained task (it has no memory of this
conversation) with: the ticket's Done/not-done table and which rows are in
scope, every screen/control you walked plus the screenshots folder path, and
the exact `playwright-cli -s=<name>` session name this engagement is using
(from `AUDIT-LOG.md`'s `Browser session:` line) — state the literal name, do
not tell it to discover one itself. `playwright-cli list` shows every session
on the machine, not just this engagement's; a subagent told to "find" an
authenticated session has no way to tell this engagement's session apart from
a different, possibly concurrently-running update's. Its job is to build its
OWN table by actually re-driving a meaningful sample of the flagged items
live and cross-checking every screenshot file exists and shows what it's
claimed to show — not to grade a table you hand it as already-true.

Example dispatch prompt (adapt names/paths):
```
Independently verify UAT coverage for the Batch Reversal screen (Term
Deposit module, ticket PF-99999). Screens/controls to check: [list]. Use the
playwright-cli session named fx-um-term-deposit-7k2q for every browser
command (playwright-cli -s=fx-um-term-deposit-7k2q <command>) — it is
already logged into UAT; do not open a new session, do not use a different
session name even if `playwright-cli list` shows one that looks
authenticated. Screenshots claimed so far are in
<Term-Deposit-Module-Manual-Update/screenshots>. Re-open the screen live,
re-test every dropdown option and every row action listed, and cross-check
each cited screenshot against what it's supposed to show. Do not assume a
row is fine because someone already labeled it Confirmed — verify each one
yourself. Report every gap, unverifiable claim, or evidence-free row via
ReportFindings, most severe first, CONFIRMED vs PLAUSIBLE.
```

Any CONFIRMED finding blocks progression to step 4: close the gap for real,
then dispatch a **new** fresh subagent (not the same one — it now has a
stake in its own prior pass) to re-verify. Loop until a dispatch comes back
clean.

The subagent (and you, briefing it) checks, for each in-scope screen:
- Every dropdown/radio/selector opened; every static option recorded exactly
  as displayed; every option that changes visible fields/dialogs actually
  selected and its branch followed (one representative value is only enough
  when the branch does NOT change the UI).
- Every row-level action (View/Update/Delete/Approve/Reject/etc.) inventoried
  from the live grid (query the DOM directly, e.g.
  `document.querySelectorAll('.ant-table-tbody tr td:last-child')` or the
  app's real equivalent — never the accessibility-tree snapshot alone for a
  virtualized list) and walked through to a confirmed result, not just
  reached and cancelled.
- Search/filter screens: a matching value, a no-match value, blank input, and
  clear/reset all exercised.
- Every transient state you intend to describe or screenshot (loading,
  validation, confirmation) actually captured, not assumed reproducible
  later.
- Defect/blocker evidence already logged separately (not left to reconstruct
  from memory when the manual is drafted).

If any row is Blocked or a branch genuinely couldn't be tested, that's fine —
name it, don't silently drop it or silently narrow scope. If the gap is large
enough that it changes what's practical to deliver this round, surface it to
the user and get explicit sign-off before proceeding — never narrow silently
and present the result as the full sweep.

## Gate B — Post-Build Content & Formatting Validation

Runs after `scripts/to_pdf_export.py` (which re-saves the docx with a
refreshed TOC/fields), before Deliver (step 7). Two layers, both required —
the mechanical layer catches structural bugs invisible to a visual read; the
hand-verify layer catches everything the script can't judge.

**Do not self-grade this gate either.** Dispatch a fresh subagent
(`Agent` tool, `subagent_type: general-purpose`, `run_in_background: false`)
to run both layers itself against the actual delivered files — not to trust
a summary of what you already did. Give it the docx and PDF paths, the
screenshots folder, and the exact `qc_audit.py` invocation (module,
`--start-heading`/`--end-heading`, `--numid`, `--baked-in-numbering` if
applicable). It must run the script itself and independently read the
document for the hand-verify checklist below — not accept your account of
either. Have it report via `ReportFindings`, most severe first,
CONFIRMED vs PLAUSIBLE. Any CONFIRMED finding blocks Deliver: fix it, then
dispatch a **new** fresh subagent (not the one that just passed it) to
re-run both layers from scratch. Loop until a dispatch comes back clean.

Example dispatch prompt (adapt paths/flags):
```
Run the Gate B pre-delivery QC pass for the Term Deposit manual build at
<path to docx>.  Run: python qc_audit.py --docx "<path>" --screenshots
"<path>" --start-heading "Batch Reversal" --numid <N>. Then, independently
of that script's output, read the actual document yourself and check the
full hand-verify list in SKILL.md's Gate B section (defect-log grep,
Bookmark-error grep, caption presence, nested-picker screenshots, dropdown
bullet formatting, grid-column accuracy, paragraph geometry, version state,
final PDF sanity). Do not accept "already checked" from me — verify every
item against the file yourself. Report findings via ReportFindings, most
severe first, CONFIRMED vs PLAUSIBLE.
```

**Mechanical — `scripts/qc_audit.py`** against the freshly re-saved docx
(not the one the build script produced a moment earlier — Word's own save
step can silently strip numbering that both python-docx and a same-session
PDF tolerate). Its checks include, in order: the file actually opens in real
Word via COM (run first, no exceptions — a `numId` of literal `"None"` passes
every other check and still makes Word refuse to open the file);
byte-identical duplicate screenshots; a full numbering simulation confirming
every child heading's number prefix matches its real parent, not just a
gapless top-level sequence; stale hardcoded chapter numbers baked into
heading text. Fix and re-run steps 5–6 until clean.

**Hand-verify** (the audit script cannot judge these — see "Pre-Delivery
Validation" in "Manual Production Rules" below for the full
rationale behind each):
- Grep the entire document, case-insensitive, for `"defect log"` — zero hits,
  full stop (see Hard Rules).
- Grep for `Error! Bookmark not defined` and similar Word field-error text —
  zero hits.
- Every screenshot referenced actually exists and has a non-empty caption,
  unless the document's confirmed real convention is uncaptioned.
- No two screenshots appear back-to-back with no explanatory text between
  them.
- Every field/bullet naming a nested picker, pop-up, or sub-screen has a
  matching screenshot of that nested view specifically, not just the parent.
- Every audited dropdown/option list from Gate A is presented as bullets (not
  prose), spelled/capitalized exactly as the UI shows it.
- Every "the grid displays X, Y, Z" column description matches a real
  screenshot of that exact screen — not a description copied across a batch
  of similar screens.
- Paragraph geometry (indentation, alignment, spacing) of new content matches
  a confirmed reference section in the same manual, not just its style name.
- Version number and Version Control table reflect whatever was decided under
  the version-bump Hard Rule (asked, and actioned per the answer) — not left
  stale, not bumped without having asked.
- Final PDF opens, has a plausible file size, and was rendered from the
  manual itself (not a stray browser tab left open during export).

Every hand-verify item must be individually checked against the actual
document (grep output, a real page read) before being ticked — "this is
probably fine, I didn't change that area" is not a check. Only once both
layers are clean does step 7 (Deliver) happen.

## Manual Production Rules

Governs step 4/5 (Inspect conventions, Build) and what Gate B's hand-verify
checklist draws from. Applies whenever the task originates from a tracking
ticket: treat its Done/not-done checklist as authoritative scope, treat the
existing manual file itself (not a PDF attached to the ticket) as the source
of truth for structure, and never modify/reformat/"clean up" out-of-scope
content even if inconsistent.

**Required front matter:** cover page; system/module/environment/observed
app version; document title and unique reference; status and classification;
owner and prepared-by; issue date; version control table; review/approval
table; distribution/maintenance statement; document conventions; roles and
responsibilities; access requirements/prerequisites; process overview; table
of contents. Every material revision increments the version and adds a
version-history entry (see the version-bump Hard Rule below — that Hard Rule
overrides this for *when* a revision counts as material).

**Organization** — by application navigation and business process: accessing
the module; main/landing screen; sidebar and nested processes; search/
inquiry; create/add; view; update/edit; delete/remove; submission/
resubmission; approval/rejection; reports/admin functions; field/option
reference; pre-action checklist. Create distinct subsections (Add, View,
Update, Delete, Submit, Approve, Reject) whenever those functions exist —
don't merge materially different operations into one vague screen
description.

**Procedure writing:** numbered lists for sequential actions, bullets for
choices/controls/non-sequential info. Use exact UI field/button/tab/screen
labels. Explain required fields, dependencies, validations, confirmations,
resulting states, and what to verify before a state-changing action. State
role/permission limitations affecting available controls. Never describe
untested behavior as confirmed.
- *Field/input presentation:* use the manual's established convention (e.g.
  an asterisk alone marks required — don't add a redundant `Required.`
  paragraph). Don't add generic helper text under self-explanatory field
  names (`Enter the name`, `Select Manual or Auto`). Keep a field
  explanation only when it conveys something not inferable from the label/
  screenshot (validation rule, dependency, conditional field, dynamic
  lookup, role restriction, required format). Removing helper-text bulk
  doesn't remove the obligation to expose all verified dropdown options
  separately. Keep Save/Create behavior, confirmations, resulting states,
  and subsequent procedures as standalone procedure text even when adjacent
  to a field list.
- *Inline procedure lead-ins:* a short line introducing a procedure but not
  part of the heading hierarchy (`View and update`, `Map products`) must be
  visibly distinct (bold, bold-underline, or the manual's existing dedicated
  style) — never indistinguishable from body text — and kept with the
  content it introduces so it can't be stranded at a page break.

**Dropdown and option formatting** — introduce the field by name; list every
static option as separate bullets/numbered items, never embedded in a prose
sentence; preserve UI capitalization/spelling exactly; explain the branch an
option causes when relevant; use a table mapping fields→option lists when a
screen has several selectors, with multi-option cells as bullet lists, not
semicolons; label dynamic/dependent lookups as such rather than presenting a
temporary result subset as a permanent list. Example:

The available search criteria are:
- **Customer Name**
- **Customer Identification**
- **Customer Reference Code**

**Matching existing document conventions** (when extending, not starting
fresh):
1. Never invent a new heading style/numbering/bullet pattern — inspect the
   actual OOXML of the immediately preceding section first. Different
   chapters in the same manual can use different conventions; match the
   chapter you're extending, not the document's most common one.
2. Match the confirmed pattern exactly: heading style, field-then-description
   layout, whether manual step numbers are used.
3. When a new sub-section reuses a numbered heading style but starts a fresh
   sequence (not a continuation), give it an explicit start override to
   begin at 1.
4. If in doubt, ask the user rather than guess — style mismatches are highly
   visible and hard to catch without an XML diff.
5. Match paragraph geometry, not just fonts/styles: left/right/hanging
   indentation, alignment, before/after spacing, cloned from a confirmed
   comparable paragraph. Never copy only the left indent and clear the
   right. Don't hardcode indentation values from another module — every
   manual can use different styles.
6. Don't apply body-text indentation to screenshot paragraphs — clone the
   manual's own figure paragraph properties.
7. Before cloning a heading's `pPr` to fix/match another heading, confirm
   whether the source uses a live Word multilevel-list number (`numPr`
   drives auto-numbering) or has that explicitly disabled with the chapter
   number typed as literal text (`numId=0`/empty override) — a document can
   mix both even across visually identical headings. Check whether the
   visible number already appears as literal characters in the source
   paragraph's own runs before picking what to clone from. When the new
   content is really a tab label or sub-topic, consider a bold inline
   lead-in instead of a heading level to sidestep this risk entirely.

**Heading numbering (multilevel lists)** — treat any numbering change with
code-change rigor; defects here are invisible in source XML and only visible
as wrong text on a rendered page:
1. Don't assume two `numId`s count independently just because they normally
   do — legacy multilevel-list definitions can leak counter state across
   `numId`s sharing an `abstractNumId`. For an isolated list, clone the
   source `abstractNum`'s level defs into a brand-new `abstractNumId` with
   fresh, unique `<w:nsid>`/`<w:tmpl>` values.
2. `numbering.xml` has a strict element order: every `<w:abstractNum>`
   before every `<w:num>`, with `<w:numIdMacAtCleanup>` (if present) last.
   Never blindly `.append()` — insert a new abstract right after the last
   existing one; insert a new num right before `numIdMacAtCleanup` (updating
   its `val`). Violating this is tolerated by python-docx and a same-session
   PDF, but Word's own `Save()` will silently detect the bad order, treat
   the whole numbering part as corrupt, and regenerate it from near-empty
   defaults — discarding every custom numbering instance with no warning.
3. A paragraph's `w:numPr` inside `w:pPr` has a required position:
   immediately after `w:pStyle`, before `w:ind`/`w:rPr`. Appending it at the
   end is the same class of bug — silently stripped on a real Word
   round-trip.
4. Verify with a real Word round-trip, not just a same-session PDF: (a)
   confirm numbering elements/`numPr` via python-docx before Word touches
   the file; (b) run the PDF export; (c) re-open the freshly-saved `.docx`
   via python-docx and re-check the same elements. Only (c) catches Word's
   silent post-save corruption.
5. Don't trust a gapless top-level sequence as proof of correctness —
   simulate the numbering counters directly against the saved `.docx`
   (walk headings in order, track per-level counters, reset the sub-counter
   on every new parent) and assert every child's number matches its real
   parent, across the whole affected scope.
6. Check for pre-existing blank heading paragraphs (a Heading style with no
   title text) in the affected scope — these silently consume a number and
   render as a blank numbered TOC row once the TOC refreshes. Confirm
   they're pre-existing (usually are) and ask the user how to handle them
   (typically demote to body text) before touching them.
7. Check for headings with an old chapter number typed directly into the
   title text (e.g. "4.5.2 Fund Transfer List") — confirm with the user
   before stripping it, then automate the strip with a script rather than
   hand-editing.
8. If overriding a heading level's start value produces an apparent
   off-by-one, don't chase it with a compensating hack — that's far more
   likely the corruption in point 2 than a real property of the override.
   Fix the corruption first, then re-test.
9. The abstract numbering level's own `w:rPr`/`w:rFonts` controls the
   auto-number glyph's font, independent of the heading text's own font.
   Explicitly set `w:ascii`/`w:hAnsi` on every level in use to match the
   document's heading font.
10. **A `numId` of `None` or any non-numeric value is a hard,
    unrecoverable failure invisible to every check above** — well-formed
    XML that opens fine in python-docx, survives a same-session PDF, and
    passes points 1–9, but Word will flatly refuse to open the file at all.
    Guard at the source: any function setting `w:numPr` should validate
    `numId`/`ilvl` are non-negative integers and raise immediately if not.
    Verifying the file opens in real Word via COM is the only after-the-fact
    check that catches this — run it first, before anything else.

**Screenshot placement** — place every screenshot immediately after the step
it supports; caption with a line explaining what to notice, unless the
manual's confirmed existing convention is bare/uncaptioned (default to
captioning when ambiguous or new); never place screenshots back-to-back with
no explanatory text; include initial/populated/review/confirmation/resulting
states, expanded dropdowns where values matter, and representative Add/
View/Update/Delete/Submit/Approve/Reject/nested-entry screens; avoid
repeating the same screenshot across sections (cross-reference instead);
keep defect-only screenshots out of the manual. When inserting
programmatically, always pass an explicit `width` (derived from an existing
embedded screenshot's `wp:extent`, not a guessed inch value) — omitting it
uses native pixel size at 96 DPI and overflows the page margin with no error.
When a field's description says it opens a secondary pop-up/picker, capture
that pop-up itself, not just the parent screen. Before delivery, audit every
field/bullet naming a sub-screen or nested pop-up and confirm each has a
matching screenshot.

**Content separation / zero defect language (Hard Rule, expanded):** the
manual's own prose must never contain defect/blocker language, in any
phrasing — this shipped wrong twice before being made an absolute rule.
Banned: "At the time of this documentation update...", "logged as a defect",
"did not complete successfully", "could not be saved/captured", "blocked",
or any pointer to the defect/coverage log. When a screen/action is genuinely
blocked with no populated-result evidence, describe the *intended* behavior
only, exactly as if it works — everything about the blocker lives solely in
the coverage/defect log. **Exception:** a real, verified functional
requirement that isn't obvious from the field's label (e.g. a field that
silently requires a numeral, a default value that fails validation) is
stated as a plain neutral fact with zero bug-framing — the test is "would
omitting this cause a reader to hit an unexplained failure?" If yes, keep
the bare fact. If the gap is purely cosmetic (a screen shows raw IDs instead
of names but the reader can still complete the task), drop the sentence
entirely. If unsure which case applies, ask. Keep the manual's prose generic
— no hardcoded reference IDs/customer names/test-data values in written
procedure text, even if visible in a screenshot (screenshots with real UAT
data are fine).

**Accuracy rules:** base the manual on observed/tested behavior only;
clearly identify configuration-driven or role-dependent values; never claim
a list is complete unless every visible static option was audited; never
claim transaction coverage unless the action was completed and the result
verified; keep excluded systems out until authorized; use consistent
terminology throughout.

**PDF and layout:** professional A4 layout, readable margins/headings/
tables/lists/captions; avoid awkward page-splits of headings/figures/small
tables; scale screenshots without distortion; keep option lists as lists,
not dense paragraphs; generate both editable source and PDF.

**Pre-delivery validation** — beyond Gate B's hand-verify list above, also
check: no adjacent duplicate paragraphs/repeated procedure sentences
anywhere in the changed range (not just duplicate screenshots); every
short, title-like body paragraph in the changed range is either intentional
prose or a correctly formatted inline lead-in; the rendered left/right text
boundaries of every changed content type match a confirmed reference section
(checking only a style name or only the left indent is insufficient); after
any bulk field-description cleanup, every remaining/removed field-to-prose
transition still has its workflow instructions, option coverage,
validations, and outcomes intact; grep the build script itself for a
screenshot filename passed twice into one screen's content block (e.g. as
both "before" and "after" args to a shared helper) before ever exporting a
PDF.

**Completion criteria:** the manual is complete only when an operational
user can follow each process without unexplained UI knowledge, every
important choice is listed, every major action has supporting evidence, and
the final PDF passes the full validation checklist (this section + Gate B).

## Repo-Wide Audit Trail — AUDIT-LOG.md and FLOWS-LOG.md

Maintain two files at the repo root, in addition to (not instead of) each
module's own Session History/Coverage Log/Outstanding Items files. The
per-module files are per-ticket detail; these two are the standing,
project-wide record spanning every module and every session, so anyone
picking up this project — not just whoever ran the last session — can answer
"has X actually been verified" without reading every module folder's history.
Create them at the repo root the first time this skill is used if they don't
already exist.

**`AUDIT-LOG.md`** — chronological, append-only narrative of every
verification session: what was checked, what was found, what was corrected,
and why. Each entry states the current, correct picture as plain fact —
never "Correction: X" or "this pass we found" framing (that framing belongs
here, in the log; never in the manual or any other deliverable). Write an
entry whenever:
- A gap is closed (state what was checked and the result, with concrete
  evidence — record IDs, screenshot names, exact field values — not just
  "confirmed").
- A prior finding turns out to be wrong (state the correction plainly and
  why the original was wrong, so the mistake doesn't recur).
- The user pushes back on completeness ("check again," "you sure?") — this
  is a signal a prior pass was breadth-only; close the gap for real, don't
  just re-assert it's done.
- A defect is found that's out of scope for the current task (log it, name
  it as out of scope, don't silently drop or silently fix it).

**`FLOWS-LOG.md`** — a master index of every distinct navigation flow/area
covered across every module, each pointing to its own evidence
(screenshots, sub-reports, or the relevant module folder). Track coverage
status at the top (complete / gaps named explicitly). Update pass-by-pass,
organized by *area of the system* (module → screen) rather than by session,
so someone can look up "has screen X been checked" without reading the whole
chronological history.

**Ground rules:**
- Default to full-depth verification on first pass, not breadth-first. If
  time genuinely forces a narrower pass, say so explicitly before starting
  and get sign-off on the narrower scope — never narrow silently and report
  it as complete.
- A completion report that only lists what was checked, without confirming
  what full depth required and that the bar was met, is not acceptable.
- These are working documents, not deliverables — keep process narration out
  of anything that ships (the manual, tickets, reports). The "why we
  corrected X" story lives in `AUDIT-LOG.md`; the manual states only the
  current correct fact — this is the same principle as the manual's own
  "zero defect language" hard rule above, applied one level up.

## Hard Rules

These have each shipped wrong at least once before being made explicit —
treat every one as non-negotiable, not a style preference.

- **Zero defect/blocker language in the manual's own prose, ever.** The
  manual describes the intended workflow as if it works. Defects live only in
  the coverage/defect log. Before delivery, grep the *entire* document
  (case-insensitive) for the substring `"defect log"` — this is the one
  invariant string across every real instance found so far; a hand-built
  keyword list has already missed real instances phrased differently.
- **Version number is never bumped by default — this includes cover text,
  running header/footer, and the Version Control table.** Build/fix content
  under the current version freely. Before delivery, if the round added
  material content, explicitly ASK the user whether to bump the version —
  don't silently skip the question and don't silently bump. **Material** =
  a new/changed section, screen, procedure, field list, or option set a
  reader would actually see — i.e. anything the Scope/Walk UAT/Inspect
  Conventions/Build steps of this skill's Workflow produced. **Not
  material** on its own = a defect-log-only entry, a
  screenshot swap/quality fix with no text change, a QC-driven formatting
  repair, or an `AUDIT-LOG.md`/`FLOWS-LOG.md`/tracking-doc update. If a round
  mixes both, materiality is decided by the manual-content changes, not the
  tracking-doc changes alongside them. Still unsure whether a specific change
  crosses the line — ask rather than decide either way. State it as a
  question with a recommendation, e.g. "This round added a new section —
  bump to vX.Y, or keep at current version?" The user decides; you surface
  the decision. This applies even if the current version already shipped.
  If the user says yes, check first whether a Version Control row for that
  target version already exists (one row per version, not one row per
  editing session) — merge into it instead of adding a duplicate. **This
  overrides the general "every material revision must increment the
  version" language in "Manual Production Rules" below** — that
  line states the eventual goal (a shipped manual shouldn't be permanently
  mislabeled), not a standing license for the agent to decide when/whether
  a revision counts as material. The decision is always the user's.
- **Full-depth coverage from the first pass**, not breadth-first. Never
  conclude a screen has "no target content" from its name or tile title —
  open it. A row-action inventory (e.g. confirming "Create" was tested) is
  not completion — every action found must be carried through to a confirmed
  result (success message + verified state change), not just reached and
  cancelled.
- **A completion re-verification request is scoped to the whole ticket**, not
  just the examples the user happened to name — named gaps illustrate a
  problem class, they are not the full list to fix.
- **Verify the file actually opens in real Microsoft Word (COM)**, not just
  python-docx, before calling anything delivered — a numId that's the literal
  string `"None"` (or any non-numeric numId/ilvl) is well-formed XML,
  survives every other check, and Word still refuses to open it.

## Quick Reference — scripts/

All three live in this skill folder's `scripts/` subdirectory.

| Script | Purpose |
|---|---|
| `build_manual_template.py` | Numbering-safe docx build helpers (headings, fields, images, OOXML numbering). Copy into the module folder — don't run as-is. |
| `to_pdf_export.py` | Word-COM PDF export with forced TOC/field refresh; re-saves the docx with that refresh applied — always QC the file this writes, not the build script's raw output. |
| `qc_audit.py` | Standalone pre-delivery QC: Word-open check first, duplicate-screenshot byte-hash, numbering simulation, stale-embedded-number check, `--baked-in-numbering` for documents with no live numbering (e.g. SCO). Run `--help` for flags. |

## Common Mistakes

See `gotchas.md` for the full list of environment/session traps (backend
outages, Word process locks, browser visibility, stale sessions) and subtle
content bugs (screenshot state-swaps, test-data pollution, cover-page vs
header version drift) collected across every module update so far.
