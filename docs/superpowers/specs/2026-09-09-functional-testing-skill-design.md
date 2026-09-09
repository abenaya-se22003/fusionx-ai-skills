# Design: `functional-testing` skill

Date: 2026-09-09
Status: Approved by user, pending write-up as implementation plan.

## Purpose

A new skill in this repo (`fusionx-ai-skills`), sibling to `user-manual-update`,
that performs full QA-style functional testing of the FusionX system UI —
not just click-through verification, but end-to-end traceability of where a
value or validation actually comes from (a cross-module API check, a
config/settings page driving a dropdown, etc.). Independent of the
`fusionx-test-agent-v0.1.1` tool, which is deliberately Read-Only Discovery
only in v0.1 — this skill drives Playwright directly, the same way
`user-manual-update` does, and is **not** subject to that tool's read-only
restriction. It performs full transaction lifecycles (create, edit, submit,
approve/reject, delete) with UAT test data where authorized.

## Why a skill, not a top-level Agent

Per `HANDOFF.md`'s Skill vs Agent table: this needs live human interaction
(manual login/MFA, test-plan confirmation before any action runs,
mid-task ambiguity Q&A, pauses before destructive/irreversible actions). That
rules out a top-level Agent. Executor / Traceability / Verifier / Defect-Triage
are dispatched as ad-hoc `Agent` tool calls (`general-purpose`, foreground,
blocking) from within the skill — the same pattern `user-manual-update` uses
for Gate A/B. No new files under `agents/` are needed.

## Source material to reuse (don't reinvent)

The `fusionx-test-agent-v0.1.1` repo already has vocabulary and templates
built for its own future (currently disabled) scenario/bug-triage modes.
Reuse these rather than inventing parallel formats:

- `templates/test-plan.md` — requirement-based test plan shape (scenario
  table with ID/Steps/Expected/Evidence/Status) → basis for this skill's
  per-round test plan.
- `templates/bug-report.md` — defect shape and classification taxonomy
  (`ApplicationDefect / SuspectedDefect / AutomationIssue / EnvironmentIssue /
  TestDataIssue / ExpectedBehaviour / NeedsBusinessReview`) → basis for
  `DEFECT-LOG.md` entries.
- `templates/coverage-report.md` — coverage table shape (Area/Discovered/
  Covered/Blocked/Deferred/Evidence) → basis for this skill's `FLOWS-LOG.md`
  updates.
- `templates/run-summary.md` — round-level summary shape → basis for the
  per-round `TEST-EXECUTION-REPORT-<round>.md`.
- `docs/evidence-and-bug-policy.md` — evidence minimization rules (mask/omit
  credentials, store minimum necessary) — carries over unchanged.
- `user-manual-update/gotchas.md` — FusionX UI/environment quirks (Ant Design
  virtualization, sticky-header click interception, slow-confirm screens,
  etc.) — cross-reference, don't duplicate.
- Global `~/.claude/CLAUDE.md` Playwright Full-Coverage Instructions — already
  govern login/session handling, coverage standard, dropdown/search/
  transaction testing, evidence capture, defect recording, and the
  AUDIT-LOG.md/FLOWS-LOG.md convention. This skill inherits all of it; SKILL.md
  should point to it, not restate it.

## Round types (user-selected, Stage 2)

Discovery always flags candidate config/cross-module controls cheaply from
snapshots (dropdowns, fields validated against another module, derived/
calculated values) regardless of round type — this costs nothing extra and
feeds whichever type is chosen.

- **A. Functional only** — Executor, Verifier, Defect-Triage. No Traceability
  subagent dispatched.
- **B. Functional + full traceability** — adds Traceability subagent,
  processing every action's captured network calls.
- **C. Functional + targeted traceability** — adds Traceability subagent,
  processing only the flagged candidates from Discovery.

Executor, Verifier, and Defect-Triage keep the same role/prompt shape across
all three types — only whether Traceability runs, and its input scope,
changes. This is the reuse model requested: one Traceability role, invoked
conditionally with a different input list, not per-type variants.

## Pipeline (per round)

1. **Intake** — Jira ticket, requirement doc, test-case list, or any source
   document. If none given, Q&A with the user to clarify scope before
   anything else.
2. **Round-type selection** — user picks A/B/C (see above) before a plan is
   drafted, since it changes what Discovery needs to flag for and what
   Executor needs to capture.
3. **Discovery & Planning** (main thread, human-authenticated browser) —
   navigate target screens, take snapshots, enumerate pathways/controls per
   the Coverage Standard, flag config/cross-module candidates, cross-reference
   the intake source, draft the round's test plan using the
   `templates/test-plan.md` shape. Check `DATA-LINEAGE.md` first for any
   candidate already mapped — reconfirm rather than rediscover.
4. **Confirmation gate** — present the plan to the user; do not proceed until
   explicitly approved. Revise and re-present on pushback; never narrow or
   proceed silently.
5. **Executor** (fresh subagent, foreground) — drives the confirmed plan
   against the same authenticated session. Performs full transaction
   lifecycles (create/edit/submit/approve/reject/delete) with UAT data where
   authorized, not read-only inspection. Captures network requests/responses
   per action as evidence (correlated to the action that triggered them).
   Records evidence-backed results per case, not bare pass/fail. Pauses back
   to the user for destructive/irreversible actions with no disposable UAT
   record, or genuine ambiguity — does not silently decide either way.
6. **Traceability** (fresh subagent, dispatched per round type, skipped
   entirely for type A) — analyzes Executor's captured network logs for its
   input list (all actions for B, flagged candidates for C), navigates to the
   config/settings screen behind each dynamic value to confirm the actual
   source, and writes/updates `DATA-LINEAGE.md`. If a value's source can't be
   traced, records that as a gap, not a silent pass.
7. **Verifier** (fresh subagent, no shared context with Executor or
   Traceability) — independently re-derives evidence for every case in the
   round: full re-check, not a sample, and re-derives any lineage claim
   Traceability made too. This is the anti-self-certification gate the
   handoff doc requires — a fresh subagent proves nothing shares Executor's
   blind spots.
8. **Defect-Triage** (fresh subagent) — for every Verifier-confirmed
   functional fail/block or lineage gap: root-causes via network/response
   inspection (not just UI symptoms), retries ≥2 input combinations before
   calling it reproducible, classifies using the existing bug-report
   taxonomy, writes a Jira-ready entry to `DEFECT-LOG.md`.
9. **Reporting** (main thread) — compiles the round's
   `TEST-EXECUTION-REPORT-<round>.md` (clean, no process narration), updates
   `FLOWS-LOG.md`'s coverage table, appends an `AUDIT-LOG.md` entry (the
   honest "what was checked, what was found, what was corrected" narrative —
   this is where process history lives, never in the shipped report).

## Files

**In this skill repo** (`fusionx-ai-skills`):
- `skills/functional-testing/SKILL.md` — orchestration, read-first list,
  workflow, subagent dispatch instructions.
- `skills/functional-testing/gotchas.md` — anything FusionX-specific learned
  building/testing this skill that isn't already in
  `user-manual-update/gotchas.md` or the global instructions. Cross-reference
  the former rather than duplicate.

No new templates authored here — the four templates already in
`fusionx-test-agent-v0.1.1/templates/` are referenced/adapted in place.

**In the target UAT project root** (wherever the skill is invoked from, per
the global CLAUDE.md convention — not this skill repo):
- `AUDIT-LOG.md`, `FLOWS-LOG.md` — already mandated by global instructions for
  any multi-session verification work; this skill inherits them.
- `FUNCTIONAL-TEST-PLAN-<topic>.md` — per round, the proposed scope, awaiting/
  recording confirmation.
- `DEFECT-LOG.md` — append-only, Jira-ready, across rounds.
- `TEST-EXECUTION-REPORT-<round-id>.md` — one clean report per completed
  round.
- `DATA-LINEAGE.md` — cumulative, updated in place across rounds, one entry
  per field/control:
  `Module.Screen.Field | Control type | API endpoint(s) observed | Source/config screen | First confirmed | Last reconfirmed | Verification method`

## Error handling

- Never self-heal a failing case to a pass (matches
  `fusionx-test-agent-v0.1.1/AGENTS.md`'s own rule, carried over here).
- Never click a destructive control just to inspect it without a disposable
  UAT record — stop at the confirmation dialog, or use disposable data.
- Blocked/no-data results get root-caused via network inspection before being
  logged as a defect, not accepted at face value.
- Ambiguity is resolved before plan confirmation, not mid-execution.
- A blocker/gap is reported to the user with a choice to keep investigating
  or stop and document as-is — never decided silently.

## Skill-authoring process (how this gets built)

1. Invoke `superpowers:writing-skills` before writing SKILL.md.
2. Gather source material: this spec, the templates and docs listed above,
   `user-manual-update/gotchas.md`, global CLAUDE.md instructions.
3. Test with at least one fresh, context-free `general-purpose` subagent
   round (foreground, blocking) against a concrete hypothetical scenario
   before calling the skill done — per the handoff's proven method, every
   round of this in the prior session found a real gap.
4. Commit to `fusionx-ai-skills` (this repo), scoped the same way
   `user-manual-update` was (`.claude`-only concerns, no project working
   data).
5. Update `HANDOFF.md` afterward with what this build learned, for the next
   skill/agent after this one.

## Explicitly out of scope for this spec

- Any change to the `fusionx-test-agent-v0.1.1` codebase or its
  Planned-Disabled modes (`fusionx-scenario`, `fusionx-api`, etc.) — those
  remain gated behind that project's own v0.1 restrictions and are a separate
  decision for that project's owner.
- Performance/load/stress testing (`fusionx-performance` territory) — not
  requested, not covered here.
