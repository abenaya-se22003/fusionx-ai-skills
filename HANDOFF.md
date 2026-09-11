# Session Handoff — Building Skills/Agents for This Project

Reference doc for building the NEXT skill or agent. Written after building and
testing `skills/user-manual-update/` end to end. Read this before starting a
new skill — it's the playbook, not just a changelog.

## What exists so far

- `skills/user-manual-update/SKILL.md` + `gotchas.md` — full pipeline for
  turning a Jira ticket into a delivered FusionX module user manual
  (UAT walkthrough → docx build → export/QC → delivery), with two
  validation gates and a repo-wide audit-trail convention baked in.
- `agents/` — created, currently empty. A custom Agent definition
  (`.claude/agents/<name>.md`) is a DIFFERENT thing from a skill — see
  "Skill vs Agent" below before building one.
- This repo (`fusionx-ai-skills`, remote
  `https://github.com/r4ge-quit/fusionx-ai-skills`, branch `main`) is scoped
  to `.claude/` ONLY — skills and agents, not the surrounding project's UAT
  screenshots/manuals/scripts. It's a **separate git repo nested inside**
  `D:\Work\LOLC\Automation Projects\User Manuals\.claude\` — the parent
  project folder itself is intentionally not under git.
- `.gitignore` here excludes `settings.local.json` (local permission
  allowlist — machine-specific, not for sharing) and `scheduled_tasks.lock`.
  Apply the same exclusions to any new skill's repo — check `.claude/` for
  local/machine-specific files before committing, don't assume everything in
  the folder is shareable.

## Skill vs Agent — decide this FIRST

| | Skill | Agent (`.claude/agents/*.md`) |
|---|---|---|
| Runs in | Current conversation, full interactivity | Separate context, dispatched via `Agent` tool |
| Good for | Tasks needing live back-and-forth (logins, MFA, mid-task questions, user decisions) | Narrow, self-contained tasks with no human-in-the-loop need, or background/parallel work |
| Trigger | Auto (description match) or `/skill-name` | `Agent({subagent_type: "name", ...})` |

Default to a **skill** unless the task is genuinely a narrow, no-interaction
job (e.g. the Gate A/Gate B verification subagents inside the manual-update
skill — those ARE agents, dispatched by the skill, because they need zero
user interaction). Don't build a top-level Agent for something that needs to
ask the user things mid-task — that was the actual reasoning that killed the
"make this whole pipeline an Agent" idea this session; the pipeline has too
many human decision points (version bump, ambiguous source file, scope
sign-off) to run headless.

## Process that worked this session (repeat it)

1. **Invoke `superpowers:writing-skills` first**, before writing anything.
   It mandates a TDD-style cycle for skill authoring — don't skip the
   testing phases even though they cost extra turns; every round found a
   real gap.
2. **Gather source material before drafting**: existing instruction docs,
   scripts, prior memory files, README. Don't invent process — extract it
   from what's already been learned the hard way. For this project that
   meant reading `User-Manual-Production-Instructions.md`,
   `Playwright-Full-Coverage-Instructions.md`, `README.md`, `Scripts/*.py`,
   and the `workflow_manual_update.md` memory file.
3. **Split reference weight**: put the stuff that's genuinely load-bearing
   and NOT yet written anywhere else into the skill's own files
   (`gotchas.md` here). Don't restate what an existing project doc already
   says well — cross-reference it instead (keeps the skill from drifting out
   of sync with the doc it's summarizing).
4. **Test with a fresh-context subagent before calling it done — more than
   once.** Each round in this session: dispatch a `general-purpose` agent,
   foreground (`run_in_background: false`), with NO knowledge of this
   conversation, told only to read the skill files and execute/critique a
   concrete hypothetical scenario. Every one of 3 rounds surfaced a real,
   previously-invisible gap:
   - Round 1: a flat contradiction between the skill's version-bump rule and
     the root instructions doc's "every material revision increments the
     version" line — nobody had noticed until an agent had to actually
     resolve it to build a plan.
   - Round 2 (after adding the audit-trail section): no instructions for
     what to do when `FLOWS-LOG.md` doesn't exist yet, no stated materiality
     boundary for the version-bump question, no note about not backfilling
     history into the new logs.
   - Round 3 (after adding Gate A/B): confirmed the gates added real value
     over the existing Hard Rules, but caught that both gates were
     self-graded by the same agent doing the work — gameable by filling in
     a checklist with unverified guesses.
   **Lesson: testing an agent's own work with an agent that shares its
   context proves nothing. A fresh subagent with no stake in the prior work
   is what actually finds gaps.**
5. **When self-certification is a real risk, make the gate a subagent
   dispatch, not a checklist.** This is the fix for round 3: Gate A and
   Gate B now each dispatch a fresh `general-purpose` subagent (foreground,
   blocking) that independently re-derives evidence (re-drives the live UAT
   screen, re-runs the QC script, re-reads the actual document) rather than
   grading a table the main agent already filled in. On failure, dispatch a
   **new** subagent for the retry — never the one that just passed something,
   since it now has a stake in its own prior pass.
6. **Ask before deciding scope/architecture questions that are genuinely the
   user's call** — don't infer. This session used `AskUserQuestion` for: the
   AUDIT-LOG/FLOWS-LOG reconciliation decision, and the git repo
   scope/remote decision. Both times the user's answer changed the actual
   design, not just cosmetic details.
7. **Git repo, once the skill is stable**: decide scope explicitly (whole
   project vs. `.claude/`-only) — don't default to "everything" when the
   surrounding folder has sensitive/live data (UAT screenshots, defect logs)
   that a teammate pulling the skill doesn't need and shouldn't get by
   accident. Exclude local/machine-specific files via `.gitignore` before the
   first commit, not after.

## Reusable defaults for this project's future skills

- Never bump a deliverable's version number without asking the user
  explicitly — this rule is specific to the manual-update skill but the
  underlying principle (ask before any versioning/release-labeling decision)
  is worth checking for in any new skill that produces a versioned artifact.
- If a new skill involves multi-session verification/audit work, apply the
  `AUDIT-LOG.md`/`FLOWS-LOG.md` convention (see
  `skills/user-manual-update/SKILL.md`'s "Repo-Wide Audit Trail" section for
  the full spec) rather than inventing a different tracking scheme.
- Keep this repo (`fusionx-ai-skills`) scoped to `.claude/` — add new skills
  as `skills/<new-skill-name>/`, new agents as `agents/<new-agent-name>.md`.
  Don't let project-specific working data leak in.
- Before calling a new skill done, run the self-containment audit (see
  "Self-containment audit and distribution fixes" below) — grep for any
  path pointing outside this repo, and confirm every external tool's
  install command is stated where the skill's own Prerequisites points to
  it, not left implicit.

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
  round it ran — 20 validation rounds this time, closing a significant gap where
  source-code contradictions couldn't reach `DEFECT-LOG.md` when the functional
  Verifier had already returned CONFIRMED for that same row.
- New pattern this skill adds: a single subagent role can be reused across
  multiple "modes" (round types A/B/C here) by keeping the role's prompt
  shape fixed and only varying its input scope — avoids needing per-type
  subagent variants.
- Reused `fusionx-test-agent-v0.1.1`'s own templates (`test-plan.md`,
  `bug-report.md`, `coverage-report.md`, `run-summary.md`) and defect
  taxonomy instead of inventing new ones — that tool already had these
  worked out for its own (currently disabled) scenario/bug-triage modes.
- Fresh-subagent validation for a document this dense didn't converge to a
  literal zero-gap round even after 20 rounds — the useful completion signal
  turned out to be "zero structural contradictions found" (achieved) rather
  than "zero gaps found" (not achieved, and per the human's own call, not
  required). If building another skill with many interacting stages/roles,
  expect the same and plan for a human-set round cap rather than an
  open-ended zero-gap loop.

### Follow-up pass: closing known gaps after ship

After merging, the user reviewed the honest gap list this build's summary
surfaced and asked to close three of them: no regression/retest flow for
`DEFECT-LOG.md`, an underspecified Verifier-vs-Traceability lineage
disagreement, and a stale design spec. All three landed in one small
follow-up branch:

- Added a `Resolution status` field to the Bug Report template and a
  `[retest: <identifier>]` row convention so a previously logged defect can
  actually be re-verified in place, never just appended to forever.
- Added a lineage-correction authority rule: Verifier's independent
  `DATA-LINEAGE.md` re-check now supersedes Traceability's claim in the row
  itself when they disagree, and Source-Verifier (which runs after Verifier
  in pipeline order) picks up the correction automatically.
- Updated `docs/superpowers/specs/2026-09-09-functional-testing-skill-design.md`
  with an "Amendments after implementation" section rather than silently
  editing the original approved text — the spec had drifted (4 roles/9
  stages/6 files vs. the shipped 5 roles/11 stages/8 files) because the
  plan evolved during writing-plans but the spec was never revisited.
- **New lesson confirmed by this pass**: a single Critical finding
  (Stage 8's carry-forward optimization for `DATA-LINEAGE.md` rows didn't
  account for a Verifier correction, so a stale source-code verification
  could silently survive) only surfaced because the reviewer was told to
  re-derive the exact failure scenario from its own prior finding, not just
  confirm the diff "looks like" a fix. A reviewer that only checks "is new
  text present" over "does the new text actually force the right dispatch
  in the adversarial case" would have approved a fix that didn't work.
- **Also confirmed**: a plain consistency reviewer (opus, reading the whole
  document for contradictions) and a fresh execution-walkthrough subagent
  (haiku, told to actually run a hypothetical scenario stage-by-stage) find
  different classes of gap — the walkthrough surfaced 9 more genuine small
  gaps (undefined identifier scheme, BLOCKED-retest status left
  unspecified in edge paths, etc.) that the consistency review had no
  reason to look for. Run both when hardening a new addition to an
  already-stable document, not just one or the other.

## Self-containment audit and distribution fixes (this session)

The repo went public-facing this session (`npx skills add` / native plugin
install instructions added to README, meant for the wider team, not just the
original author's machine). That surfaced a class of gap neither skill's
fresh-subagent validation rounds had ever been positioned to catch, because
those rounds always ran on the author's own machine with the author's own
global config already in place — they were testing correctness of the
workflow, never testing what a genuinely fresh install looks like.

- **Found**: `functional-testing/SKILL.md`'s "Read First" step 1 pointed at
  `~/.claude/CLAUDE.md` — the author's personal global config — for the
  Coverage Standard, Dropdowns/Selectable Controls, Search/Filtering,
  Transaction Testing, and Evidence Capture rules, stating "this skill
  inherits all of it and does not restate it." A teammate installing via
  `npx skills add` or the plugin gets the repo's files only, never that
  personal file — so the installed skill was silently missing its own core
  operating rules for anyone but the author.
- **Fix**: inlined all of it directly into `functional-testing/SKILL.md` as
  a new top-level section, mirroring the self-contained treatment
  `user-manual-update/SKILL.md` already had (it already inlined its own
  Coverage Standard and stated "this skill is self-contained" explicitly —
  `functional-testing` was just never given the same pass). Updated every
  internal cross-reference (8 spots) that pointed at "the global
  instructions" to point at the new inlined section instead.
- **Found a second layer**: even after that fix, `playwright-cli` itself —
  a required external CLI tool, not a repo file — was undocumented as an
  install step anywhere `functional-testing` itself blocks on it. The only
  install command (`npm install -g @playwright/cli`) lived in
  `user-manual-update/gotchas.md`, which `functional-testing`'s own
  Prerequisites explicitly calls "not a hard dependency" — inconsistent,
  since a capable browser tool is a hard Stage-0 blocker for
  `functional-testing` specifically.
- **Fix**: stated the install command directly in `functional-testing`'s own
  Prerequisites, not deferred to a sibling skill's optional file.
- **Fix**: added a README "Dependencies" section listing every external tool
  either skill needs, install command included, as one flat common list
  (not split per-skill) — Node.js (`winget install OpenJS.NodeJS.LTS`),
  `playwright-cli` (`npm install -g @playwright/cli`), Python +
  `python-docx`/`pywin32` (`pip install python-docx pywin32`), and a real
  licensed MS Word desktop install (`user-manual-update`'s
  `to_pdf_export.py`/`qc_audit.py` drive real Word over COM — no
  installable substitute).

**Lesson for the next skill**: "self-contained" is a claim that needs its
own explicit check, separate from the fresh-subagent functional-correctness
rounds in the Process section above — those rounds share the author's
already-configured environment by construction, so they cannot surface a
missing external file or tool. Before calling a new skill done, explicitly
audit two things a normal validation round won't: (1) grep the skill's own
files for any path/reference pointing outside this repo (`~/`, another
repo, a personal config file) and either inline it or mark it plainly
optional; (2) list every external *tool* (not file) the skill's
instructions assume is already installed, and make sure the install command
for each one is stated somewhere the skill's own Prerequisites points to
directly — not left to a reader to infer from a script's import statement
or a sibling skill's "by the way" note.

## Next up: URS skill

The next skill to build is for URS (User Requirement Specification) — not
yet scoped. Follow the Process section above: invoke
`superpowers:brainstorming`/`superpowers:writing-skills` first, gather
existing URS source material (templates, prior URS docs, any project
convention already in use) before drafting, and run the self-containment
audit above as a first-class step this time — not a follow-up pass
discovered after the repo already went out to the team, as happened with
`functional-testing` this session.

## Where the deeper history lives

This session's full reasoning (including the earlier back-and-forth on
whether to make this an Agent at all) is in the conversation transcript, not
duplicated here. My own cross-session memory has a `workflow_manual_update.md`
file with the raw lessons this skill was built FROM (numbering-corruption
war stories, screenshot-swap bugs, etc.) — useful if you're ever debugging
why the skill says something oddly specific, but not needed to build the
next skill; this handoff is.
