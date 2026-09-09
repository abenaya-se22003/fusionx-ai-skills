# Functional Testing Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `functional-testing` skill to the `fusionx-ai-skills` repo that performs full QA-style functional testing of the FusionX system UI — transaction lifecycle testing (not read-only) plus data-lineage traceability (UI value → API call → config/source screen) and, when a codebase connection is configured, source-code cross-verification — orchestrated as a skill that dispatches fresh, single-purpose subagents (Executor, Traceability, Verifier, Source-Verifier, Defect-Triage) per round, and validate it with fresh-subagent test rounds before shipping.

**Architecture:** One skill (`skills/functional-testing/SKILL.md` + `gotchas.md`) drives Playwright directly against a human-authenticated FusionX session. Per round: Intake (incl. codebase-availability check) → round-type select (A/B/C) → Discovery/Plan → user confirmation gate → Executor subagent → Traceability subagent (skipped for type A) → Verifier subagent (fresh, no shared context) → Source-Verifier subagent (skipped when no codebase is configured; cross-checks confirmed lineage rows and any rejected case against the actual implementation) → Defect-Triage subagent (only on confirmed fails, consumes Source-Verifier's root-cause when available) → Reporting. All five subagent roles are ad-hoc `Agent` tool dispatches (`general-purpose`, foreground/blocking) — no persistent `.claude/agents/*.md` files. Existing `fusionx-test-agent-v0.1.1` templates (test-plan, bug-report, coverage-report, run-summary) are reused, inlined into SKILL.md so the skill is self-contained even when that repo isn't checked out alongside it.

**Tech Stack:** Markdown skill authoring (SKILL.md + gotchas.md), Playwright (driven per the global Playwright Full-Coverage Instructions already in the user's `~/.claude/CLAUDE.md`), git.

## Global Constraints

- Skill lives at `skills/functional-testing/` in the `fusionx-ai-skills` repo (local checkout: `D:\Work\LOLC\Automation Projects\User Manuals\.claude`), sibling to `skills/user-manual-update/`.
- This is a **skill**, not a top-level Agent. No files under `agents/`.
- Executor/Traceability/Verifier/Source-Verifier/Defect-Triage are dispatched via the `Agent` tool, `subagent_type: "general-purpose"`, `run_in_background: false` (foreground/blocking) — never a persistent custom agent definition.
- Executor performs **full transaction lifecycles** — create, edit, submit, approve, reject, delete — with disposable UAT data where authorized. Not read-only. This must be stated explicitly in SKILL.md so it is never misread as inheriting `fusionx-test-agent-v0.1.1`'s read-only restriction (that restriction belongs to a different, unrelated codebase).
- Verifier must be dispatched with **zero shared context** with Executor/Traceability and must re-derive every row's result independently — full re-check, never a sample.
- Defect classification is fixed to the existing taxonomy from `fusionx-test-agent-v0.1.1/templates/bug-report.md`: `ApplicationDefect / SuspectedDefect / AutomationIssue / EnvironmentIssue / TestDataIssue / ExpectedBehaviour / NeedsBusinessReview`. Do not invent a new taxonomy.
- Round types: **A** (functional only, no Traceability dispatch), **B** (functional + full traceability, every action), **C** (functional + targeted traceability, flagged candidates only). Same Traceability role/prompt shape for B and C — only the input list differs.
- **Source-Verifier** is a 5th subagent role, orthogonal to round type A/B/C: it runs whenever the target project has a configured codebase path, regardless of which round type was chosen, and is skipped (with an explicit note, never silently) when no codebase is configured. Ask at Intake whether a codebase connection exists; record the answer in the round's test plan header. Same role/prompt shape whether its input is a confirmed lineage row or a Verifier-rejected case — only the input differs, same reuse pattern as Traceability.
- Working files (`AUDIT-LOG.md`, `FLOWS-LOG.md`, `DEFECT-LOG.md`, `DATA-LINEAGE.md`, `FUNCTIONAL-TEST-PLAN-<topic>.md`, `TEST-EXECUTION-REPORT-<round-id>.md`) are created at the **target project's root**, never inside the `fusionx-ai-skills` skill repo.
- `DATA-LINEAGE.md` is cumulative and updated in place across rounds — check it before rediscovering a candidate's source.
- Never self-heal a failing case to a pass. Never click a destructive control to inspect it without a disposable record. Root-cause blocked/no-data results via network inspection before logging as a defect. Resolve ambiguity before plan confirmation, not mid-execution.
- Follow the global `~/.claude/CLAUDE.md` Playwright Full-Coverage Instructions and AUDIT-LOG/FLOWS-LOG conventions by reference — do not restate them in SKILL.md.
- Out of scope for this plan: any change to the `fusionx-test-agent-v0.1.1` codebase or its Planned-Disabled modes (`fusionx-scenario`, `fusionx-api`, etc.), and performance/load/stress testing (`fusionx-performance` territory). Neither is touched by any task below.

---

Whoever executes this plan (subagent-driven-development or executing-plans)
must invoke `superpowers:writing-skills` before Task 1's Step 1 — it governs
the TDD-style cycle for skill authoring (write, test with a fresh subagent,
fix, repeat) that Task 3 below implements. Do not skip straight to writing
`SKILL.md` without it.

## Task 1: Write `SKILL.md`

**Files:**
- Create: `skills/functional-testing/SKILL.md`

**Interfaces:**
- Produces: the skill's frontmatter `name: functional-testing` and `description:` — this is what later tasks' fresh-subagent test rounds will load and follow.
- Consumes: nothing (first task).

- [ ] **Step 1: Write the file**

```markdown
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
4. The Templates section below. If the `fusionx-test-agent-v0.1.1` repo
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
them now with a minimal header (title + "no entries yet") rather than
waiting until the Reporting stage — an empty file that exists is easier to
append to correctly than one whose absence gets missed later.

Also ask (or check a prior round's plan header for the answer already on
record): is a codebase connection configured for this target — a local
path or checkout the automation can actually read? If yes, record the path
in this round's plan header and the Source-Verifier stage (8) runs. If no,
record "Source-Verifier: not available — no codebase connection configured"
in the plan header and skip stage 8 later — note the skip explicitly in the
round's report too, never silently.

### 1. Intake

Accept any of: a Jira ticket, a requirement/spec document, a test-case list,
or any other source document. If none is given, or the request is ad hoc
("test the X screen"), ask the user directly what needs covering before
doing anything else — module, screens/flows, specific business rules, and
any known risk areas. Don't guess scope from a screen name.

If the source names a **specific change** (a ticket describing one new
field, one modified validation rule, etc.), scope Discovery's first pass to
exactly that change and its immediate dependents, then expand to the full
Coverage Standard for the surrounding screen only if time/scope allows.
Don't spend the first pass spread evenly across an entire module when the
source document already tells you where the risk is concentrated.

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
  module, or calculated rather than directly entered. This costs nothing
  extra during a snapshot pass and feeds whichever round type was chosen.
- Check `DATA-LINEAGE.md` for each flagged candidate. If already mapped,
  mark it "reconfirm" rather than "discover" in the plan — don't rediscover
  a dependency already on record.
- Draft the round's plan using the Test Plan template below. Include the
  scenario table, safety authorization, and data strategy (which records
  are newly created for this round vs. existing UAT records being reused —
  see the global instructions' Transaction Testing section for why both
  matter).
- Explicitly flag any planned step that is destructive/irreversible with no
  disposable UAT record available — these become pause points for the
  Executor, not silent skips.

### 4. Confirmation gate

Present the drafted plan file to the user. Do not proceed until they
explicitly approve it. If they push back, revise and re-present — never
narrow scope silently and continue as if it were approved.

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
- This explicit instruction: "Record raw network requests/responses for
  every action you perform, tagged with the action that triggered them, in
  a network-capture log file. Do not summarize them away — Traceability and
  Verifier need the raw entries."
- This explicit instruction: "If you reach a destructive/irreversible
  action with no disposable UAT record available, or a genuinely ambiguous
  step the plan doesn't resolve, stop and report back rather than deciding
  either way yourself."

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
  Update `DATA-LINEAGE.md` at the project root: add a new row, or refresh
  the 'Last reconfirmed' date on an existing one. If you cannot confirm a
  source for an entry, record that as a gap in the same file — do not
  silently drop it or mark it resolved."

### 7. Verifier dispatch

Dispatch one fresh `Agent` tool call with **no shared context** with
Executor or Traceability — it must not see their claimed results, only:

- The confirmed test plan (every row), exactly as given to Executor.
- Which round type was selected (so it knows whether to also re-check
  `DATA-LINEAGE.md` rows touched this round).
- This instruction: "Independently re-derive the actual result for every
  row yourself — re-navigate, re-check the live state, re-read the actual
  screen or data. Do not read or trust any prior claimed result. This is a
  full re-check of every row, never a sample. If this round included
  traceability, independently re-confirm every `DATA-LINEAGE.md` row it
  touched the same way — re-navigate to the claimed source screen yourself.
  Return CONFIRMED or REJECTED per row, each with its own fresh evidence."

If Verifier's evidence contradicts Executor's or Traceability's claim, the
Verifier's independently-derived result is what's recorded — flag the
discrepancy itself as a finding too (it usually indicates the earlier
subagent reported an unverified guess).

### 8. Source-Verifier dispatch

Skip entirely if Intake (stage 0) recorded no codebase connection — note
the skip in the round's report at stage 10, don't just drop it quietly.

If a codebase is configured, dispatch one fresh `Agent` tool call (with
`Read`/`Grep`/`Glob` access to the configured codebase path — it doesn't
need browser access, it never touches the live app) for **each** of these
input sets that has entries this round:

- Every `DATA-LINEAGE.md` row Traceability added or reconfirmed this round
  (round types B/C only) — prompt: "Given this claimed data source (module,
  screen, API endpoint, and the config/settings screen Traceability
  identified), find the actual code that implements this — the validation
  rule, the query, or the config lookup. Confirm whether the code's real
  behavior matches what Traceability observed from the UI/API alone (for
  example: a dropdown that looks config-driven from the API response but
  is actually hardcoded in code, or a threshold that looks configurable
  but has a hardcoded override). Report file/line references. If the code
  contradicts the UI-observed behavior, say so explicitly — that is a
  finding, not a detail to smooth over."
- Every Verifier-REJECTED row — prompt: "Given this failing case (what was
  expected, what was actually observed), find the code path responsible
  and identify the precise cause — not just 'it fails' but the actual
  faulty condition, missing check, or incorrect value in the code. Report
  file/line references. If you cannot locate the responsible code, say so
  plainly rather than guessing."

Source-Verifier's output feeds into stage 9 (Defect-Triage, for rejected
rows) and stage 10 (Reporting, for `DATA-LINEAGE.md`'s "Verification
method" column, which should say "source code" rather than only "UI/API
observation" wherever Source-Verifier ran).

### 9. Defect-Triage dispatch

Only if Verifier returned any REJECTED row or unconfirmed lineage gap.
Dispatch one fresh `Agent` tool call. The prompt must include:

- Every REJECTED row and lineage gap, with Verifier's evidence.
- Source-Verifier's file/line root-cause findings for that row, if stage 8
  ran and produced one — include it verbatim so Defect-Triage doesn't have
  to re-derive what's already been found.
- This instruction: "Before treating anything as a reproducible defect,
  retry it with at least one different input combination or a fresh
  session/login. Root-cause it using the actual network request/response
  and, if provided, the Source-Verifier finding — not just what the UI
  shows. Classify each confirmed defect using exactly one of:
  ApplicationDefect, SuspectedDefect, AutomationIssue, EnvironmentIssue,
  TestDataIssue, ExpectedBehaviour, NeedsBusinessReview. Write one Bug
  Report entry (see template below) per confirmed defect into
  `DEFECT-LOG.md` at the project root, appending — never overwrite prior
  entries."

### 10. Reporting (main thread)

- Compile `TEST-EXECUTION-REPORT-<round-id>.md` using the Run Summary
  template below — the clean, user-facing deliverable. No process
  narration (no "we initially thought X" — that belongs in AUDIT-LOG.md).
  State plainly whether Source-Verifier ran this round or was skipped for
  lack of a codebase connection — never leave that ambiguous.
- Update `FLOWS-LOG.md`'s coverage table using the Coverage Report template
  shape below.
- Append one `AUDIT-LOG.md` entry: what was checked this round, what was
  found, with concrete evidence references (file/screenshot names, not just
  "confirmed"). State the current, correct picture as plain fact.

## Templates

### Test Plan (drafted at Stage 3, confirmed at Stage 4)

```markdown
# Functional test plan — [module/topic]

- Requirement/source:
- Environment/version:
- Roles/browsers:
- Scope and exclusions:
- Round type: A / B / C
- Safety authorization:
- Data strategy: (new records created this round vs. existing UAT records reused)
- Destructive/irreversible steps flagged: (list, or "none")

| ID  | Scenario | Preconditions | Steps | Expected | Evidence | Status |
| --- | -------- | ------------- | ----- | -------- | -------- | ------ |

## Risks, dependencies, deferred work, and exit criteria
```

### Bug Report (one per confirmed defect, appended to `DEFECT-LOG.md`)

```markdown
# [Summary]

- Environment:
- Application version:
- Role:
- Classification: ApplicationDefect / SuspectedDefect / AutomationIssue / EnvironmentIssue / TestDataIssue / ExpectedBehaviour / NeedsBusinessReview
- Suggested severity:
- Reproducibility:

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

### Data Lineage row shape (`DATA-LINEAGE.md`)

```markdown
| Module.Screen.Field | Control type | API endpoint(s) observed | Source/config screen | First confirmed | Last reconfirmed | Verification method |
| -------------------- | ------------- | ------------------------- | --------------------- | ---------------- | ----------------- | -------------------- |
```

"Verification method" is `UI/API observation` when only Traceability
confirmed the row, or `source code (file:line)` when Source-Verifier also
cross-checked it against the actual implementation — always prefer
recording the stronger of the two when both ran.

## Subagent Dispatch Rules (cross-cutting)

- Always foreground/blocking (`run_in_background: false`) — this pipeline
  is sequential; each stage's output gates the next, so nothing here should
  run unattended.
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
- Resolve ambiguity before the Stage 4 confirmation gate, not mid-execution.
- When a blocker or gap is found, tell the user and ask whether to keep
  investigating or stop and document it as-is — never decide silently
  either way.
```

- [ ] **Step 2: Verify frontmatter and cross-references**

Run:
```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
sed -n '1,4p' skills/functional-testing/SKILL.md
test -f skills/user-manual-update/gotchas.md && echo "cross-ref OK: user-manual-update/gotchas.md exists"
```
Expected: frontmatter shows `name: functional-testing` and a `description:`
line; the cross-ref check prints `cross-ref OK...`. `gotchas.md` for this
skill doesn't exist yet — that's Task 2, don't treat its absence as a
failure here.

- [ ] **Step 3: Commit**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
git add skills/functional-testing/SKILL.md
git commit -m "Add functional-testing SKILL.md"
```

---

## Task 2: Write `gotchas.md`

**Files:**
- Create: `skills/functional-testing/gotchas.md`

**Interfaces:**
- Consumes: nothing new — references `../user-manual-update/gotchas.md` by
  relative path (already exists) and the round-type/stage names from
  `SKILL.md` (Task 1): "Discovery", "Executor", "Traceability", "Verifier".
- Produces: nothing consumed by later tasks directly — read by whoever runs
  the skill, and by the fresh-subagent validation rounds (Task 3).

- [ ] **Step 1: Write the file**

```markdown
# Functional Testing — Gotchas

Operational lessons specific to this skill. FusionX UI/environment quirks
that apply to any Playwright walkthrough of this system (Ant Design
virtualized dropdowns, sticky-header click interception, slow-confirm
screens with no progress indicator) are already documented in
`../user-manual-update/gotchas.md` — read that first, this file doesn't
repeat it.

## Selector drift after a UI release

If a FusionX release changes a screen's markup, both a `DATA-LINEAGE.md`
row's remembered path and a plan step's expected selector can go stale in
the same way. When Executor, Traceability, or Verifier can't find an
element that a prior round successfully located:

- Don't conclude the feature was removed. Treat it as "possibly moved" and
  re-derive it live (search the current screen, don't assume the old
  snapshot is still accurate).
- Record what actually happened in `AUDIT-LOG.md` either way — "element
  moved from X to Y after release Z" is exactly the kind of correction that
  log exists for, and it prevents the next round from repeating the same
  confused search.
- Don't silently update `DATA-LINEAGE.md`'s row without noting the change —
  a "Last reconfirmed" bump should reflect that the source was re-verified,
  not that the row was blindly carried forward.

## Diff/risk-aware scoping in practice

When a ticket names one specific field or rule change, do a first pass
narrowly on exactly that change and its immediate dependents, and let that
pass reach completion on its own. Only start the broader full-screen
Coverage Standard pass afterward, as a separate round if time allows. Don't
block the narrow pass's completion on the broader pass also finishing —
they're allowed to be reported as two separate rounds, and the narrow one
being done is real progress even if the broad one isn't started yet.

## Network capture stays action-correlated

When Executor records raw network requests/responses, tag each captured
request with the specific action that triggered it (e.g. "clicked Submit
on Collateral > Add Charge") rather than dumping one undifferentiated log
for the whole session. Traceability and Verifier both depend on being able
to find "the request(s) this one action caused" without re-deriving that
mapping themselves — an uncorrelated dump pushes work downstream that
Executor was already in the best position to do at capture time.
```

- [ ] **Step 2: Verify the cross-reference resolves**

Run:
```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude/skills/functional-testing"
test -f ../user-manual-update/gotchas.md && echo "relative path OK"
```
Expected: prints `relative path OK`.

- [ ] **Step 3: Commit**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
git add skills/functional-testing/gotchas.md
git commit -m "Add functional-testing gotchas.md"
```

---

## Task 3: Fresh-subagent validation round(s)

This is this domain's equivalent of a test cycle: a context-free
`general-purpose` subagent is the "test" that the skill files must pass.
Per the design spec, at least one round is required; repeat with a new
fresh subagent after every fix until a round surfaces zero new gaps
(the prior session's experience: every one of 3 rounds found a real gap,
so budget for more than one).

**Files:**
- Modify: `skills/functional-testing/SKILL.md` and/or `gotchas.md` (as
  gaps are found)
- No new files unless a gap requires one (e.g. a missing template shape)

**Interfaces:**
- Consumes: the complete `SKILL.md` (Task 1) and `gotchas.md` (Task 2).
- Produces: nothing new — this task only hardens the files already
  produced by Tasks 1–2.

- [ ] **Step 1: Dispatch round 1**

Use the `Agent` tool, foreground (`run_in_background: false`),
`subagent_type: "general-purpose"`, with a prompt equivalent to:

"You have no knowledge of any prior conversation. Read
`D:\Work\LOLC\Automation Projects\User Manuals\.claude\skills\functional-testing\SKILL.md`
and its `gotchas.md`, plus `../user-manual-update/gotchas.md` that it
references. Do not read anything else about this project. Here is a
hypothetical scenario: a Jira ticket says 'Lending module: new field
Collateral Coverage Ratio, must reject values below 1.2, the minimum
threshold is configurable in Common Module > Settings > Risk Parameters.'
Walk through exactly what this skill tells you to do, stage by stage, from
Intake through Reporting, as if you were actually executing it. At each
stage, note anything the skill file fails to tell you that you'd need to
know to actually proceed — an undefined term, a missing decision rule, a
contradiction between two stages, a template field you wouldn't know how
to fill in, or an instruction that assumes state (like a file or session)
that might not exist yet. Report every such gap plainly; don't paper over
ambiguity by guessing what was probably intended."

- [ ] **Step 2: Apply fixes for every gap the subagent found**

For each gap reported, edit `SKILL.md` or `gotchas.md` directly to close
it — add the missing decision rule, resolve the contradiction, define the
term, or state the missing assumption. Don't defer any of them.

- [ ] **Step 3: Commit round 1 fixes**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
git add skills/functional-testing/SKILL.md skills/functional-testing/gotchas.md
git commit -m "Fix gaps found in functional-testing validation round 1"
```

- [ ] **Step 4: Dispatch round 2 with a different hypothetical scenario**

Same setup as Step 1, but use a scenario exercising the traceability path
specifically: "A Lending module dropdown for 'Product Category' — you
suspect its options come from a configuration screen elsewhere in the
system. Round type B was selected. Walk through Discovery flagging this
candidate, Executor capturing the network calls, Traceability confirming
the source, and Verifier independently re-confirming it. Report every gap
the same way as before."

- [ ] **Step 5: Apply fixes, then repeat Steps 4–5 with a new scenario each time**

Keep dispatching fresh subagents with new hypothetical scenarios and fixing
what each one finds, until one full round reports zero new gaps. Vary:
round type; whether a destructive/irreversible step with no disposable
record appears; whether `DATA-LINEAGE.md` already has a matching row; and
**at least one round with a codebase connection configured** ("assume the
target project has a codebase checked out at `./repo`, walk through stages
8 and 9 as if Verifier had just rejected a case") and **at least one round
with none configured** ("no codebase connection exists for this target —
confirm the skill tells you to skip stage 8 and say so explicitly rather
than silently omitting it"). Commit after each round's fixes, same message
pattern as Step 3 with the round number incremented.

- [ ] **Step 6: Final commit once a round finds zero gaps**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
git add -A
git commit -m "functional-testing skill passes fresh-subagent validation" --allow-empty
```

---

## Task 4: Update `HANDOFF.md`

**Files:**
- Modify: `HANDOFF.md` (repo root)

**Interfaces:**
- Consumes: the final state of `SKILL.md`/`gotchas.md` and how many
  validation rounds Task 3 actually took.
- Produces: nothing consumed by a later task in this plan — this is the
  last task.

- [ ] **Step 1: Read the current file**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
cat HANDOFF.md
```

- [ ] **Step 2: Add a new section above "Where the deeper history lives"**

Insert this section (fill in the actual round count from Task 3 and any
gap that was genuinely notable, replacing the bracketed notes):

```markdown
## `functional-testing` skill (built after `user-manual-update`)

- `skills/functional-testing/SKILL.md` + `gotchas.md` — full QA-style
  functional testing of the live FusionX UI: transaction-lifecycle testing
  (create/edit/submit/approve/reject/delete, not read-only) plus
  data-lineage traceability (UI value → API call → config/source screen),
  via a 5-role subagent pipeline (Executor, Traceability, Verifier,
  Source-Verifier, Defect-Triage) dispatched per round, gated by an upfront
  round-type choice (A: functional only, B: full traceability, C: targeted
  traceability) and, independently, by whether a codebase connection is
  configured (Source-Verifier only — cross-checks confirmed UI/API
  behavior against the actual implementation, degrades to an explicit skip
  note when no codebase is available).
- Confirms the `user-manual-update` handoff's core lesson again: fresh-
  subagent validation with a hypothetical scenario found real gaps every
  round it ran — [N] rounds this time, closing [one-line summary of the
  most significant gap found].
- New pattern this skill adds: a single subagent role can be reused across
  multiple "modes" (round types A/B/C here) by keeping the role's prompt
  shape fixed and only varying its input scope — avoids needing per-type
  subagent variants.
- Reused `fusionx-test-agent-v0.1.1`'s own templates (`test-plan.md`,
  `bug-report.md`, `coverage-report.md`, `run-summary.md`) and defect
  taxonomy instead of inventing new ones — that tool already had these
  worked out for its own (currently disabled) scenario/bug-triage modes.
```

- [ ] **Step 3: Commit**

```bash
cd "D:/Work/LOLC/Automation Projects/User Manuals/.claude"
git add HANDOFF.md
git commit -m "Update HANDOFF.md with functional-testing skill lessons"
```
