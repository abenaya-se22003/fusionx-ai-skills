# FusionX AI Skills

Claude Code skills that support FusionX business-analysis work — user
manuals, functional testing, requirement documentation, and more. Each
skill orchestrates a human-in-the-loop workflow that drives Playwright
against a live FusionX UAT session, with independent verification built in
rather than self-certified results.

This repo is scoped to `.claude/` skills and agents only — not the
surrounding project's UAT screenshots, manuals, or scripts.

## Install

No cloning needed — either of these works:

**[`npx skills`](https://github.com/vercel-labs/skills)** (Claude Code, Cursor, Codex, Gemini CLI, and other Agent Skills Standard tools):

```bash
npx skills add r4ge-quit/fusionx-ai-skills
```

**Claude Code's native plugin system:**

```
/plugin marketplace add r4ge-quit/fusionx-ai-skills
/plugin install fusionx-ai-skills@fusionx-ai-skills
```

Skills are auto-invoked by description either way. Plugin install also
namespaces them as `/fusionx-ai-skills:functional-testing` and
`/fusionx-ai-skills:user-manual-update`.

## Dependencies (install before first use)

Neither `npx skills add` nor the native plugin installer installs these —
they're external tools the skills drive, not files inside this repo. Install
them yourself once per machine before running either skill.

**Both skills** — a live browser session with network-request capture:

```bash
npm install -g @playwright/cli
```

Confirm it's reachable with `playwright-cli list`. (A Playwright MCP server
with equivalent navigate/click/snapshot/network-capture tools works too, if
that's what the project has configured instead.)

**`user-manual-update` only** — its `scripts/` build the manual `.docx` and
export/QC it, and require:

- Python 3, plus:
  ```bash
  pip install python-docx pywin32
  ```
- A real, licensed Microsoft Word desktop install (Windows). `to_pdf_export.py`
  and `qc_audit.py`'s Word-open check drive real Word over COM automation —
  python-docx alone cannot produce a file guaranteed to actually open in Word
  (see `SKILL.md`'s Hard Rules).

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
