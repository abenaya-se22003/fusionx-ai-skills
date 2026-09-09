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

## Where the deeper history lives

This session's full reasoning (including the earlier back-and-forth on
whether to make this an Agent at all) is in the conversation transcript, not
duplicated here. My own cross-session memory has a `workflow_manual_update.md`
file with the raw lessons this skill was built FROM (numbering-corruption
war stories, screenshot-swap bugs, etc.) — useful if you're ever debugging
why the skill says something oddly specific, but not needed to build the
next skill; this handoff is.
