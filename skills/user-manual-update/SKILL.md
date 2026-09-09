---
name: user-manual-update
description: Use when a Jira ticket or user request asks to create or update a FusionX module user manual (Accounts, Cash, Collateral, Lending, SCO, Term Deposit, or a new module) by walking the live UAT application and producing a screenshot-led Word/PDF user guide.
---

# User Manual Update

## Overview

Orchestrates the full pipeline for turning a Jira ticket into a delivered
module user manual: scope → live UAT walkthrough → **Gate A** (coverage
validation) → docx build → export/QC → **Gate B** (content/formatting
validation) → delivery. Three governing documents already live at the repo
root and hold the actual rules — this skill sequences them and adds
operational lessons not yet folded into those docs. It does not restate what
they already say.

## Read First, In Order

1. `README.md` (repo root) — folder map, end-to-end workflow, deliverables list.
2. `Playwright-Full-Coverage-Instructions.md` (repo root) — how deep the UAT
   walkthrough must go. Default is full depth immediately, never a
   breadth-only/title-only pass.
3. `User-Manual-Production-Instructions.md` (repo root) — what the manual
   document itself must contain: structure, hard content rules, numbering
   safety, screenshot rules, pre-delivery validation checklist.
4. `gotchas.md` (this skill folder) — operational/environment lessons learned
   across prior module updates that aren't written into the two docs above.

Do not skip ahead to writing UAT steps or manual content without reading the
governing doc for that phase first — each was written because skipping it
caused real, repeat-costing rework.

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
2. **Walk UAT.** Drive the browser with `playwright-cli` only — never a
   project-specific test framework/agent that might also exist in the repo.
   Follow the full Coverage Standard in `Playwright-Full-Coverage-Instructions.md`.
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
5. **Build.** Copy `Scripts/build_manual_template.py` into
   `<Module>-Manual-Update/`, fill in CONFIG, write content with its helper
   functions. Follow its docstring's required operation order exactly.
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
that a `playwright-cli` session is already authenticated and reusable
(`playwright-cli list`/`tab-list`). Its job is to build its OWN table by
actually re-driving a meaningful sample of the flagged items live and
cross-checking every screenshot file exists and shows what it's claimed to
show — not to grade a table you hand it as already-true.

Example dispatch prompt (adapt names/paths):
```
Independently verify UAT coverage for the Batch Reversal screen (Term
Deposit module, ticket PF-99999). Screens/controls to check: [list]. A
playwright-cli session is already logged into UAT (playwright-cli
list/tab-list to find it). Screenshots claimed so far are in
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

Runs after `Scripts/to_pdf_export.py` (which re-saves the docx with a
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

**Mechanical — `Scripts/qc_audit.py`** against the freshly re-saved docx
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
Validation" in `User-Manual-Production-Instructions.md` for the full
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
  version" language in `User-Manual-Production-Instructions.md`** — that
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

## Quick Reference — Scripts/

| Script | Purpose |
|---|---|
| `build_manual_template.py` | Numbering-safe docx build helpers (headings, fields, images, OOXML numbering). Copy into the module folder — don't run as-is. |
| `to_pdf_export.py` | Word-COM PDF export with forced TOC/field refresh; re-saves the docx with that refresh applied — always QC the file this writes, not the build script's raw output. |
| `qc_audit.py` | Standalone pre-delivery QC: Word-open check first, duplicate-screenshot byte-hash, numbering simulation, stale-embedded-number check, `--baked-in-numbering` for documents with no live numbering (e.g. SCO). Run `--help` for flags. |
| `fix_accounts_collateral_formatting.py` | One-off formatting-repair script from a prior round — read before reusing; likely needs adapting, not running verbatim. |

## Common Mistakes

See `gotchas.md` for the full list of environment/session traps (backend
outages, Word process locks, browser visibility, stale sessions) and subtle
content bugs (screenshot state-swaps, test-data pollution, cover-page vs
header version drift) collected across every module update so far.
