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
`/fusionx-ai-skills:user-manual-update`, `/fusionx-ai-skills:fusionx-urs`,
and `/fusionx-ai-skills:api-field-mapper`.

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
  pip install python-docx pywin32 PyMuPDF openpyxl requests
  ```
- A real, licensed Microsoft Word desktop install (Windows). `to_pdf_export.py`
  and `qc_audit.py`'s Word-open check drive real Word over COM automation —
  python-docx alone cannot produce a file guaranteed to actually open in Word
  (see `user-manual-update/SKILL.md`'s Hard Rules). `fusionx-urs`'s own
  `get_page_numbers.ps1` and Pass-2 visual-verification step rely on the same
  Word-COM toolchain.

`playwright-cli` is used by all four skills (for `fusionx-urs`, only when a
live UAT walkthrough is needed to ground a story — see its SKILL.md STEP 1.5;
`api-field-mapper` uses it for its live-capture workflow). Every skill opens
its own named session (`fx-func-…`, `fx-um-…`, `fx-urs-…`, `fx-api-…` — see
`shared/browser-session.md`), so two skills — or two runs of the same skill —
can drive the live app at the same time without one grabbing the other's
browser.
The Python/Word toolchain is exercised by `user-manual-update`'s and
`fusionx-urs`'s build/export/QC scripts — but installing it alongside
`playwright-cli` up front means no teammate stalls mid-run discovering a
missing tool one skill needed and another didn't.

## Skills

### [`user-manual-update`](skills/user-manual-update/)

Turns a Jira ticket or request into a delivered FusionX module user manual
(Accounts, Cash, Collateral, Lending, SCO, Term Deposit, or a new module).

- **Pipeline:** live UAT walkthrough → docx build → export/QC → delivery.
- **Gate A** (pre-draft coverage validation, before a word of manual content
  is written) and **Gate B** (post-build content/formatting validation,
  against the actual delivered docx/PDF) are each a fresh, independent
  subagent dispatch — not the main thread grading its own work.
- Each gate re-derives its own evidence (re-drives the live UAT screen,
  re-runs the QC script, re-reads the actual document) rather than grading a
  table the main thread already filled in.
- Any CONFIRMED finding blocks progress; the retry goes to a **new**
  subagent, never the one that just passed something.
- Maintains a repo-wide `AUDIT-LOG.md`/`FLOWS-LOG.md` audit trail spanning
  every module and session, not just per-ticket detail.

### [`functional-testing`](skills/functional-testing/)

Full QA-style functional testing of a FusionX module end to end:
transaction-lifecycle testing (create/edit/submit/approve/reject/delete, not
read-only), data-lineage tracing, and optional source-code cross-verification.

- **5-role subagent pipeline per round:** Executor → Traceability → Verifier
  → Source-Verifier → Defect-Triage.
- Source-Verifier cross-checks confirmed behavior against the actual codebase
  (read-only); it degrades explicitly, never silently, when no codebase
  connection is configured.
- Gated by an upfront round-type choice: functional only / full traceability
  / targeted traceability.
- Verifier's independent re-check supersedes Traceability's claim when they
  disagree.
- A `DEFECT-LOG.md` entry can be tagged `[retest: ...]` and updated in place
  once a fix is confirmed, rather than duplicated.

### [`fusionx-urs`](skills/fusionx-urs/)

Writes a FusionX User Requirement Specification (URS) .docx from a scope
statement.

- **Module reference lookup** across all 8 FusionX modules: Lending, CASA,
  Customer Onboarding/KYC, Cash & Teller, Term Deposit, MicroFinance, Common
  Settings, and Open Banking/OBIE.
- An elicitation pass before drafting, then a cognitive quality pass
  (ambiguity, assumption, edge-case, conflict, gap checks) on the drafted
  requirements.
- **Three independent subagent checkpoints**, none self-graded by the main
  thread: a pre-draft BA Analyst (ambiguity/gaps, before elicitation even
  starts), Gate A (pre-generation content), and Gate B (post-generation
  docx/QC — seventeen automated XML-structural checks plus a hand-verify
  pass).
- On an update or change request, the verifiers also run a change-impact
  audit — tracing every renamed screen/field/role/rule through diagrams,
  mockups, captions, navigation, stories, dictionaries, and linked artifacts
  — and block delivery on any stale reference.
- A failed check gets a fresh subagent for the retry, never the one that
  just passed something.

### [`api-field-mapper`](skills/api-field-mapper/)

Maps fields in a FusionX Master Data/API Requirements document to
Swagger/OpenAPI operations, or to live-captured dropdown and create/save
network traffic when Swagger alone can't prove the real request/response
shape.

- Renders an auditable Excel workbook with confidence levels
  (High/Medium/Low/Not Found/Blocked) and the raw lookup responses behind
  each row.
- Single main-thread workflow — no subagent dispatch.
- Every task's captures and workbook live in their own numbered task folder
  nested under the module folder, so concurrent tasks (and concurrent
  skills) never collide on output.

More skills are planned as other BA-support activities come up
(requirement-gathering support, etc.).

## Build history and lessons

See [`HANDOFF.md`](HANDOFF.md) for the full build history of each skill —
what was learned, what patterns proved worth repeating (fresh-subagent
validation, independent verification gates, reusing existing templates
instead of inventing new ones), and open follow-ups for whoever builds the
next one.
