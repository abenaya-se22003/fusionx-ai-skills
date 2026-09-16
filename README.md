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
namespaces them as `/fusionx-ai-skills:functional-testing`,
`/fusionx-ai-skills:user-manual-update`, and `/fusionx-ai-skills:fusionx-urs`.

## Update

If you installed the skills with `npx skills`, **do not reinstall them when
the repo changes**. Pull the latest versions with:

```bash
npx skills update
```

This updates the installed skills that have changed. The browser-session
contract is packaged inside each browser-dependent skill, so it is updated
alongside the skill itself.

For contributors changing the canonical shared browser contract, run:

```bash
python scripts/sync-shared.py
```

Use `--check` in CI or before committing to detect drift:

```bash
python scripts/sync-shared.py --check
```

## Dependencies (install before first use)

Neither `npx skills add` nor the native plugin installer installs these —
they're external tools the skills drive, not files inside this repo. Install
all of them once per machine, up front, regardless of which skill you end up
running:

- Node.js (18+) — needed to run `npx skills add` itself and to install
  `playwright-cli` below. The URS generator also requires its pinned local
  `docx` package; after installing the skill, run:
  ```powershell
  npm --prefix <installed-skill-path>/generator ci
  ```
  ```powershell
  winget install OpenJS.NodeJS.LTS
  ```
  (macOS/Linux: install from [nodejs.org](https://nodejs.org) or your usual
  version manager instead.)
- A live browser session with network-request capture:
  ```bash
  npm install -g @playwright/cli
  ```
  Confirm it's reachable with `playwright-cli list`. Whenever a skill uses
  browser automation, it requires this CLI because its session reuse,
  tracing, and evidence instructions use named-session and network-capture
  behavior.
- Python 3, plus:
  ```bash
  pip install python-docx pywin32 PyMuPDF
  ```
- A real, licensed Microsoft Word desktop install (Windows). `to_pdf_export.py`
  and `qc_audit.py`'s Word-open check drive real Word over COM automation —
  python-docx alone cannot produce a file guaranteed to actually open in Word
  (see `user-manual-update/SKILL.md`'s Hard Rules). `fusionx-urs`'s own
  `get_page_numbers.ps1` and Pass-2 visual-verification step rely on the same
  Word-COM toolchain.

`playwright-cli` is used by all three skills (for `fusionx-urs`, only when a
live UAT walkthrough is needed to ground a story — see its SKILL.md STEP 1.5).
The Python/Word toolchain is exercised by `user-manual-update`'s and
`fusionx-urs`'s build/export/QC scripts — but installing it alongside
`playwright-cli` up front means no teammate stalls mid-run discovering a
missing tool one skill needed and another didn't.

## Skills

- **[`user-manual-update`](skills/user-manual-update/)** — Turns a Jira
  ticket or request into a delivered FusionX module user manual (Accounts,
  Cash, Collateral, Lending, SCO, Term Deposit, or a new module): live UAT
  walkthrough, docx build, delivery. Gate A (pre-draft coverage validation)
  and Gate B (post-build content/formatting validation) are each
  independently re-verified by a fresh subagent dispatch, not self-graded
  by the same thread that did the work.
- **[`functional-testing`](skills/functional-testing/)** — Full QA-style
  functional testing of a FusionX module end to end: transaction-lifecycle
  testing (create/edit/submit/approve/reject/delete, not read-only),
  data-lineage tracing (where a validated value or dropdown option actually
  comes from), and optional source-code cross-verification. Runs a 5-role
  subagent pipeline (Executor, Traceability, Verifier, Source-Verifier,
  Defect-Triage) per round, gated by an upfront round-type choice.
- **[`fusionx-urs`](skills/fusionx-urs/)** — Writes a FusionX User
  Requirement Specification (URS) .docx from a scope statement: module
  reference lookup across all 8 FusionX modules plus OBIE Open Banking specs,
  an elicitation pass before drafting, a cognitive quality pass (ambiguity,
  assumption, edge-case, conflict, gap checks) on the drafted requirements,
  and a two-pass validation gate (content, then seventeen automated
  XML-structural checks against the generated .docx) before the file is
  presented.

More skills are planned as other BA-support activities come up
(requirement-gathering support, etc.).

## Build history and lessons

See [`HANDOFF.md`](HANDOFF.md) for the full build history of each skill —
what was learned, what patterns proved worth repeating (fresh-subagent
validation, independent verification gates, reusing existing templates
instead of inventing new ones), and open follow-ups for whoever builds the
next one.
