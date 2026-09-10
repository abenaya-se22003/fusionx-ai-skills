# FusionX AI Skills

Claude Code skills that support FusionX business-analysis work — user
manuals, functional testing, requirement documentation, and more. Each
skill orchestrates a human-in-the-loop workflow that drives Playwright
against a live FusionX UAT session, with independent verification built in
rather than self-certified results.

This repo is scoped to `.claude/` skills and agents only — not the
surrounding project's UAT screenshots, manuals, or scripts.

## Skills

- **[`user-manual-update`](skills/user-manual-update/)** — Turns a Jira
  ticket or request into a delivered FusionX module user manual (Accounts,
  Cash, Collateral, Lending, SCO, Term Deposit, or a new module): live UAT
  walkthrough, coverage validation gate, docx build, content/formatting
  validation gate, delivery.
- **[`functional-testing`](skills/functional-testing/)** — Full QA-style
  functional testing of a FusionX module end to end: transaction-lifecycle
  testing (create/edit/submit/approve/reject/delete, not read-only),
  data-lineage tracing (where a validated value or dropdown option actually
  comes from), and optional source-code cross-verification. Runs a 5-role
  subagent pipeline (Executor, Traceability, Verifier, Source-Verifier,
  Defect-Triage) per round, gated by an upfront round-type choice.

More skills are planned as other BA-support activities come up
(requirement-gathering support, etc.).

## Build history and lessons

See [`HANDOFF.md`](HANDOFF.md) for the full build history of each skill —
what was learned, what patterns proved worth repeating (fresh-subagent
validation, independent verification gates, reusing existing templates
instead of inventing new ones), and open follow-ups for whoever builds the
next one.
