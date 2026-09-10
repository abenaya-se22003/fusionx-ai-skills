---
name: functional-testing
description: Use when a Jira ticket, requirement/spec document, test-case list, or ad hoc request asks to functionally test a FusionX module end to end — verifies UI behavior across full transaction lifecycles (create/edit/submit/approve/reject/delete, not read-only), traces where validated values, dropdown options, and derived data actually originate (cross-module API calls, config/settings screens), and — when a codebase connection is configured — cross-checks observed behavior against the actual implementation.
---

# Functional Testing

## Overview

Orchestrates full QA-style functional testing of the live FusionX UI: not
just "does the button work" but "where does this value actually come from,
and does the code actually implement the rule the UI appears to enforce."
Runs as a skill (not a top-level Agent) because it needs a human for login,
plan confirmation before any action runs, ambiguity Q&A, and pauses before
destructive/irreversible actions. The actual test execution, independent
re-verification, data-lineage tracing, source-code cross-check, and defect
write-up are each done by a fresh, single-purpose subagent dispatched from
here — never by this skill's own thread, and never by re-using a subagent
that already has a stake in the work it would be re-checking.

This skill is independent of the `fusionx-test-agent-v0.1.1` tool. That tool
is deliberately Read-Only Discovery only in its v0.1. This skill is not —
it performs full create/edit/submit/approve/reject/delete transaction
testing with disposable UAT data wherever the environment authorizes it.
Do not import that tool's read-only restriction here.

## Prerequisites

- A live, human-authenticated browser session via the project's configured
  browser-automation tool (e.g. Playwright MCP or `playwright-cli`).
  Executor, Traceability, Verifier, and Defect-Triage all attach to this
  same session per the Subagent Dispatch Rules — none of them logs in
  itself.
- That tool must be able to capture raw network requests/responses
  correlated to the action that triggered them — this is not optional
  instrumentation, it's what Executor's evidence, Traceability, and
  Defect-Triage's root-causing all depend on (see the global instructions'
  root-cause rule and Stage 5's network-capture instruction). Confirm this
  capability actually exists before Stage 2 — many browser MCP tools expose
  only navigate/click/snapshot, not network interception. If it isn't
  available, this is a real environment limitation: surface it plainly at
  Stage 0, the same as any other blocker, and let the user decide whether
  to proceed with UI-observable evidence only (state this limitation in
  every affected round's report, not just once) or pause until a capable
  tool is configured. Never substitute a screenshot for a missing
  network-capture entry and call the evidence requirement met.
- `Agent` tool access, to dispatch the five roles described throughout
  Workflow below.
- `Read`/`Grep`/`Glob` file access, for Source-Verifier — only needed when
  a codebase connection is configured for the round.
- `Write` file access for every dispatched role, per the Subagent Dispatch
  Rules — each writes its own artifacts directly.
- `../user-manual-update/gotchas.md` (referenced below) is a sibling
  skill's file in this same repo, not a hard dependency: if it doesn't
  exist in a given checkout, note that in the round's plan header and
  proceed without it — it's supplementary operational knowledge, not
  something Stage 0 blocks on.

## Read First, In Order

1. Your global Playwright Full-Coverage Instructions (`~/.claude/CLAUDE.md`)
   — session/login handling, the Coverage Standard, Dropdowns and
   Selectable Controls, Search and Filtering, Transaction Testing, Evidence
   Capture, Ant Design/virtualized-UI quirks, and the AUDIT-LOG.md/
   FLOWS-LOG.md convention. This skill inherits all of it and does not
   restate it — read it before starting, not after hitting a gap it would
   have covered.
2. `../user-manual-update/gotchas.md` — FusionX UI/environment quirks
   already learned (Ant Design virtualization specifics, sticky-header
   click interception, slow-confirm screens with no progress indicator).
3. `gotchas.md` (this folder) — functional-testing-specific lessons.
4. `docs/evidence-and-bug-policy.md` (from `fusionx-test-agent-v0.1.1`, if that
   repo is checked out) — evidence-minimization rules: mask/omit credentials
   and auth data, store the minimum necessary. The Bug Report template's
   Evidence section and the global Playwright instructions already operationalize
   this; read the policy doc for the fuller rationale if available.
5. The Templates section below. If the `fusionx-test-agent-v0.1.1` repo
   happens to be checked out in the current project, its `templates/`
   directory has the canonical originals these were adapted from
   (`test-plan.md`, `bug-report.md`, `coverage-report.md`,
   `run-summary.md`) — prefer those if present, they're the same shapes
   inlined here so this skill works even when that repo isn't available.

Do not skip ahead to running a test round without reading the governing
Playwright instructions first — every rule in there exists because skipping
it caused real, repeat-costing gaps in prior sessions.

## Workflow

### 0. Check standing state

At the target project root, read `AUDIT-LOG.md`, `FLOWS-LOG.md`,
`DEFECT-LOG.md`, and `DATA-LINEAGE.md` if they exist — don't re-derive from
scratch what a prior round already established. If any are missing, create
them now with a minimal header rather than waiting until the Reporting
stage — an empty file that exists is easier to append to correctly than one
whose absence gets missed later. The minimal header is literally:
`# <Filename, e.g. Audit Log>` followed by a blank line and `No entries
yet.` — identical shape for all four files, only the title line changes.

Also ask (or check a prior round's plan header for the answer already on
record): is a codebase connection configured for this target — a local
path or checkout the automation can actually read? "Configured" means the
user has told you (this round or a prior one) a local filesystem path to
a checked-out copy of the codebase — there is no separate setup step or
config file; if that path isn't already on record, asking the user for it
is what "checking" means here. If yes, record the path
in this round's plan header and the Source-Verifier stage (8) runs. If no,
record "Source-Verifier: not available — no codebase connection configured"
in the plan header and skip stage 8 later — note the skip explicitly in the
round's report too, never silently. The Test Plan template's header has a
"Codebase connection" field for exactly this (same value shape as the Run
Summary template's field of the same name) — that's where this gets
recorded; it is not a separate file or a new artifact.

### 1. Intake

Accept any of: a Jira ticket, a requirement/spec document, a test-case list,
or any other source document. If none is given, or the request is ad hoc
("test the X screen"), ask the user directly what needs covering before
doing anything else — module, screens/flows, specific business rules, and
any known risk areas. Don't guess scope from a screen name.

If the user's answer stays non-specific even after being asked (e.g. "just
test it thoroughly, whatever you think is important" with no named field,
rule, or ticket), that is not a blocker to proceed past — it means no
specific change exists to narrow against, so the "specific change" branch
below does not apply and the global Playwright instructions' full-depth
default applies unmodified: Discovery covers the full Coverage Standard
across every screen/flow in the named module from the start, not a
progressively-expanding subset. Record the Test Plan's "Requirement/source"
field as the plain fact of what was given, e.g. "Ad hoc verbal request —
no ticket/spec: 'test the Savings module thoroughly'" — never leave it
blank or invent a ticket number that doesn't exist.

If multiple source documents are given or discovered (e.g. a ticket that
links to a design/spec doc) and they disagree on the actual business rule
to be tested (e.g. one says a 30-day minimum, the other says 45), that is
unresolved ambiguity the same as the no-source case above — escalate it to
the user for a single confirmed resolution before drafting the plan at
Stage 3. Don't average the values, guess which document is authoritative,
or write more than one candidate into the Test Plan's Expected column.
Record what was decided as the plain fact in the Requirement/source field,
e.g. "Ticket specifies 30 days, linked design doc specifies 45; user
confirmed 45 is authoritative." This same escalate-before-finalizing rule
applies if Discovery later observes a live configured value that agrees
with neither original source (e.g. the config screen actually shows 60) —
that is a new discrepancy to put back to the user the same way (per the
Error Handling section's escalation rule) before the plan's Expected column
is finalized, not a reason to silently substitute whichever value was found
live.

If the source names a **specific change** (a ticket describing one new
field, one modified validation rule, etc.), scope Discovery's first pass to
exactly that change and its immediate dependents — the field's own
validation rule, any config/settings screen supplying a threshold or
default it uses, and any other screen that reads or displays the same
field or value — then expand to the full Coverage Standard for the
surrounding screen only if time/scope allows. Don't spend the first pass
spread evenly across an entire module when the source document already
tells you where the risk is concentrated.

This narrow-then-expand scoping is a deliberate, sanctioned exception to
the global Playwright instructions' full-depth-first default — it still
needs the same explicit user sign-off that default requires for any
narrowed pass. State the narrow scope in the drafted plan's "Scope and
exclusions" field so the user is approving it at the Stage 4 gate, not
learning about it afterward.

If the request is to verify whether a previously logged defect is actually
fixed (the user names a specific `DEFECT-LOG.md` entry, or a ticket says
something like "verify fix for X"), treat this as a retest: draft one Test
Plan row per referenced entry, Scenario cell prefixed `[retest: <Bug Report
Summary or entry identifier>]` — the "entry identifier" is simply the exact
`# [Summary]` heading text of the entry being retested, since that heading
is the only handle `DEFECT-LOG.md` provides; there is no separate ID scheme
to invent. If the named entry can't actually be found in `DEFECT-LOG.md`,
that's the same unresolved-ambiguity case as Stage 1's no-source-document
handling above — escalate to the user for the correct entry rather than
guessing which one was meant or silently treating the round as a fresh
defect search.

Check the referenced entry's own Reproduction steps before drafting the
row: if they describe a UI/API action (a functionally observable symptom),
this is a **functional retest** and everything below in this section
applies unchanged. If instead they describe a code-inspection step (a
Source-Verifier-originated finding per Stage 8 — the dynamic-vs-hardcoded
contradiction case, logged even though the corresponding functional row
was CONFIRMED because the UI happened to look correct that day), this is a
**code-only retest**: only Source-Verifier can actually re-check whether
the contradiction is still there, so this round must be type B or C with a
codebase connection configured. If the user picked type A, or no codebase
connection is available, that's a blocker on this row the same as any
other input the skill can't act on — escalate before finalizing the plan
at Stage 4 rather than letting Stage 7's functional CONFIRMED (which was
never in dispute for this entry) silently stand in for a resolution it
can't actually speak to. See Stage 8 and Stage 10 for how a code-only
retest's resolution gets decided and written.

Use that entry's own Reproduction steps
and Expected result as the row's Steps/Expected — Discovery (stage 3) still
confirms the screen/flow is actually reachable before finalizing the row
(per the selector-drift gotcha, a UI release since the original defect was
logged may have moved things). If the live path has genuinely moved,
update the row's Steps to the current path rather than copying the stale
one verbatim, and note the change (e.g. "field moved from Tab A to Tab B
since original defect") — this is the same selector-drift correction
`gotchas.md` already describes for `DATA-LINEAGE.md` rows, applied here to
a Test Plan row instead. This does not need to rediscover the scenario
from scratch. If the user asks to retest every open, claimed-fixed, or
still-failing defect for a module rather than naming one (i.e. every entry
that isn't already `Retested — resolved` or `Won't fix`), draft one row per
matching `DEFECT-LOG.md` entry the same way. A retest row's outcome is
written back into the referenced Bug Report entry's Resolution status field
in place — see Stage 9 and Stage 10 — rather than a new entry, unless the
retest surfaces a genuinely different symptom than the entry describes, in
which case that different symptom does get its own new entry (Stage 9).

### 2. Round-type selection

Ask the user (one question, multiple choice) which round type applies:

- **A. Functional only** — verifies behavior, no data-lineage tracing.
- **B. Functional + full traceability** — every action's underlying network
  calls get traced to their source.
- **C. Functional + targeted traceability** — only actions flagged as
  config/cross-module-driven during Discovery get traced.

This must be decided before the plan is drafted — it changes what Discovery
needs to flag and what the Executor needs to capture.

### 3. Discovery & Planning (main thread, human-authenticated browser)

- Navigate the target screens/flows named by Intake.
- Take snapshots; enumerate every control per the Coverage Standard
  (buttons, dropdowns, tabs, modals, nested records, row actions, etc.).
- Regardless of round type, flag candidates cheaply: any dropdown, field,
  or derived value that looks config-driven, validated against another
  module, or calculated rather than directly entered. "Cheaply" means
  labeling what the required Coverage Standard pass already surfaces (you
  open every dropdown anyway to enumerate its options — flagging is just
  noting which ones look config-driven while you're already there) — it is
  not a shortcut that lets you skip opening a control, and it does not
  defer or replace the full-depth pass the global instructions require.
  Actually chasing down the source screen is Traceability's job (stage 6),
  not Discovery's.
- A numeric or validated field whose actual expected value or rule changes
  depending on a selectable value elsewhere on the form (e.g. a fee
  calculation whose rounding convention differs by currency, or a threshold
  that differs by product type) is subject to the same per-value branch
  testing the inherited Coverage Standard already requires for any dropdown
  or selector: draft one Test Plan row per value that changes the rule
  (e.g. one row per currency), not one row that picks a single
  representative value and calls the field covered. This isn't new scope —
  it's the existing "select every value that changes validation/behavior"
  rule from the global instructions applied to a field whose branching
  driver happens to be a currency/product selector rather than the field's
  own dropdown.
- A UI language switcher is a selectable control the same as any other, so a
  screen tested under one language and never re-checked in a second
  supported language is not fully covered — apply the same per-value branch
  rule above, treating each supported language as a value. Record each
  language's exact displayed labels separately (the global "record every
  static value exactly as displayed" rule applies per language, not just
  once); note in the Evidence column or the screenshot filename which
  language the evidence was captured in so a later reader isn't left
  guessing which language a given Pass/Fail reflects. Separately from the
  displayed-label branch, confirm the underlying submitted/stored value
  (the option code sent to the API, visible in the network-capture log
  Executor already produces regardless of round type) stays identical
  across languages even though its displayed label changes — this is an
  ordinary functional assertion using evidence the pipeline already
  captures, not a new capture requirement.
- Check `DATA-LINEAGE.md` for each flagged candidate. "Already mapped" means
  that exact `Module.Screen.Field` has its own existing row — a different
  field is its own row and starts as `[discover]` even if you suspect it
  shares a source with an already-mapped sibling field (e.g. two dropdowns
  on the same form); don't inherit one field's row for another, let
  Traceability confirm each field's actual source empirically. If already
  mapped, mark it "reconfirm" rather than "discover" in the plan — don't
  rediscover a dependency already on record. The Test Plan template has no
  separate column for this — record it as a `[discover]` or `[reconfirm]`
  prefix on the row's Scenario cell. Both `[discover]` and `[reconfirm]`
  rows are members of the flagged-candidate list carried into stage 6 for
  round type C — "reconfirm" doesn't mean "exclude from tracing," it means
  "trace it again against the known source" rather than starting from
  scratch.
- A `[retest]`-prefixed row (Stage 1) still gets a live navigation check
  during this Discovery pass — confirm the screen/flow the referenced
  `DEFECT-LOG.md` entry describes is still reachable as described; don't
  skip straight to drafting the row from the Bug Report entry's text alone.
  If the same field is also an on-record `DATA-LINEAGE.md` candidate, that's
  a separate row with its own `[discover]`/`[reconfirm]` prefix, not the
  same row carrying two prefixes — a retest verifies a defect's resolution,
  tracing a value's source is a different question, and the Test Plan has
  no shape for a row answering both at once.
- Draft the round's plan using the Test Plan template below and save it as
  `FUNCTIONAL-TEST-PLAN-<topic>.md` at the target project root (not in this
  skill repo). `<topic>` is a short kebab-case label for the module/feature
  under test this round (e.g. `lending-collateral-coverage-ratio`) — pick
  something specific enough to tell this round's files apart from another
  round's in the same project. Include the scenario table, safety
  authorization, and data strategy (which records are newly created for
  this round vs. existing UAT records being reused — see the global
  instructions' Transaction Testing section for why both matter).
- Explicitly flag any planned step that is destructive/irreversible with no
  disposable UAT record available — these become pause points for the
  Executor, not silent skips. Flag it in the plan header's
  "Destructive/irreversible steps flagged" field by row ID (e.g. "Row 5 —
  Delete approved Term Deposit — no disposable record available"); the
  Test Plan table itself has no separate column for this.

### 4. Confirmation gate

Present the drafted plan file to the user. Do not proceed until they
explicitly approve it. If they push back, revise and re-present — never
narrow scope silently and continue as if it were approved. "Revise" means
editing the same `FUNCTIONAL-TEST-PLAN-<topic>.md` file in place (patch
only the rows/fields the feedback actually addresses; don't regenerate
rows the user didn't object to, and don't keep the rejected version as a
separate file — the log entry made at Stage 10 will reference the plan as
it stood when finally approved, not its rejected drafts). If the feedback
names coverage that wasn't part of the original plan (a new scenario, a
different record type, a missed variant), that's a real scope addition —
go back to Stage 3 and actually navigate that flow live before drafting
its row, the same Coverage Standard bar as the original pass; don't draft
a new row purely from the user's description without Discovery having
looked at it.

### 5. Executor dispatch

Dispatch one fresh `Agent` tool call, `subagent_type: "general-purpose"`,
`run_in_background: false`. The prompt must include, verbatim:

- The full confirmed test plan (every row).
- That it operates the **same already-authenticated browser session** —
  it must not attempt its own login or assume a fresh unauthenticated
  session.
- The Transaction Testing rules from the global instructions: full
  lifecycle testing (create/edit/submit/approve/reject/delete) with
  disposable UAT data where authorized — this is not a read-only pass.
- The Dropdowns and Selectable Controls, Search and Filtering, and Evidence
  Capture rules from the global instructions.
- This skill's own Error Handling section (below) — in particular: never
  click a destructive control merely to inspect it without a disposable
  record; stop at the confirmation dialog (it's fine to open it and
  screenshot it) rather than confirming the destructive action itself.
- This explicit instruction: "Record raw network requests/responses for
  every action you perform, tagged with the action that triggered them, in
  a network-capture log file named `NETWORK-CAPTURE-<round-id>.md` at the
  target project root — one heading per action, followed by its raw
  request/response pairs underneath. Do not summarize them away —
  Traceability and Verifier need the raw entries." `<round-id>` is a short
  sequential label unique within the target project (e.g. `round-1`,
  `round-2`) — check existing `TEST-EXECUTION-REPORT-*.md` files at the
  project root for the highest number used so far and increment it; use
  `round-1` if none exist yet. Use the same `<round-id>` for every artifact
  this round produces (network-capture log, test-execution report).
- This explicit instruction: "If you reach a destructive/irreversible
  action with no disposable UAT record available, or a genuinely ambiguous
  step the plan doesn't resolve, stop and report back rather than deciding
  either way yourself." When Executor reports back on one of these, the
  main thread applies the Error Handling section's escalation rule: tell
  the user and ask whether to keep investigating (e.g. authorize the action
  anyway, or source a disposable record) or stop and document the row as
  Blocked as-is. Never resume Executor with a unilateral decision, and never
  treat "reported back" as itself a completed row — it stays open until the
  user's answer resolves it one way or the other.
- If a row's precondition depends on a scheduled/external event outside the
  automation's control (a batch job, an overnight accrual posting, anything
  that happens on a clock rather than on demand), Executor does not sleep or
  poll for it within one dispatch. Complete every row that's checkable now,
  explicitly report which rows are pending until the event occurs and roughly
  when that is, and stop there — same "stop and report back" shape as any
  other blocked step, just triggered by time instead of missing data or
  authorization. The main thread re-dispatches a fresh Executor call for the
  pending rows only, after the event has occurred.

Expected output: one evidence-backed result per plan row (not bare
pass/fail — a screenshot/state reference and what was actually observed),
plus the network-capture log file.

### 6. Traceability dispatch

Skip this stage entirely for round type A.

For B or C, dispatch one fresh `Agent` tool call (same subagent_type/
foreground settings as Executor). Input list is **all** captured actions
for type B, or **only the flagged candidates** from Discovery for type C —
same prompt shape either way, only the input list changes. The prompt must
include:

- The Executor's network-capture log (or the relevant slice of it).
- The flagged-candidate list (for type C) or full action list (type B).
- This instruction: "For each entry, identify the actual API endpoint(s)
  called. Then navigate to the screen you believe is the true source of
  that value (commonly a Settings/Configuration module screen) and confirm
  it directly — don't infer the source from the endpoint name alone.
  Update `DATA-LINEAGE.md` at the project root (see the Data Lineage
  template below for the exact row format): add a new row, or refresh the
  'Last reconfirmed' date on an existing one — but only after you've
  actually re-navigated to the source screen and re-checked it this round;
  never bump the date without having actually rechecked it. If you looked
  and found no admin/config screen at all in the UI/API — the value appears
  hardcoded, computed, or served by an external system with nothing to
  navigate to — that is itself a confirmed finding at the UI level: record
  the source screen as `no config screen found in UI (suspected hardcoded)`
  (or the equivalent), not as unconfirmed. You don't have codebase access,
  so don't claim it's definitely hardcoded in code — that's confirmed or
  refuted by Source-Verifier in stage 8 if a codebase connection exists.
  Only use `UNCONFIRMED` when you simply haven't been able to locate the
  source yet and more digging might still find it — do not silently drop
  either kind of entry or mark it resolved when it isn't. Trace exactly one
  hop per `DATA-LINEAGE.md` row: confirm the immediate source screen for
  the field you were given, and stop there for that row. If, while
  confirming it, you notice the source screen's own value is itself
  populated from yet another screen (a second hop), don't chase the chain
  inside the same row — add a second, separate `DATA-LINEAGE.md` row for
  that intermediate screen's own field (e.g. `CommonModule.RiskCategoryMaster.ActiveStatuses`),
  starting as `[discover]` the same as any newly-flagged candidate, so the
  chain is represented as multiple one-hop rows linked by matching
  `Module.Screen.Field` values rather than one row trying to hold multiple
  hops. Confirm that second row this round if time allows; otherwise flag
  it in the round's report as a follow-up `[discover]` row for next round,
  the same way any other time-boxed deferral is recorded."

### 7. Verifier dispatch

Dispatch one fresh `Agent` tool call with **no shared context** with
Executor or Traceability — it must not see their claimed results, only:

- The confirmed test plan (every row), exactly as given to Executor.
- Which round type was selected, and — if B or C — the same
  flagged-candidate list (type C) or full action list (type B) that was
  given to Traceability, so Verifier knows exactly which
  `DATA-LINEAGE.md` rows are in scope this round. This is scope
  information, not a claimed result — it doesn't compromise independence to
  tell Verifier which rows exist to check, only what Traceability claimed
  about them.
- For a row whose expected result depends on a scheduled/external event (a
  batch job, an accrual posting, anything time-gated rather than on-demand),
  confirm the event has actually already occurred before recording a result
  — check a timestamp, status field, or downstream effect that proves it ran,
  don't just check as soon as dispatched and assume enough time has passed.
  If it plainly hasn't occurred yet, that's not-yet-due, not a result: report
  it back the same as any other unmet precondition rather than recording a
  premature Pass/Fail.
- This instruction: "Independently re-derive the actual result for every
  row yourself — re-navigate, re-check the live state, re-read the actual
  screen or data. Do not read or trust any prior claimed result. This is a
  full re-check of every row, never a sample. Where the plan's data
  strategy calls for a newly created record, create your own fresh
  disposable record and execute the row's steps against it — don't ask for
  or rely on the specific record Executor created; an independent check
  means an independently produced result, not a re-read of Executor's
  artifact. Where the row instead uses an existing shared UAT record, confirm
  it's actually in the precondition state the plan describes before acting
  on it — a shared record can drift between Executor's pass and yours for
  reasons outside this round (see the Error Handling section's shared-record
  check); if it isn't in the expected state, that's an environment finding
  to report, not something to silently proceed past or assume Executor
  caused. If this round included traceability, independently re-confirm
  every `DATA-LINEAGE.md` row in scope this round the same way —
  re-navigate to the claimed source screen yourself. For a row flagged in
  the plan header as destructive/irreversible with no disposable UAT record
  available, do not attempt the destructive action yourself either — that
  flag applies to you the same as it applied to Executor. Instead confirm
  the record is still unchanged and that Executor's stop was genuine (not a
  fabricated 'blocked' claim covering for work not actually attempted), then
  return BLOCKED for that row. Return CONFIRMED, REJECTED, or BLOCKED per
  row, each with its own fresh evidence — BLOCKED is for when the row's
  precondition or environment genuinely prevents execution (missing data,
  screen unreachable, a flagged destructive step with no disposable record),
  not for when the observed behavior simply fails to match expectation,
  which is REJECTED. Write this evidence — your per-row result plus
  screenshot/state references, and, for any row involving an API
  interaction, the raw request/response you observed during your own
  independent execution — to `VERIFIER-FINDINGS-<round-id>.md` at the
  project root (same `<round-id>` as this round's other artifacts); one
  heading per row. Downstream stages read Verifier's evidence from this
  file, not from Executor's network-capture log, for whatever Verifier
  itself independently observed."

If Verifier's evidence contradicts Executor's or Traceability's claim, the
Verifier's independently-derived result is what's recorded — flag the
discrepancy itself as a finding too (it usually indicates the earlier
subagent reported an unverified guess). Record this discrepancy in the
round's `AUDIT-LOG.md` entry at stage 10 (per that stage's process-narration
rule: this is exactly the kind of prior-finding-corrected note that belongs
there), naming which stage's claim was wrong and what the independent
re-check actually found. Do not add a discrepancy field to the Test Plan,
Bug Report, or Run Summary templates — those stay to the clean, current-state
facts (the row's final Status, and — if the underlying behavior is a
confirmed defect — its Bug Report), per stage 10's rule against process
narration in user-facing deliverables.

For a `DATA-LINEAGE.md` row specifically, the same override applies to the
row's content, not just the round's narrative: if Verifier's independent
re-check of the claimed source contradicts Traceability's — a different
screen, no screen at all where Traceability claimed one, or a screen found
where Traceability claimed none ("suspected hardcoded") — Verifier writes
its own finding directly into that row's Source/config screen and
Verification method fields, superseding Traceability's claim, the same way
Verifier's result already supersedes Executor's for a functional row. When
Verifier's correction is itself a "no config screen found" finding, record
it using the exact same phrasing Stage 6 already defines for Traceability's
version of this finding-shape (`no config screen found in UI (suspected
hardcoded)`) and set Verification method to `UI/API observation` — the same
as any other Traceability/Verifier-only finding not yet cross-checked
against code; this is a confirmed UI-level finding, not `UNCONFIRMED`, the
same distinction Stage 6 already draws. The
discrepancy itself still goes into the round's `AUDIT-LOG.md` entry per the
paragraph above. Stage 8 (Source-Verifier) always reads whatever
`DATA-LINEAGE.md` currently says at the time it runs — since this
correction happens here, before stage 8, Source-Verifier automatically
checks the corrected claim, not the superseded one; no separate re-dispatch
of Traceability is needed to fix its own row.

### 8. Source-Verifier dispatch

Skip entirely if the standing-state check (stage 0) recorded no codebase connection — note
the skip in the round's report at stage 10, don't just drop it quietly.

If a codebase is configured, dispatch one fresh `Agent` tool call (with
`Read`/`Grep`/`Glob` access to the configured codebase path — it doesn't
need browser access, it never touches the live app) for **each** of these
input sets that has entries this round. If the frontend and the
backend/config service live in separate repos and the user has given you
more than one path, record each in the plan header and point Source-Verifier
at whichever repo actually contains the relevant module — or grant access to
all configured paths if the boundary isn't obvious and let it search across
them. If the recorded path turns out not to exist or isn't readable when
Source-Verifier actually tries it, that's a genuine blocker, not a silent
skip — apply the Error Handling section's escalation rule (tell the user;
don't fabricate a finding or quietly treat the round as if no codebase were
configured).

A readable, existing codebase path that returns zero results for an obvious
search (the field name from the UI, the class name you'd expect) is not by
itself evidence the code doesn't exist — a recent refactor can rename
fields/classes and move logic across files without changing what the UI
does. Include this in Source-Verifier's dispatch prompt for both input sets
below: "If your first search (the exact field/class name) returns nothing,
don't conclude 'not implemented' from that alone — broaden the search
before reporting a negative result: try the business-logic term itself
(e.g. 'coverage ratio', 'collateral'), the API endpoint path or a fragment
of it, the config/settings key name Traceability observed, and a directory
listing of the module area the endpoint or screen name suggests. Only report
'not found in code' as a finding once you've tried more than the one obvious
pattern and state which search strategies you actually tried — a bare 'not
found' with no record of what was searched is not a usable finding." A
Source-Verifier report that claims "not found" without naming the search
strategies attempted doesn't satisfy this stage's instructions — per the
Error Handling section's subagent-retry rule, dispatch one fresh retry with
this instruction restated before accepting the negative result and passing
it on to Reporting or Defect-Triage. This is a distinct case from round 5's
path-inaccessible escalation (below): here the path is fine and readable,
the search was just insufficient — no need to involve the user unless a
genuinely thorough search (multiple strategies, stated) still comes up
empty, in which case report it plainly as "not located in code despite
searching for X, Y, Z" rather than a flat "not found."

A `DATA-LINEAGE.md` row that a prior round already verified as "source code
(file:line)" and that Traceability reconfirmed this round with no change to
the claimed source doesn't need Source-Verifier to redo the same code check
— carry the prior "source code" verification forward. Only dispatch
Source-Verifier again for a reconfirmed row if the row's claimed source
changed this round for any reason — either Traceability's own reconfirm
found something different from what was on record before, or Stage 7
(Verifier) overwrote the row with a correction per its lineage-correction
rule. A Stage 7 correction always invalidates any carry-forward for that
row, even if Traceability itself reported no change — Traceability and
Verifier can disagree about the same row in the same round, and it's
Verifier's version that's current once stage 7 has run. This carry-forward
optimization is about whether Source-Verifier re-checks a *data-lineage*
source claim — it has nothing to do with whether a `[retest]` row (Stage 1)
counts as fixed. A retest's Pass/Fail always comes from Verifier's own
independent functional re-check at stage 7, never from a carried-forward
Source-Verifier result; there is no "skip re-verifying because nothing
changed" shortcut for a retest's actual functional outcome.

- Every `DATA-LINEAGE.md` row Traceability added or reconfirmed this round
  with a confirmed source (round types B/C only) — skip any row Traceability
  recorded as `UNCONFIRMED`; there's no claimed source yet for Source-Verifier
  to check code against, and that stays open as a Traceability gap, not a
  Source-Verifier task. A row Stage 7 corrected to
  `no config screen found in UI (suspected hardcoded)` counts as a
  confirmed source for this purpose the same as any of Traceability's own
  findings of that shape (per Stage 7's note above) — it is not treated as
  `UNCONFIRMED` and is not a separate third input set. Prompt: "Given this claimed data source (module,
  screen, API endpoint, and the config/settings screen currently recorded
  in the row — this may be Traceability's original finding or a later
  Stage 7 correction; use whichever is currently on record), find the
  actual code that implements this — the validation
  rule, the query, or the config lookup. Confirm whether the code's real
  behavior matches what Traceability observed from the UI/API alone (for
  example: a dropdown that looks config-driven from the API response but
  is actually hardcoded in code, or a threshold that looks configurable
  but has a hardcoded override). Specifically check whether the code reads
  the config/settings value dynamically at runtime, rather than merely
  containing a value that happens to currently match it — a hardcoded
  constant that coincidentally equals today's config value will silently
  diverge the next time someone changes the setting. Report file/line
  references. If the code contradicts the UI-observed behavior, say so
  explicitly — that is a finding, not a detail to smooth over."
- Every Verifier-REJECTED row — include the test plan row (Scenario,
  Preconditions, Steps, Expected), Verifier's own evidence for the
  rejection (its entry in `VERIFIER-FINDINGS-<round-id>.md`), and the
  relevant slice of Executor's network-capture log so Source-Verifier has
  the actual test context (what was tested, with what data, and what the
  app actually returned), not just a bare pass/fail claim. Prompt:
  "Given this failing case (what was expected, what was actually observed),
  find the code path responsible and identify the precise cause — not just
  'it fails' but the actual faulty condition, missing check, or incorrect
  value in the code. Report file/line references. If you cannot locate the
  responsible code, say so plainly rather than guessing." Source-Verifier
  does static analysis only — it has
  no browser access and cannot retry the scenario live; that's
  Defect-Triage's job in stage 9. If the same field also has a
  `DATA-LINEAGE.md` row in scope this round, one combined dispatch covering
  both questions (lineage confirmation and failure root-cause) is fine —
  no need for two redundant dispatches against the same code area.
- Every code-only `[retest]` row (per Stage 1's routing) — this round's
  round type is already confirmed B/C with a codebase connection per that
  routing rule, so this dispatch is never skipped for such a row. Include
  the referenced `DEFECT-LOG.md` entry's file/line finding from when it was
  originally logged. Prompt: "Re-check the exact code location this entry
  originally identified. Does it still fail to read the config/settings
  value dynamically at runtime — the same contradiction as before — or does
  it now read it correctly? Report file/line and state plainly which of the
  two it is; this determines whether the referenced defect is resolved."
  This dispatch's result — not Verifier's functional CONFIRMED for the
  corresponding row, which was never in dispute — is what stage 10 records
  as the retest's outcome for this entry.

Source-Verifier updates `DATA-LINEAGE.md`'s "Verification method" column
itself (it has the same write access as every other dispatched role, per
the Subagent Dispatch Rules) — set it to `source code (file:line)` rather
than leaving it at `UI/API observation` for whichever rows it cross-checked
against the implementation. Stage 10 (Reporting) summarizes this in the Run
Summary; it does not independently re-edit `DATA-LINEAGE.md`. Source-Verifier's
output also feeds into stage 9 (Defect-Triage): as well as rejected rows,
dispatch Defect-Triage for any `DATA-LINEAGE.md` row Source-Verifier flagged
as contradicting the UI-observed behavior (e.g. a hardcoded value that
coincidentally matches today's config) — this is a real finding even when
Verifier returned CONFIRMED for the corresponding functional row, since the
UI behavior looked correct today but the underlying implementation is wrong.
Its Bug Report entry's Reproduction steps describe how to observe the
contradiction, not a UI failure — e.g. "Read the configured value at
[screen]; inspect [file:line] and confirm the value is a fixed constant,
not read from that config at runtime" — and Expected/Actual describe the
code behavior (expected: reads config dynamically; actual: hardcoded
constant), not a click-path pass/fail.

### 9. Defect-Triage dispatch

Only if Verifier returned any REJECTED or BLOCKED row, an unconfirmed
lineage gap, or Source-Verifier flagged a `DATA-LINEAGE.md` row as
contradicting the UI-observed behavior (this last case applies even if
Verifier returned CONFIRMED for the corresponding functional row — see
stage 8). Exception: a BLOCKED row that is destructive/irreversible with no
disposable UAT record available, where the user already resolved it at the
stage 5 escalation (e.g. "document as Blocked, don't pursue further"), does
not go to Defect-Triage — there is nothing to retry (no disposable record
exists) and nothing to classify (it isn't an application-behavior question,
it's a data/authorization constraint the user already decided on). Take it
straight to Reporting as a closed Blocked row instead. Only route a BLOCKED
row to Defect-Triage when the block is something Defect-Triage could
plausibly investigate or retry (e.g. a screen was unreachable, environment
data was missing) rather than a destructive step the user already declined
to authorize. Dispatch one fresh `Agent` tool call. The prompt must include:

- Every REJECTED/BLOCKED row, lineage gap, and Source-Verifier-flagged
  contradiction, with Verifier's evidence (its entry in
  `VERIFIER-FINDINGS-<round-id>.md`) and the relevant slice of Executor's
  network-capture log (Defect-Triage needs the actual request/response, not
  just Verifier's narrative, to root-cause before treating anything as
  reproducible).
- Source-Verifier's file/line root-cause findings for that row, if stage 8
  ran and produced one — include it verbatim so Defect-Triage doesn't have
  to re-derive what's already been found; Defect-Triage's job on top of it
  is to confirm reproducibility and write it up, not repeat the code
  investigation.
- This instruction: "Before treating anything as a reproducible defect,
  retry it with at least one different input combination (e.g. a different
  record or product than the one Verifier used — the point is to rule out
  a record-specific quirk, not to repeat the identical case) or a fresh
  session/login. If the retry produces a DIFFERENT failure symptom than the
  original (e.g. the original showed a 0% penalty, the retry on different
  data shows a 5% penalty instead of the expected 2%), that counts as 'not
  reproduced' for the original symptom's Reproducibility field — record it
  as such — and the new symptom is itself a separate finding, never folded
  silently into the original or dropped. Default to writing it up as its
  own Bug Report entry with its own classification and severity, on the
  assumption it's a distinct defect until shown otherwise; only combine it
  into the original row's single entry if your own root-cause investigation
  (or Source-Verifier's, if you can get a fresh dispatch for the new
  symptom and a codebase connection is configured) actually traces both
  symptoms to the same code path or condition. A new symptom discovered
  this way gets the same Source-Verifier treatment stage 8 would have given
  it had it been known then — request a fresh Source-Verifier dispatch for
  it before finalizing its classification if a codebase connection is
  configured, the same as for any other rejected case. Retry the original
  symptom once; if you still can't reproduce it after that one
  retry, don't keep retrying indefinitely — record the attempt count and
  outcome in 'Reproducibility' as-is (e.g. 'reproduced on 1 of 2 attempts')
  and classify accordingly (a failure that won't reproduce on different
  data may be TestDataIssue or EnvironmentIssue rather than
  ApplicationDefect). Root-cause it using the actual network
  request/response and, if provided, the Source-Verifier finding — not
  just what the UI shows. Classify each confirmed defect using exactly one
  of: ApplicationDefect, SuspectedDefect, AutomationIssue, EnvironmentIssue,
  TestDataIssue, ExpectedBehaviour, NeedsBusinessReview — a failure that
  traces to a shared UAT record having been externally modified by someone
  outside this round (confirmed via the audit-trail/last-modified check the
  Error Handling section requires for shared-record rows, not merely a
  differing retry result) classifies as EnvironmentIssue: the app behaved
  correctly against the state it was actually given, the state itself was
  the problem. If it's genuinely
  unclear whether an observed behavior is a defect or intended design, that
  uncertainty is itself what NeedsBusinessReview is for; don't guess, and
  don't stop to ask the user to make this classification call for you (that
  is a routine judgment this stage is trusted to make; it is not the same
  as being genuinely blocked, which the Error Handling section's escalation
  rule still covers — e.g. if you can't access a screen at all). Judge
  'Suggested severity' as Critical/High/Medium/Low by business or
  data-integrity impact — a wrong monetary or regulatory calculation is at
  least High. Write one Bug Report entry (see template below) per confirmed
  defect into `DEFECT-LOG.md` at the project root, appending — never
  overwrite prior entries. Fill every template field yourself from what you
  directly observed or retried — 'Reproducibility' from your own retry
  results, 'Suggested severity' from the business impact of the observed
  failure — don't leave fields blank for the main thread to backfill
  later. For a `[retest]` row (Stage 1) that still reproduces with the same
  symptom the referenced `DEFECT-LOG.md` entry already describes, don't
  write a new entry — update the existing one in place: restate its
  Reproducibility using this stage's normal retry rule above (the
  different-input-or-fresh-session retry still applies to a retest the same
  as any other row — a retest isn't exempt from ruling out a
  record-specific quirk), leave its Classification as-is unless your own
  investigation now points to a different one, and set Resolution status to
  `Retested — still failing`. Leave Environment, Application version, and
  Preconditions/test data as originally recorded unless the retest actually
  used a materially different one of these (e.g. a newer app version) — if
  so, update that specific field to the retest's actual value and note the
  change inline rather than silently overwriting what the original entry
  said. If the retest instead surfaces a different
  symptom than the original entry describes, that's the distinct-new-finding
  case above, unchanged by this being a retest — write it as its own new
  entry, and separately set the original entry's Resolution status to
  `Retested — resolved` (the original symptom didn't reproduce, even though
  a new, different defect was found). A `[retest]` row that Verifier
  returned BLOCKED (and that reaches this stage under this stage's normal
  BLOCKED-dispatch condition above, rather than the destructive-exception
  case that skips straight to Reporting) is inconclusive, not evidence
  either way — investigate whether the block is itself resolvable the same
  as for any other BLOCKED row, but do not set the referenced entry's
  Resolution status to either `Retested —` value on the strength of a block;
  leave it exactly as it was and report the block plainly instead."

### 10. Reporting (main thread)

- Compile `TEST-EXECUTION-REPORT-<round-id>.md` at the target project root
  (not in this skill repo) using the Run Summary template below — the
  clean, user-facing deliverable. No process narration (no "we initially
  thought X" — that belongs in AUDIT-LOG.md). State plainly whether
  Source-Verifier ran this round, ran but couldn't locate a root cause, or
  was skipped for lack of a codebase connection; and whether Defect-Triage
  ran or was skipped. For Defect-Triage skips, distinguish between: no
  REJECTED/BLOCKED rows and no unconfirmed lineage gaps or
  Source-Verifier-flagged contradictions (normal dispatch-skip), versus a
  destructive BLOCKED row the user already resolved at Stage 5 escalation
  (direct-to-Reporting exception; see Stage 9 for the full trigger
  conditions). State explicitly which rows, if any, were Blocked because
  they were destructive/irreversible with no disposable record available —
  this is a legitimate closed outcome (see "Coverage closure result" below),
  not a silently dropped case, unless a disposable record later becomes
  available and the row is re-planned. For
  each defect raised, if Source-Verifier didn't run or found nothing, say so
  directly in the same field rather than leaving it blank (e.g. "source
  file:line not available — no codebase connection configured" or "not
  located in code").
- Update `FLOWS-LOG.md`'s coverage table using the Coverage Report template
  shape below.
- Append one `AUDIT-LOG.md` entry: what was checked this round, what was
  found, with concrete evidence references (file/screenshot names, not just
  "confirmed"). State the current, correct picture as plain fact.

If the user disputes a `DEFECT-LOG.md` entry's Classification after this
report has already been compiled and presented (e.g. Defect-Triage called
something `ExpectedBehaviour` and the user, with business-rule knowledge
Defect-Triage had no access to, says it's really `ApplicationDefect`), the
user's confirmed correction is authoritative — the same as the Stage 1 rule
that a user's confirmed resolution of a business-rule question is
authoritative — and no re-dispatch of Defect-Triage is needed to "re-derive"
what the human already knows. Edit the existing Bug Report entry's
Classification (and Suggested severity, if it also changes) in place; the
"append, never overwrite" rule exists to keep distinct defects from being
lost, not to prevent fixing a wrong field value on an entry that still
describes the same underlying defect. If the already-compiled
`TEST-EXECUTION-REPORT-<round-id>.md` for that round references the old
classification, patch that reference too so the two files don't disagree —
don't regenerate the whole report, and don't add correction narration into
either file. Append a new `AUDIT-LOG.md` entry stating the corrected
classification as the current, correct fact (this is exactly the "a prior
finding turns out to be wrong" case the global instructions already define
for this log) — the "why it changed" story belongs only there. The row's
Test Plan Status is untouched by this: Classification and Status are
independent facts about the same row (Status reflects Verifier's confirmed
functional observation, which didn't change) — a Classification correction
never implies revisiting Pass/Fail/Blocked.

When a round includes one or more `[retest]` rows (Stage 1), update each
referenced `DEFECT-LOG.md` entry's Resolution status field in place. For a
**functional retest** (Stage 1's routing), use Verifier's result once it's
known: `Retested — resolved` if Verifier's independent check confirms the
original symptom no longer reproduces, or `Retested — still failing` if
Stage 9 confirms it still does. For a **code-only retest** (Stage 1's
routing — a Source-Verifier-originated entry with no functional symptom),
Resolution status instead comes from Stage 8's re-check of the same code
location: `Retested — resolved` if the contradiction is gone, `Retested —
still failing` if it's still there — never from the corresponding
functional row's CONFIRMED, which was never in dispute for this entry. For
a functional retest that passes (Verifier CONFIRMED), there's never a
REJECTED/BLOCKED row for Stage 9 to dispatch on, so this stage — not
Stage 9 — is always the one that writes `Retested — resolved`; that is not
a gap, it is simply which stage's own dispatch condition happens to be met.
If Stage 9 already set
this field for the same entry this round (per its own instructions), don't
overwrite it here — this is the same in-place-edit precedent as the
classification-correction rule above: appending a duplicate entry for a
retest of an already-logged defect would fragment one defect's history
across multiple entries instead of keeping it in one place. The Test Plan
row's own Status (Pass/Fail/Blocked) is filled from Verifier's result the
same as any other row — a `[retest]` row that passes gets Status `Pass`
even though the `DEFECT-LOG.md` entry it closes out keeps its full original
history rather than being deleted. A `[retest]` row that came back BLOCKED
— whether Stage 9 reported it inconclusive, or it was the destructive-
exception BLOCKED case that skipped Stage 9 entirely — leaves the
referenced entry's Resolution status exactly as it was; state the block
plainly in this round's report instead of guessing at a resolved/still-
failing outcome the round didn't actually establish.

## Templates

### Test Plan (drafted at Stage 3, confirmed at Stage 4)

```markdown
# Functional test plan — [module/topic]

- Requirement/source:
- Environment/version:
- Roles/browsers:
- Scope and exclusions:
- Round type: A / B / C
- Codebase connection: [path, or "not configured — Source-Verifier skipped"]
- Safety authorization:
- Data strategy: (new records created this round vs. existing UAT records reused)
- Destructive/irreversible steps flagged: (list, or "none")

| ID  | Scenario | Preconditions | Steps | Expected | Evidence | Status |
| --- | -------- | ------------- | ----- | -------- | -------- | ------ |

## Risks, dependencies, deferred work, and exit criteria
```

A row's Status is filled in from Verifier's per-row result once Verifier
has run (stage 7): `Pass` for CONFIRMED where the expected result was
observed, `Fail` for REJECTED, `Blocked` for BLOCKED. Before Verifier runs,
leave Status as whatever Executor observed, labeled provisional — write it
as `<value> (provisional)`, e.g. `Pass (provisional)`. Once stage 7
completes, replace it outright with Verifier's plain `Pass`/`Fail`/`Blocked`
(no provisional suffix) rather than appending to or annotating the
provisional value. For a row Executor stopped and reported back on (stage
5 escalation) rather than observing a result for, the main thread — not
Executor — writes `Blocked (provisional)` directly into the plan once the
user's escalation answer resolves it (e.g. "document as Blocked"); this is
the one case where the main thread edits the Test Plan file itself rather
than a dispatched role, because the escalation and its resolution both
happen in the main thread, not inside a subagent. Verifier still
independently re-confirms this row per its own dispatch instructions and
its result replaces the provisional value the same as any other row.

### Bug Report (one per confirmed defect, appended to `DEFECT-LOG.md`)

```markdown
# [Summary]

- Environment:
- Application version:
- Role:
- Classification: ApplicationDefect / SuspectedDefect / AutomationIssue / EnvironmentIssue / TestDataIssue / ExpectedBehaviour / NeedsBusinessReview
- Suggested severity:
- Reproducibility:
- Resolution status: Open / Fixed — pending retest / Retested — resolved / Retested — still failing / Won't fix

## Preconditions and test data

## Reproduction steps

1.

## Expected result

## Actual result

## Evidence

- Screenshots:
- Trace/video:
- Sanitized console/network evidence:
- Source reference (file:line), if a codebase connection was configured:
- Sensitive data masked or omitted:

## Related/duplicate issues and notes
```

Defect-Triage sets Resolution status to `Open` when writing a new entry
(stage 9). It only becomes `Fixed — pending retest` if the user says so at
Intake (Stage 1) for an existing entry — this skill has no way to observe a
code fix landing on its own, so this transition always comes from the user.
It becomes `Retested — resolved` or `Retested — still failing` only via an
actual `[retest]` round (Stage 1, Stage 9, Stage 10) — never set either of
these from anything short of an independently-verified retest. `Won't fix`
is likewise a user/business decision recorded here for reference, not
something this skill infers.

### Coverage Report row shape (`FLOWS-LOG.md` table)

```markdown
| Area | Discovered | Covered | Blocked | Deferred | Evidence |
| ---- | ---------: | ------: | ------: | -------: | -------- |
```

### Run Summary (`TEST-EXECUTION-REPORT-<round-id>.md`)

```markdown
# Test execution report — [module/topic], round [id]

- Project/environment/role:
- Round type: A / B / C
- Codebase connection: [path, or "not configured — Source-Verifier skipped"]
- Coverage closure result (separate from test pass/failure):
- Cases executed / passed / failed / blocked:
- Start/end/duration:
- Screens/controls/routes covered:
- Defects raised (with DEFECT-LOG.md references, incl. source file:line where Source-Verifier ran):
- Data-lineage entries added/reconfirmed this round (if B/C), noting which were source-code-confirmed vs. UI/API-observed only:
- Known limitations and recommended next action:
```

"Coverage closure result" states whether every row in this round's Test
Plan reached a final Status (Pass/Fail/Blocked) — a fact about
completeness, independent of whether those outcomes were themselves passes
or failures, e.g. "12/12 planned rows closed" or "2 of 12 rows still
Blocked pending UAT data." A row with Status `Fail` that has since had a
Bug Report written for it in `DEFECT-LOG.md` still counts as closed — it
reached a final Status and was root-caused; only a row still awaiting
retry, triage, or missing data stays open. Likewise, a row with Status
`Blocked` because it's destructive/irreversible with no disposable UAT
record available counts as closed once the user has confirmed stopping
there (per stage 5's escalation) — the Coverage Standard's requirement to
exercise delete/destructive actions doesn't override the global
instructions' rule against mutating real data with no disposable record;
it stays a permanent, legitimate exception, not an open item, unless a
disposable record later becomes available.

### Data Lineage row shape (`DATA-LINEAGE.md`)

```markdown
| Module.Screen.Field | Control type | API endpoint(s) observed | Source/config screen | First confirmed | Last reconfirmed | Verification method |
| -------------------- | ------------- | ------------------------- | --------------------- | ---------------- | ----------------- | -------------------- |
```

"Verification method" is `UI/API observation` when only Traceability
confirmed the row, or `source code (file:line)` when Source-Verifier also
cross-checked it against the actual implementation — always prefer
recording the stronger of the two when both ran. If Traceability could not
confirm a source at all, still add the row rather than omitting it: set
"Source/config screen" to `UNCONFIRMED — <what was checked and why it
didn't resolve>` and "Verification method" to `unconfirmed`. "First
confirmed" and "Last reconfirmed" are calendar dates in `YYYY-MM-DD`
format.

Each row is a single hop: `Source/config screen` names the immediate
source of `Module.Screen.Field`, nothing further upstream. A chain (the
source screen's own value is itself populated from a further screen) is
represented as a second row for that intermediate field, not as extra
columns on the first row — see Stage 6's instruction for when Traceability
adds that second row.

`DATA-LINEAGE.md` tracks where a value's source of truth lives, not
whether the app currently implements it correctly — a row's content
doesn't change just because the same field also turned up a defect
elsewhere in this round's pipeline. If Source-Verifier's dynamic-vs-hardcoded
check is what actually surfaced the defect, that's worth a short
cross-reference to the `DEFECT-LOG.md` entry, but the row's Source/config
screen and Verification method still describe the source, not the defect.

## Subagent Dispatch Rules (cross-cutting)

- All five dispatched roles — Executor, Traceability, Verifier,
  Source-Verifier, Defect-Triage — use `subagent_type: "general-purpose"`.
  This applies even where a stage's own dispatch instructions don't repeat
  it.
- Always foreground/blocking (`run_in_background: false`) — this pipeline
  is sequential; each stage's output gates the next, so nothing here should
  run unattended.
- Executor, Traceability, Verifier, and Defect-Triage all operate the same
  already-authenticated browser session established during Discovery
  (stage 3) — none of them attempts its own login or assumes a fresh
  unauthenticated session. Find and attach to that existing session (e.g.
  via `playwright-cli list`/`tab-list`, per `../user-manual-update/
  gotchas.md`) rather than launching a new browser instance. Source-Verifier
  is the only role that never touches the browser at all (see below).
- This rule covers the default single-role case. A row that structurally
  requires a second, different authenticated identity to complete (e.g. a
  maker-checker approval step where the app enforces that the submitter
  cannot also approve) is a genuinely ambiguous step this rule doesn't
  resolve on its own — Executor stops and reports back per its Stage 5
  escalation instruction rather than attempting a second login itself; the
  main thread asks the human to authenticate the second role in a separate
  browser context/tab, then hands that context's identifier back to the
  same dispatch to resume against. Label which step needs which role
  directly in the Scenario cell (e.g. "As Maker: submit. As Checker:
  approve.") since the Test Plan table has no separate role column.
- Verifier's independent re-check of such a row is subject to the same
  escalation the first time it needs the second identity — it is not
  expected to authenticate as a second user unassisted any more than
  Executor was.
- This holds across rounds within one working session too: if a second,
  unrelated round (different module, different topic) starts later in the
  same session, its Discovery (stage 3) navigates to the new module in the
  same already-authenticated browser session rather than relaunching or
  re-logging in — the session belongs to the human's login for the whole
  working session, not to any one round. A UI-level preference that's part
  of that session's mutable state — a language switcher is the clearest
  example — is not guaranteed to still be set the way an earlier stage left
  it by the time a later stage's dispatch runs. Any row whose Scenario or
  Preconditions names a specific language (per Stage 3's per-language branch
  rule) must have the dispatched role explicitly (re)select that language
  itself before acting, rather than trusting whatever the shared session
  currently happens to have set — silently inheriting the wrong language
  produces a false Pass or false Fail that looks like a normal result.
- This assumes a continuous working session; it does not extend across a
  genuine multi-day gap forced by a scheduled/external event a row's
  precondition depends on (see stages 5 and 7). When a stage resumes hours
  or days after the browser session was established, treat the old session
  as presumptively expired rather than assuming it survived — ask the human
  to re-authenticate before that stage's dispatch runs, rather than
  discovering the session is dead mid-dispatch. The round-id and every
  artifact filename stay the same across this gap (the round hasn't
  restarted, it's only paused); only the browser authentication is
  re-established.
- If the disposable record a prior stage created is no longer reachable or
  usable when a later stage resumes (auto-closed, archived, expired by the
  app's own lifecycle rules), treat that the same as any other unmet
  precondition — report it back rather than silently recreating or assuming,
  and let the user decide whether to recreate the prerequisite sequence
  fresh or document the row as Blocked.
- When two rounds targeting different modules run back-to-back in the same
  session against the same project, every stage still runs per round from
  Stage 0 onward (Stage 0's file checks, Stage 2's round-type question, and
  Stage 4's confirmation gate are never silently skipped for a later round
  just because an earlier round in the same session already did them) — but
  a recorded codebase-connection path from an earlier round is only reused
  as-is if it actually covers the new module; if the new module plausibly
  lives in a different repo, confirm this with the user rather than
  carrying the old path forward unchecked. `AUDIT-LOG.md` and `FLOWS-LOG.md`
  are shared across every round and module in the project (they are not
  per-module files) — lead each `AUDIT-LOG.md` entry and each `FLOWS-LOG.md`
  "Area" value with the module/topic it covers (e.g. "Lending —
  Collateral Coverage Ratio: ...", Area = `Lending.CollateralCoverageRatio`
  or an equally specific module-qualified label) so entries from different
  modules/rounds stay distinguishable without relying on chronological
  position alone.
- Every dispatched role is a `general-purpose` subagent and so has full
  tool access, including `Write` — it writes its own artifacts directly
  (network-capture log, `DATA-LINEAGE.md` rows, `DEFECT-LOG.md` entries,
  etc.) per its stage's instructions; the main thread does not need to
  transcribe a subagent's findings into these files on its behalf.
- Wherever a stage's dispatch instructions say a subagent "must include" or
  "is given" something (a test plan, a network-capture log, a
  `DATA-LINEAGE.md` row), deliver it either inline in the dispatch prompt
  text or as an exact file path plus explicit confirmation the subagent may
  read it — never assume a fresh subagent already knows where a file lives
  or what it contains.
- Never dispatch the same subagent instance to both do a piece of work and
  verify or retry that same piece of work. Each stage that re-checks
  anything gets a brand-new dispatch.
- Give each subagent only what its stage needs. Verifier in particular
  must never see Executor's or Traceability's claimed results — that's
  what makes its re-check worth anything.
- Source-Verifier only ever gets read access to the codebase (`Read`/
  `Grep`/`Glob`) — it never drives the browser and never needs the live
  session. Don't give it more access than that.
- Never skip Source-Verifier silently when a codebase connection exists —
  either it runs, or the report says explicitly why it didn't for this
  particular row (e.g. "no matching module found in the configured repo").

## Error Handling

- Never self-heal a failing case to a pass.
- Never click a destructive control merely to inspect it without a
  disposable UAT record — stop at the confirmation dialog, or use
  disposable data instead.
- Root-cause a blocked/no-data result via the actual network request/
  response before logging it as a defect — don't accept "no data" at face
  value.
- When a row uses an existing shared UAT record (not one created fresh this
  round) and its state doesn't match what the plan's steps or Executor's own
  actions account for, don't assume it's an application defect by default —
  a shared record can be modified by someone outside this round entirely
  (another tester, another session, in the same live UAT environment). Check
  the record's audit trail/last-modified-by field or history screen, if the
  app has one, for a change not attributable to this round's own actions
  before concluding the app is at fault. If an external modification is
  confirmed, that's environment contamination, not a finding about the
  application: note it plainly in `AUDIT-LOG.md` (it doesn't fit the
  gap-closed/correction/out-of-scope categories cleanly — record it as its
  own plain fact, e.g. "record X's status was changed by an unrelated
  session between steps 3 and 4; re-run against a clean state"), and re-run
  the affected row once the record is back to a known-good state (or against
  a fresh disposable record if one is available and the row's data-strategy
  allows it) rather than logging the contaminated observation as a defect.
- Resolve ambiguity before the Stage 4 confirmation gate, not mid-execution.
- When a blocker or gap is found, tell the user and ask whether to keep
  investigating or stop and document it as-is — never decide silently
  either way.
- If a dispatched subagent errors out, times out, or returns output that
  doesn't actually satisfy its stage's instructions, dispatch one fresh
  retry of the same role before escalating to the user — never advance to
  the next stage on a failed or unusable dispatch, and never have the
  orchestrating thread fill in the missing result itself.
