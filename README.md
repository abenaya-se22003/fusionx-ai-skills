# FusionX AI Skills

Claude Code skills that support FusionX business-analysis work — user
manuals, functional testing, requirement documentation, release reporting,
and more. Most skills orchestrate a human-in-the-loop workflow that drives
Playwright against a live FusionX UAT session; the rest drive other live
systems (Canva, Jira) the same way. Every skill with a subagent-checkable
step builds independent verification in rather than relying on
self-certified results.

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
`/fusionx-ai-skills:api-field-mapper`, and
`/fusionx-ai-skills:banking-pillar-release-update`.

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
- `playwright-cli` — drives every skill's live browser session
  (network-request capture, named-session reuse, evidence capture):
  ```bash
  npm install -g @playwright/cli
  ```
  Confirm it's reachable with `playwright-cli list`. It's a real shell CLI,
  not an MCP tool, so it won't show up in an MCP tool search.
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
- A configured **Canva MCP connector** and **Atlassian (Jira) MCP
  connector** — needed only by `banking-pillar-release-update`, which
  doesn't touch `playwright-cli` at all. If it's targeting a PowerPoint file
  instead of Canva, it also needs an Office/PowerPoint automation tool
  exposing `execute_office_js`.

`playwright-cli` is used by the four UAT/browser-driven skills —
`functional-testing`, `user-manual-update`, `fusionx-urs` (only when a live
UAT walkthrough is needed to ground a story — see its SKILL.md STEP 1.5), and
`api-field-mapper` (its live-capture workflow) — but not by
`banking-pillar-release-update`, which drives Canva/Jira instead. Each of the
four opens its own named session (`fx-func-…`, `fx-um-…`, `fx-urs-…`,
`fx-api-…` — see `shared/browser-session.md`), so two skills — or two runs of
the same skill — can drive the live app at the same time without one grabbing
the other's browser.
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

### [`banking-pillar-release-update`](skills/banking-pillar-release-update/)

Refreshes one module's release slides in the FusionX Version Release BA
Meeting deck's Banking Pillar section from live Jira data — story point
totals, Epic/Story counts, and one correctly-sized enhancement card per
real ticket.

- Runs against a **Canva design by default**; a PowerPoint file is an
  optional alternate target when the user explicitly asks for it.
- Finds slides by content (module name, slide-role text), never by a
  carried-over page index — every insert/delete shifts later indices, only
  page IDs stay stable within one read.
- Pulls three JQL queries per module (planned / delivered / upcoming) from
  Jira, with an explicit exclusion rule for tickets that carry a
  cross-cutting `IslamicBanking` label in addition to their module label.
- Grows or shrinks continuation slides to match the actual ticket count
  rather than ever shrinking cards to force a fit, and confirms with the
  user before deleting any slot or slide.
- Doesn't use `playwright-cli` — drives Canva/Jira (and optionally
  PowerPoint) MCP connectors instead.
- Built specifically for Banking Pillar's own deck, module labels, and card
  styling — see its
  [`references/repurposing-for-other-pillars.md`](skills/banking-pillar-release-update/references/repurposing-for-other-pillars.md)
  before adapting it for a different pillar's deck.

More skills are planned as other BA-support activities come up
(requirement-gathering support, etc.).

## Build history and lessons

See [`HANDOFF.md`](HANDOFF.md) for the full build history of each skill —
what was learned, what patterns proved worth repeating (fresh-subagent
validation, independent verification gates, reusing existing templates
instead of inventing new ones), and open follow-ups for whoever builds the
next one.
