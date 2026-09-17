---
name: fusionx-urs
description: >
  Use this skill to write, draft, or generate a URS for the FusionX Co-Banking platform at LOLC
  Technologies. Trigger on: "write/draft/create/generate a URS", "URS for [feature]", "write
  requirements for [module]", "I need a URS", or any scope/feature description for FusionX
  modules (Lending, CASA, COB/KYC, Cash & Teller, Term Deposit, MicroFinance, Common Settings,
  Open Banking). Also trigger on any scope statement or change request to formalise. Always use
  this skill — never write a URS from memory alone. Contains: exact LOLC URS format (structure +
  .docx formatting) verified against signed-off samples, FusionX module knowledge for all 8
  modules, OBIE Open Banking specs, and a cognitive quality pass (ambiguity, assumption,
  edge-case, conflict, gap checks) on drafted requirements, not just formatting.
---

# FusionX URS Writer — LOLC Technologies
*Backed by: Live Confluence module knowledge · OBIE Open Banking specs · Real LOLC URS format samples*

This skill produces two things that both have to be right: the **content** (correct module
knowledge, correct navigation paths, correct business rules) and the **document** (a .docx that
looks like it came from the same template every time — same fonts, same colors, same table
styles, same column proportions). Past versions of this skill got the content right but let the
document drift: headings would silently fall back to the theme font instead of Candara, table
header colors would vary table-to-table, and data-heavy tables (Data Dictionary, E2E Impact)
were given so little column width that every cell wrapped into a vertical ladder of single words.
The DOCX FORMATTING section below exists specifically to prevent that drift — treat it as
load-bearing, not decorative.

**Operating stance: you are acting as the Business Analyst on this engagement, not a formatting
tool that turns a scope statement into a document.** A BA's actual job is to make sure a
requirement is understood and complete *before* writing it down — which means noticing when a
scope statement is thinner than it sounds, asking the stakeholder (the user) the few questions
that would actually change what gets written, and only then drafting. Don't silently pad gaps with
plausible-sounding text and don't ask about everything either — a BA who interrogates every detail
is as useless as one who never asks anything. STEP 1.5 below is where this happens, before any
drafting starts; the cognitive quality pass in STEP 2 is the second half of the same discipline,
applied to what actually got drafted.

**Validation prerequisite:** the `Agent` tool must be available for the
pre-draft BA Analyst and the two independent verification dispatches described
below. Confirm that it can run a foreground `general-purpose` subagent before
drafting. If it is not
available, tell the user before generation and do not present a final `.docx`
as fully validated unless the user explicitly accepts that exception.

---

## STEP 0 — ALWAYS FIRST: Load Reference Files

Before writing a single word, identify the module(s) from the scope and load the relevant files.
**This is mandatory — never skip.**

### Module Reference Files
Read `<skill-root>/references/<filename>`, where `<skill-root>` is the directory containing this
`SKILL.md`. Do not assume a machine-specific installation path.

| Module | Trigger Keywords | File |
|---|---|---|
| Lending / Loan Management | Lending, Loan Origination, Loan Account, Repayment, Penal Interest, Arrears, Write-off, Bad Debt, Due Date | `lending.md` |
| CASA / Accounts | CASA, Current Account, Savings Account, Standing Order, Cheque, Overdraft, OD | `casa.md` |
| Customer Onboarding / KYC | COB, Customer Onboarding, KYC, AML, PEP, Customer Registration | `cob.md` |
| Cash & Teller | Cash, Teller, Vault, Till, Cash Deposit, Cash Withdrawal, Teller Limit | `cash-teller.md` |
| Term Deposit | Term Deposit, TD, Fixed Deposit, FD, Maturity, Renewal, TD Interest | `term-deposit.md` |
| MicroFinance | MicroFinance, MF, Microenterprise, ME, Center, Group Lending | `microfinance.md` |
| Common Settings | Common Settings, GL, General Ledger, Tax Code, Holiday, Currency, Alert, Blacklist | `common-settings.md` |
| Open Banking | Open Banking, PCA, BCA, SME Loan, AISP, PISP, TPP, OBIE, MMC, AER, DCR, FAPI | `open-banking.md` |

**Also always load the URS format reference:**
Read `<skill-root>/references/urs-format.md`.
This contains the exact section structure, table formats, numbering scheme, and writing rules,
cross-checked at the raw XML level against four real LOLC files: Transaction Reversal – Interest
Rollback URS V1.0 (most authoritative), the blank XX-Module and Master org templates, and the
Lending Module V0.1 draft.

**If scope spans multiple modules** (e.g., Lending feature that impacts GL): load all relevant files.

**If no reference file exists for the module** (Authorization, Yard Management, Supplier):
proceed using general conventions and flag `[Confluence reference not yet available — verify navigation paths]`.

**Live Confluence lookup** (when more detail is needed beyond reference files):
- Search: `Atlassian Rovo:search` with the feature or screen name
- Fetch page: `Atlassian Rovo:getConfluencePage` cloudId=`50681345-b1f0-46ba-875b-dde9c72f71c5`
- Search epics: `Atlassian Rovo:searchJiraIssuesUsingJql` with module JQL from reference file

---

## STEP 1 — INTAKE

Identify the following from the scope statement. If any are missing, ask **all at once in a single message**.

| Field | Source / Default |
|---|---|
| Feature / Enhancement title | From scope statement |
| Module | Infer from scope; ask if ambiguous |
| Type: New Development or Enhancement | Ask if not clear |
| Drafted By (BA name) | Ask |
| Reviewed By (Senior BA name) | Default: leave blank |
| Client Name | Default: LOLC Technologies Pvt LTD |
| Version | Default: 0.1 |
| Release Date | Today's date in DD/MM/YYYY format |
| Related Jira ticket (PF-XXXXX) | Default: [TO BE CONFIRMED] |

Do **not** ask for what you can infer from the scope statement.

---

## STEP 1.5 — ELICITATION (interactive — this is the thinking part, not a formality)

STEP 1 collects metadata. This step is different: it's where you actually interrogate the scope
statement the way a BA interrogates a stakeholder ask, before committing anything to a draft.
Adapted from `requirements-interrogator` and `probe-question-generator`
(`45ck/business-analysis-skills`). Do this every time, even for a scope statement that reads as
complete — completeness is exactly what needs pressure-testing, not assumed.

### Pre-draft BA Analyst dispatch (mandatory)

Before the main thread asks the user elicitation questions, dispatch a fresh
foreground `general-purpose` subagent to perform an independent intake review.
Give it the raw scope/request, the relevant module reference files, and—when
this is an update—the baseline URS and requested change. Do not give it the
main thread's assumptions or proposed questions. It must return:

- normalized actors, triggers, flow boundaries, data, outcomes, and affected
  modules;
- material ambiguities and decision questions, each tied to what it changes;
- missing stakeholders, permissions, dependencies, integrations, failure
  paths, and change-impact candidates;
- whether a live UAT walkthrough is appropriate, based on the screen's
  existence and stability.

The subagent does not contact the user, invent answers, or draft URS content.
The main thread reviews its report, combines it with the inline BA checks
below, and asks the user one batched set of decisive questions. Any question
that remains unanswered becomes an explicit Open Question or blocks drafting
according to the existing elicitation rules.

Example dispatch shape:
```
Agent({
  subagent_type: "general-purpose",
  run_in_background: false,
  prompt: "Act as the independent pre-draft BA Analyst. Read the supplied
  scope, module references, and baseline URS/change request if present.
  Normalize actors, trigger, flow boundary, data, outcomes, dependencies,
  stakeholder/permission gaps, failure paths, and likely change impacts.
  Produce decisive questions tied to what each answer changes, and recommend
  whether live UAT grounding is appropriate. Do not contact the user, invent
  answers, or draft requirements. Do not trust prior assumptions."
})
```

If this dispatch errors, times out, or returns an unusable report, dispatch a
new BA Analyst before asking the user questions. Never reuse a verifier for
this role or treat the main thread's own elicitation as its substitute.

**1. Normalize the scope statement.** Silently (don't show this as a separate deliverable) sort
what you were given into: the actor(s)/role(s) involved, the trigger, the main flow, what data is
touched, what business rule(s) are implied, what's explicitly out of scope, and what's simply
missing. Don't invent certainty for anything that isn't actually there yet — a gap stays a gap at
this stage, it doesn't get silently filled in.

**2. Cross-check against what you already know.** For every gap from step 1, check the loaded
module reference file and Confluence/Jira first — a lot of "missing" information (screen names,
navigation paths, standard field validation, existing behavior) is actually already known and
doesn't need asking. Only what's genuinely undetermined even after checking your own knowledge
graduates to step 4.

**3. Consider a live walkthrough for user-flow accuracy — but only when the screen already exists
and is stable.** Navigation paths, stepper sequences, exact field names, and dropdown values are
exactly the kind of detail that's easy to get subtly wrong from a scope statement or module
reference alone, and exactly the kind a live look at the actual screen would settle outright. But
this only helps when there's a real, finished screen to look at:
- **If the feature's screen(s) already exist live in FusionX UAT and the flow is stable** (not
  mid-development, no pending stepper/field changes before release): ask the user for the FusionX
  UAT URL and do a live walkthrough to ground the User Flow, navigation paths, and Section 7 story
  details in what's actually there. For browser lifecycle, login/MFA, session reuse, viewport, and
  evidence handling, read and follow `references/browser-session.md`; it is the self-contained,
  mandatory Playwright contract for this skill. Per its Section 0, open this session under this
  story's own name, `fx-urs-<ticket-or-story-id>-<tag>` — never a bare `playwright-cli` call, and
  never a session found by running `list` and picking whatever looks authenticated, since that
  session may belong to a different, concurrently-running URS story or a different skill entirely.
  Check for browser automation access before assuming
  it's unavailable — `playwright-cli` is a shell CLI, not an MCP tool, so confirm it with
  `playwright-cli --version` rather than concluding "no Playwright access" from tool-search
  results alone. Once
  authenticated, walk the flow in full depth by default, not as a breadth-only click-through:
  verify dropdown values via the live DOM not just the accessibility snapshot, no loading-spinner
  races, capture evidence continuously). This is a grounding step, not a full UAT coverage sweep —
  walk the specific flow this story covers, not every adjacent screen.
- **If this is new development, or the flow/steppers are still expected to change before this URS
  ships**, skip the walkthrough entirely — a walkthrough of a moving target goes stale by release
  and produces false confidence in details that are about to change. Rely on the scope statement
  and this step's own elicitation (steps 4-5 below) instead, and mark navigation paths/field names
  that couldn't be verified as `[not yet verified against a live screen — confirm before sign-off]`
  rather than presenting them as settled.
- **If it's unclear which case applies, ask directly**: "Does this screen already exist live in
  FusionX UAT, and is the flow (steppers, fields) considered final, or still likely to change
  before this URS is finalized?" — the answer alone decides whether a walkthrough is worth doing.

**4. Classify remaining gaps by risk, not by whether they're answerable.** For each real gap, ask:
if you guessed wrong here, would the URS's actual requirements be wrong — not just cosmetically
different? High-risk examples: which role(s) can perform the action, what happens on a validation
failure or rejection, whether an existing behavior is being changed or only extended, a business
rule with a threshold or condition that isn't stated (a limit, a time window, an approval level).
Low-risk examples: exact button/field label wording, which screen a field sits on if the module
reference already implies it, cosmetic phrasing. High-risk gaps get asked about. Low-risk gaps get
a stated, reasonable default and go into 1.4 Assumptions instead of interrupting the user.

**5. Ask well, not much.** If there are high-risk gaps, ask them **all at once, in a single
message** (same rule as STEP 1) — don't trickle questions one at a time. Each question should be
concrete enough to answer decisively, not generic:
```
Bad:  "Any other requirements I should know about?"
Good: "Should the Request Change action be restricted to Approval Officers only, or can any
       approver at any level trigger it?"
Good: "What should happen if the creator resubmits without editing any of the enabled steppers —
       block resubmission, or allow it since nothing prevents an unchanged resubmission today?"
```
Tie each question to what it actually changes in the URS (a business rule, a validation, a
Data Dictionary field) — don't ask about things that wouldn't change what gets written either way.

**6. If there are no high-risk gaps, say so and proceed** — don't manufacture questions to seem
thorough. "Scope is clear enough to draft — proceeding" is a legitimate, correct outcome of this
step, not a skipped step.

**Question design aids** (adapted from `45ck/business-analysis-skills` and `olbboy/BA-Kit`'s
elicitation techniques): frame each question with 5W1H (Who/What/When/Where/Why/How) rather than
yes/no where possible — "Who specifically can trigger this?" surfaces more than "Can anyone
trigger this?". Use the funnel: start broad enough to catch something you didn't anticipate, then
narrow only where the broad answer left a real gap. Before finalizing a question, check it doesn't
already assume the answer — "How many approval levels should this have?" assumes multi-level
approval exists; if that's not established, ask "Does this need more than one approval step?"
first. Also check stakeholder coverage, not just the person giving you the scope statement: who
directly performs the action, who's downstream of its result (indirect users, other teams reading
a report it feeds), and who owns the rule being changed (approver, compliance, product owner) — a
missing stakeholder category is itself a gap worth surfacing, not just a missing content item.

**Don't rationalize skipping this step.** Time pressure or an apparently-clear scope statement are
exactly the conditions this step exists for:

| Rationalization | Reality |
|---|---|
| "Scope statement is detailed, elicitation would be redundant" | Detail isn't completeness — a long paragraph can still omit every failure path. Run steps 1-4 regardless; only step 5 (asking) is conditional on what they find. |
| "I can infer the missing role/rule from a similar past story" | Inference is a guess wearing confidence. If step 4 classifies it high-risk, ask instead of inferring. |
| "Asking questions will slow the user down" | A wrong assumption costs a full redraft later; one batched question message costs one reply now. |
| "The user will correct me in the draft review anyway" | STEP 2.5 catches structure and formatting, not whether the underlying business rule was ever verified — draft review isn't a substitute for elicitation. |
| "The screen probably still looks like the last one I saw" | Screens change between UAT builds. If step 3 says the flow is stable and live, verify it fresh rather than reusing a stale mental picture. |

**Red flags that steps 4/5 were skipped, not just fast:** every gap classified low-risk with none
high-risk on a multi-actor or approval-related feature; zero questions asked despite the scope
statement never mentioning a failure/rejection path; "Scope is clear enough to draft" used on a
feature involving money movement, an approval chain, or a new role — these are exactly the
categories where an unstated rule is expensive to get wrong. Also a red flag: navigation paths
presented as confirmed fact when step 3 was never actually resolved (neither walked through live
nor explicitly marked unverified) — that's the same "looks right but isn't real" failure mode this
skill was built to catch, just applied to flow accuracy instead of docx formatting.

Once elicitation is resolved (answered, or explicitly deferred to Open Questions with the user's
sign-off), proceed to STEP 2.

---

## STEP 2 — DRAFT IN CHAT

Generate the full URS as a structured markdown draft in chat, section by section.
**Always follow the exact 12-section order below** (verified against real signed-off LOLC URS samples).
**Always use reference file navigation paths, screen names, and E2E defaults — never guess.**
**For Section 7 specifically, drafting is not filling in a template — see "How to think through
each story" under SECTION 7 below and actually work through it per story, not just at the end.**

### Cognitive quality pass — run before presenting the draft, not after

This is the second half of the same discipline STEP 1.5 applies before drafting — that step
pressure-tests the *input* (the scope statement); this one pressure-tests the *output* (what
actually got written), since even a well-elicited scope can still end up drafted sloppily.
Everything else in this skill (structure, table shapes, numbering, spacing, fonts) checks whether
the document is built *correctly*. None of it checks whether the requirements themselves are any
*good* — a URS can pass every structural and formatting check while its Action rules are vague,
its Assumptions section misses what the rules are quietly relying on, its Test Scenarios are all
happy-path, its Risks contradict its Scope, or a Data Dictionary field nobody's business rule ever
references. This pass is adapted from eight techniques in a public BA-skills reference
(`45ck/business-analysis-skills`) and exists to catch exactly that class of gap, before the user
spends time reviewing a draft that has structural polish but weak substance underneath.

Run all eight against the drafted Section 5-11 content (Scope, Epic, Stories, Data Dictionary, E2E
Impact, Test Scenarios) before presenting. Each is a short, targeted scan — don't turn this into a
separate deliverable; fold findings directly into the draft, then note in your presentation message
what you tightened.

Run this as a literal self-critique, not a silent mental tally. For each check, pose the question
to yourself and actually answer it before moving to the next — the master question behind all
eight is *"Critic: what am I assuming here, and how do I know it's true?"*; the numbered checks
below are that same question aimed at eight different failure classes.

1. **Ambiguity check.** Scan Action/Trigger/Expected text and General Guide Line rows for
   subjective terms with no defined threshold. Forbidden without a number, rule, or explicit
   reference to back them: *adequate, appropriate, as quickly as possible, easy, efficient, fast,
   flexible, good, intuitive, lightweight, maximize/minimize, normal, optimal, quick, reasonable,
   robust, seamless, simple, sufficient, timely, transparent, user-friendly, significant, TBD.*
   Also scan for pronouns or nouns with an unclear referent, and conditions implied but not spelled
   out. *Critic: if I flag "user-friendly," is it actually backed by a named style guide or
   standard elsewhere in the doc — or is it decoration?* Rewrite tighter or flag as an Open
   Question — don't leave it polished-sounding but unverifiable, and don't over-flag a term that's
   genuinely grounded elsewhere (e.g. "consistent with existing screen layout" is fine; "intuitive"
   alone is not).
2. **Assumption check.** For every business rule in Action/Trigger that quietly depends on
   something being true (a field already populated, a status already reached, a role already
   provisioned, data already migrated), confirm that dependency is either explicit in the rule
   text or listed in 1.4 Assumptions. A rule that silently assumes something not stated anywhere
   is a gap, not a clean requirement — add the assumption explicitly rather than leaving it buried.
3. **Edge-case check (Section 11 specifically).** Happy path plus one validation error is not
   sufficient coverage — that was already the minimum bar (see Section 11 below), this check is
   what makes it real instead of token. Systematically consider, grounded in the actual fields and
   rules just drafted (not generic placeholders): boundary values against Data Dictionary's Data
   Validation column, invalid/malformed input, duplicate or concurrent submission, unauthorized
   user attempt, maker-checker violation, partial/interrupted state, stale or already-processed
   data, and EOD/batch timing edges where applicable.
4. **Conflict check.** Cross-read Assumptions against Risks, Scope (in vs out) against what Action
   actually implements, and General Guide Line's "existing functionality preservation" rule
   against what this story changes. Flag any contradiction with both conflicting statements quoted
   side by side — don't silently resolve it by picking one; that's a decision for the user for
   anything non-obvious.
5. **Gap check.** Walk the drafted Action rules against: every actor/role named, preconditions
   stated, a validation rule for every field touched, a permission/authorization rule where
   relevant, an error/failure path (not just the success path), and whether every Data Dictionary
   field is actually referenced by some rule (an orphaned field the business rules never mention is
   a sign something's missing, not just a formatting nit).
6. **Bias/logic check.** Re-read Assumptions and Risks specifically for hidden assumptions stated
   as settled fact ("users will always..."), unfounded absolutes ("never," "always," "all users"),
   and causal claims with nothing backing them ("this will reduce errors" — based on what, versus
   what baseline?). A Risk or Assumption that overstates its own certainty is a defect the same way
   a vague requirement is — soften the certainty or ground it in something concrete from the scope
   statement or module reference.
7. **Terminology consistency check.** The same role, actor, screen, field, or status value must be
   named identically everywhere it appears — across every story, the Data Dictionary, and the E2E
   Impact table. "Approval Officer" in Story 1 and "Approver" in Story 3 for the same role is a
   defect even though each instance reads fine in isolation; it's the kind of inconsistency a
   single-story read-through won't catch but a cross-document scan will.
8. **Traceability check.** Every "what is in scope" bullet (5.1) should trace to at least one
   story; every story's Action rules should trace to at least one Data Dictionary field group;
   every Data Dictionary field should trace to at least one Test Scenario, or be explicitly
   uninteresting to test (e.g. a purely display-only audit timestamp). A scope item with no story,
   or a story with no test coverage anywhere, is a gap in the chain — note it rather than letting
   the chain silently break.

**Don't rationalize skipping or shortcutting this pass:**

| Rationalization | Reality |
|---|---|
| "This story is simple, doesn't need all 8 checks" | Simple-looking stories hide the same defect classes — a one-field update story still has an actor, a failure path, and a Data Dictionary reference to check. |
| "I already thought about this while drafting" | STEP 2's checks operate cross-document (terminology, traceability) — a per-story read can't catch those; they only surface reading the whole draft at once. |
| "The user will catch anything I missed in review" | The point of this pass is to hand the user a draft worth reviewing for substance, not one they have to debug for basic gaps first. |
| "Flagging every vague word will annoy the user" | Only flag what fails the check — a term backed by a stated rule or standard elsewhere isn't a defect (see check 1's critic question); under-flagging to avoid friction just ships the ambiguity instead. |

Findings that are clear-cut (missing units, an obviously-implied assumption) get fixed directly in
the draft. Findings that are genuinely ambiguous or would require guessing the user's intent go
into Section 2 (Open Questions) instead of being silently resolved either way.

Tell the user: *"Here's your URS draft. Review it and let me know any changes before I generate the Word document."*

---

## STEP 2.5 — VALIDATION GATE (mandatory, blocking — run twice)

**This gate applies every time this skill produces or touches a `.docx` — not only on a fresh
STEP 1-3 draft.** If the task is "make some changes to this existing URS," "fix this section,"
"regenerate this file," or any other edit to a `.docx` that already exists, that is still this
skill's output and Pass 2 still runs before the file is handed back. Confirmed failure mode from a
real file: a session asked to make content changes to an already-fixed URS regenerated it using the
generic/default numbering approach instead of this skill's documented recipe, silently reverting
numbering fixes (`suff="tab"`, widened hanging-indents, no leading-space runs) that a prior session
had already put in place — because it treated "edit an existing file" as outside the scope of the
validation gate. It is not. Read `references/docx-formatting.md`'s numbering section in full before
writing or regenerating any numbering-bearing content, and run Pass 2 for real (actual script
output, not a claimed `[PASS]`) before presenting the result, regardless of how small the requested
change sounds.

## Independent validation dispatch (mandatory for every URS)

The main thread owns intake, elicitation, drafting, user confirmation, and
fixes. The two validation passes below must be independently verified by fresh
subagents; do not self-certify them from a checklist you wrote yourself.

- Dispatch each verifier with `subagent_type: "general-purpose"` and
  `run_in_background: false`. The dispatch is blocking and its result gates
  the next step.
- Use a new subagent for the pre-draft BA Analyst, a different new subagent
  for Gate A, and a third new subagent for Gate B. If a
  verifier fails, times out, or returns an unusable result, dispatch a fresh
  retry; never reuse the instance that already saw the draft or file.
- Give each verifier the exact artifact paths and source material it needs,
  but do not give it the main thread's claimed checklist or conclusions. It
  must independently re-read the draft or generated `.docx`, run the required
  scripts, and report `PASS`, `FAIL`, or `EXCEPTION: reason` for each item.
- A substantive `FAIL` blocks progress. Fix the underlying draft/build issue
  and dispatch a new verifier to re-check from scratch. The main thread may
  summarize the verdict, but may not turn an unresolved failure into a pass.

Gate A's fresh verifier independently checks the chat-confirmed draft against
the full CONTENT CHECKLIST before generation. Gate B's fresh verifier
independently opens the generated DOCX, reruns `qc_audit.py` and the required
structural checks, and performs the visual review required below when Word is
available. If either verifier needs a missing business decision, it returns an
open question to the main thread instead of inferring user intent.

### Change-impact audit (required when this is an update or change request)

The verifier must not check only the newly edited sentence or section. First
derive the changed items (for example, an old and new screen name, field,
role, status, rule, or flow step) from the request and the baseline document.
Then search and visually inspect every place the item can affect, including:

- flow diagrams, UI mockups, screenshots, figure labels, captions, and
  navigation paths;
- Section 5 Scope, Section 7 stories (all six rows), Preconditions, Triggers,
  Expected outputs, and cross-story references;
- Data Dictionary Feature/Field/Source entries, E2E Impact rows, Test
  Scenarios, Open Questions, Assumptions, Risks, Annexure, and any module
  reference or linked artifact named in the URS.

For embedded diagrams or mockups, a text search is insufficient: inspect the
rendered image and its caption/alt text for stale labels. Report an impact
matrix with `changed item`, `reference location`, `required update`, and
`evidence/status`. A stale or missing update is a `FAIL`, even when the edited
section itself is correct. The main thread must apply the correction across
all affected areas and dispatch a new verifier; the verifier does not silently
patch its own finding or mark an unresolved reference as an exception.

Example dispatch shape (adapt paths and scope):
```
Agent({
  subagent_type: "general-purpose",
  run_in_background: false,
  prompt: "Act as the independent URS verifier. Read the supplied scope,
  references, draft or DOCX, and fusionx-urs/SKILL.md. Re-derive the relevant
  checklist, inspect the actual artifact, run required scripts, and report
  every item as PASS, FAIL, or EXCEPTION with evidence. Do not trust prior
  checklists or conclusions and do not edit the artifact."
})
```

For Pass 1, post the fresh Gate A verifier's itemized verdict as the content
checklist result; the main thread may fix the draft and explain changes but
must not replace the independent verdict with its own unverified pass. For
Pass 2, post the fresh Gate B verifier's itemized verdict together with the
actual script output and visual-review result.

Generating the .docx is not the next action after content confirmation. Two separate, blocking
checklist passes sit between "content confirmed" and "file handed to user," and neither is a soft
reminder — each is a literal checklist you must post as chat output, item by item, before
proceeding. **Do not generate or present the .docx while any item is unresolved.**

**Pass 1 — before generating, against the chat-confirmed draft.** Walk every item in the CONTENT
CHECKLIST below (structure, table shapes, numbering rules, row sets) against the draft. Post the
checklist with a literal pass/fail per item, e.g.:
```
[PASS] All 6 story rows present, all 6 row labels numbered (7.1.1-7.1.6), real numPr not typed digits
[PASS] E2E Impact table uses the 8-row Area set (no Repayment Schedule Engine / Loan Accounting-GL rows)
[FAIL] General Guide Line still has the generic 7-row template placeholder text — needs feature-specific rows
```
Any `[FAIL]` blocks generation. Fix the draft and re-run Pass 1 — don't generate around a known
failure and fix it "in the docx" instead; fix the content, then re-check. This is a loop, not a
single retry (see the escalation rule under Pass 2, same principle applies here).

**Pass 2 — after generating, against the actual .docx file.** Content compliance doesn't imply
formatting compliance — they can pass and fail independently. Re-open the generated file (don't
rely on memory of what you intended to generate) and walk the FORMATTING CHECKLIST below the same
way, item by item, with an explicit pass/fail. Any `[FAIL]` blocks presenting the file — fix the
generation and re-run Pass 2.

**This is a loop, not a single retry — keep fixing and re-running until every item is `[PASS]` or
`[EXCEPTION: reason]`, not until you've tried once.** A `[FAIL]` that persists after one fix
attempt is not grounds to present the file anyway, note the issue in a caveat, or quietly move on
to a different item — go back to the specific paragraph/table/list the script or checklist flagged
and fix that exact thing, then re-run the same check again, same as Pass 1. If a specific item is
still `[FAIL]` after 3 fix attempts, stop looping blindly (that's a sign the fix approach itself is
wrong, not that one more try will work) — tell the user directly which item won't resolve, what
you tried, and ask whether to keep debugging or accept it as a documented, explicit exception. Do
not silently present a file with an unresolved `[FAIL]`, and do not silently give up and present it
anyway without saying so.

**The numbering, front-matter, and body-spacing checks are not visual checks — run the scripts.**
A user reported generated output where numbers looked correct on inspection but were typed text
(editable, didn't renumber on delete) rather than real Word list fields, and separately reported
spacing problems both in the Table of Contents / List of Figures / List of Tables region and more
generally — inside tables and around image captions — that trace to the same class of issue (see
`docx-formatting.md`'s "Spacing — full audit"). All of these look identical to correct output in a
rendered preview or a quick read-through, so eyeballing any of these checklist items is not
sufficient and has already produced false passes — including, at one point, false passes hiding
behind a still-broken font/color checklist item, since "Font check" and "Color check" were
eyeball-only until fonts/colors got the same script treatment as numbering, and a real generated
file (Blacklist Rule to Transaction Event Mapping URS) later showed a session can self-report
`[PASS]` on numbering while its actual XML uses the wrong suffix and invented indent values —
which is why `check_numbering_gap()` exists and why every one of these checks means actually
running the script, not describing what it would probably say. Run all seventeen checks from
`references/docx-formatting.md`'s "MANDATORY: verify numbering, fonts, colors, and
front-matter/body spacing" section against the actual generated file and paste all seventeen
outputs as part of the Pass 2 report — a `[PASS]` on any of these items requires the corresponding
script's `PASS` output, not a visual read of the document:
- `check_numbering()` — story sub-points inside table cells (e.g. `7.1.2.1.`)
- `check_numbering_gap()` — the number-to-text gap mechanism itself: `suff="tab"` (not `"nothing"` outside the documented COM-Save exception) and no literal leading space/tab typed into a numbered paragraph's text
- `check_heading_numbering()` — section headings and sub-headings (e.g. `1.`, `1.6.`)
- `check_bullets()` — Assumptions/Risks/Scope/Test Scenarios
- `check_second_list_start()` — the Data-Dictionary-onward multilevel restart quirk
- `check_front_matter()` — Table of Contents / List of Figures / List of Tables fields, their placement (never numbered, always before Section 1), and their spacing
- `check_section_transitions()` — heading-after-table/list spacing everywhere else in the body
- `check_body_spacing()` — coarser safety net for any other stacked empty paragraphs
- `check_fonts()` — every text-bearing run has an explicit Candara (or Arial for `→`) override — this is the check that was missing when a user reported generated fonts not matching the reference doc despite the spec being documented correctly
- `check_colors()` — cover title (`0070C0`) and every numbered section heading (`2F5496`, run-level or via its paragraph style's own default)
- `check_table_styles()` — every table references a named `tblStyle` (not manual borders alone)
- `check_no_cell_margins()` — no table cell has an explicit `tcMar` override anywhere
- `check_heading_indent_progression()` — heading numbering indents level 1 further right than level 0, not flush at every level
- `check_no_docdefault_paragraph_spacing()` — `styles.xml`'s document-level default paragraph spacing is empty/absent (setting it inflates table row height ~2.4x)
- `check_toc_field_live()` — ToC/LoF/LoT fields have no leftover `<w:sdt>` wrapper, no stale `w:dirty="true"`, and balanced field boundaries
- `check_toc_page_numbers_real()` — ToC/LoF/LoT entries show real, varying page numbers, not a uniform unpatched placeholder
- `check_hex_ids()` — every `w14:paraId`/`wp14:anchorId`/`wp14:editId` attribute value is valid 8-digit hex (`^[0-9A-Fa-f]{8}$`); an invalid value (e.g. a non-hex letter) is a confirmed hard-open-failure cause when new paragraphs/images are hand-spliced into an existing real file

Then separately eyeball the table-cell-spacing, image/caption-adjacency, and other not-yet-scripted
color rules (nav paths, captions) that no script covers yet (same section explains why).

**If Word is available in this environment (check for `WINWORD.EXE`, e.g. under `Program Files\Microsoft Office`), visual verification via actual rendering is REQUIRED before presenting the file, not an optional nice-to-have.** All seventeen scripted checks above are XML-structural — they catch typed-vs-real numbering, missing fields, wrong colors, missing table styles. They cannot catch how something actually renders: margins, spacing gaps, row height, page layout. Every one of those was, at some point this project, wrongly believed fixed because all scripted checks passed and the file "looked right" in a quick description — and was later found wrong only when the user provided a screenshot or asked for a direct comparison. Do not wait for that. If Word is available:
1. Open the generated file via Word COM automation (PowerShell `New-Object -ComObject Word.Application`, `.Visible = $false`), call `.Fields.Update()`, export to PDF (`ExportAsFixedFormat`), close, quit.
2. Render every PDF page to PNG (e.g. PyMuPDF) and actually look at each one — not just the cover page. Compare against a real reference file rendered the same way, section by section (cover, front matter, every heading level, every table, every figure/caption).
3. For any specific discrepancy suspected (spacing gap, indent, row height), measure it — extract exact pixel/point positions from the rendered PDF (e.g. `page.get_text("dict")` bounding boxes) and compare the number directly against the same measurement on the real file. "Looks close" is not sufficient once a discrepancy is suspected; get the actual numbers on both sides. **Exception: for table cell padding/margins specifically, PDF-position inference is NOT reliable enough — confirmed to produce a false lead once (it silently compared two structurally different tables that happened to share matching cell text). Use a direct Word-COM property query instead: `Table.Cell(1,1).LeftPadding`/`.RightPadding` on the first cell of every distinct table style used in the document, compared directly against the same query on a real reference file.** This is also the only way to catch the defect class where `check_no_cell_margins()` passes (no explicit override) but the implicit default padding still isn't resolving (confirmed real, separate defect — see docx-formatting.md's "Real cell padding requires injecting TableNormal" section).
4. Kill any lingering `WINWORD.EXE` process before regenerating the file (Word holds a file lock that causes the next `node`/write step to fail with `EBUSY`).
If Word is not available in this environment, say so explicitly to the user rather than silently skipping this step or presenting the file as if it had been visually confirmed.

Only after both passes show all-`[PASS]` (plus visual verification where Word is available) do you
present the file to the user. If a genuine exception applies (e.g. no Jira ticket exists yet, so
the Annexure link is legitimately a placeholder), mark it `[EXCEPTION: reason]` rather than
`[PASS]`, and say so explicitly when presenting the file — don't silently pass an item that isn't
actually met.

---

## STEP 3 — GENERATE .docx ON CONFIRMATION

Once confirmed and Pass 1 of the validation gate is clean, install the bundled generator once with
`npm --prefix <skill-root>/generator ci`, then run:
`node <skill-root>/generator/build.js <draft-json> --output <output-docx>`.
The input schema is documented in `<skill-root>/references/build-input.md` and an executable
example is supplied at `<skill-root>/examples/urs-draft.example.json`. Apply LOLC formatting (see DOCX FORMATTING section below)
**exactly** — don't improvise table styles, column widths, numbering mechanism, or font handling,
since that's what causes documents to look inconsistent from one URS to the next.
Save to the user-agreed output directory. If none is given, use `./outputs/[FeatureName]_URS_V[version].docx`
relative to the current project; create `outputs/` if needed.

**The generation pipeline for any document with a Table of Content is three phases, not two — the
third is not optional. Use the scripts in this skill's `scripts/` folder as the starting point,
don't rederive this logic from prose each time — that's what took many rounds to get right the
first time:**
1. `node <skill-root>/generator/build.js <draft-json> --output <output-docx>` followed by
   `python <skill-root>/scripts/postprocess_template.py <output-docx>`. Builds the file, including a
   genuinely live ToC/LoF/LoT field with real bookmarks and entries, but only a placeholder page
   number in each entry — pagination can't be computed without an actual layout engine.
2. If Word is available: run `<skill-root>/scripts/get_page_numbers.ps1 <docx> <mapping-file>` (read-only —
   opens via COM, `Repaginate()` + `Fields.Update()`, reads each `PAGEREF` field's real computed
   page number, closes **without saving**; never add a `.Save()` call to this, see the Word-COM
   destructive-save warning in docx-formatting.md), then `python scripts/patch_page_numbers.py
   <docx> <mapping-file>` to substitute the real numbers into the file step 1 already produced. If
   Word is not available, stop before delivery: real page numbers are a required quality gate.
3. Run `python <skill-root>/scripts/qc_audit.py <docx>` and Pass 2 of the validation gate (STEP 2.5)
   before presenting the file.

See docx-formatting.md's "Table of Content / List of Figures / List of Tables must be genuine,
live, updatable Word fields" section for exactly why each of these phases is required and what goes
wrong if any is skipped — this was explicitly, repeatedly demanded by the user: the ToC/LoF/LoT must
behave like one inserted by hand in Word (right-click → Update Field works after future edits), not
a one-time static snapshot.

---

## DOCUMENT STRUCTURE (exact LOLC format — 12 sections)

*Verified against four real LOLC files at the raw XML level, cross-checked against each other:
Transaction Reversal – Interest Rollback URS V1.0 (most authoritative — furthest toward sign-off),
the blank XX-Module and Master org templates, and the Lending Module V0.1 draft. Facts here are
kept only where at least two of the four agree; forks between sources are called out explicitly
in `references/urs-format.md` rather than silently resolved.*
*See `references/urs-format.md` for full format detail, table layouts, and writing rules.*

---

### COVER PAGE

```
Proprietary and Confidential                                    [LOLC logo, top-right]

[Module Name] – [Feature Title]

User Story Document

User Story for [Full Feature Name]

| Document Version | 1.0        |
| Release Date     | DD/MM/YYYY |
| Number of Pages  | [n]        |

LOLC Technologies
137, Rajagiriya Road, Rajagiriya. 10100
```

---

### TABLE OF CONTENTS

```
[Module Name] – [Feature Title]................................................1
Table of Content.................................................................2
List of Figures...................................................................2
List of Tables....................................................................2
1.    Document Control............................................................3
1.1.  Document Information........................................................3
1.2.  Revision History............................................................3
1.3.  Definitions and Acronyms....................................................3
1.4.  Assumptions.................................................................3
1.5.  Risks.......................................................................3
1.6.  General Guide Line..........................................................3
2.    Open Questions..............................................................4
3.    Overview/Project Description................................................4
4.    Flow Chart..................................................................4
5.    Scope.......................................................................5
5.1.  What is in scope............................................................5
5.2.  What is out of scope........................................................5
6.    Epic: Narrative and Statement................................................5
7.    Features/Stories............................................................5
7.1.  Story 01 ([Story Title])....................................................5
7.2.  Story 02 ([Story Title], if applicable).....................................6
7.   Data Dictionary..............................................................7
8.   E2E Impact Identification Table..............................................8
9.   Diagrams and Examples........................................................9
10.  Annexure......................................................................9
11.  Test Scenarios................................................................9
```

**Note on the duplicate "7.":** the real samples number the body section after Features/Stories
with the *same number* Features/Stories itself has, not the next integer — this is a real,
mechanical restart in the source template's own numbering definitions (a second multilevel list
whose start value is set to match), not a typo, and not something to "fix" to 8, 9, 10...
**The duplicated digit is not always 7** — it equals whatever number Features/Stories actually
landed on in the document being generated, which depends on whether the Flow Chart section
(below) is included as its own heading. In the layout above (Flow Chart present as section 4),
Features/Stories is 7, so Data Dictionary duplicates "7." — but a real sample that skipped the
standalone Flow Chart heading had Features/Stories at 6, and Data Dictionary correctly duplicated
"6." instead. Count the actual preceding sections in the document you're generating and match
Features/Stories' real number — don't hardcode 7.

**Note on Flow Chart (section 4):** confirmed present as its own heading in the blank org
templates and in a V1.0 sample — keep it as a standalone section by default. One real V0.1 draft
skipped the heading entirely and embedded the flow chart figure/caption directly under Overview
instead; treat that as an acceptable variant only when the feature genuinely has no
decision/process flow worth a dedicated section, not the default.

**Immediately follows the ToC, before Section 1:**
```
List of Figures
Figure 1 - Flowchart...........................................................[page]
[Figure 2, 3... if additional diagrams are included]

List of Tables
Table 1 - Data Dictionary.......................................................[page]
Table 2 - E2E Impact Identification.............................................[page]
```

---

### SECTION 1 — Document Control

#### 1.1 Document Information
| Drafted By | [name] |
|---|---|
| Reviewed By | [name, or blank if not yet reviewed] |
| Document Status | Draft |
| Client Name | LOLC Technologies Pvt LTD |
| Circulation | Internal |

#### 1.2 Revision History
| Revision Date | Updated By | Version | Section(s) | Description |
|---|---|---|---|---|
| YYYY-MM-DD | [name] | 0.1 | All | Initial Draft |
| | | | | |

#### 1.3 Definitions and Acronyms
Simple 2-column table — acronym | definition. Include only those relevant to the scope.

Always include:
- URS — User Requirement Specification
- UI — User Interface
- CBS — Core Banking System
- FusionX — Core Banking Platform by LOLC Technologies

Add module-specific acronyms from the loaded reference file (e.g., DPD, GL, EOD, KYC, PEP, TD, CASA).

For Open Banking URS, include relevant OBIE acronyms from `references/open-banking.md`:
OBIE, OB, API, AISP, PISP, TPP, PCA, BCA, SME, MMC, AER, EAR, APR, RepAPR, MIG, JSON, REST, CMA9,
CMA, FCA, DCR, FAPI, TierBandMethod, DepositInterestAppliedCoverage, MarketingState, PredecessorID,
OverdraftType, RepaymentType, x-fapi-auth-date, x-fapi-interaction-id, x-fapi-customer-ip-address

#### 1.4 Assumptions
Bullet list of complete sentences. Be specific to the feature scope.
Module-specific defaults from reference files apply. Additional feature-specific assumptions beyond defaults:
- Lending: active account required; maker-checker enforced; settings layer pre-configured
- CASA: account Active/verified; teller limits configured; dual auth for high-value
- COB: KYC/AML validation passes before downstream module use
- Cash & Teller: till open; vault balance sufficient; teller limits configured
- TD: product/sub-product configured; interest templates active
- Common Settings: downstream modules pick up changes at next processing cycle

Ground each assumption in something — the scope statement, the module reference file, or existing
system behavior — rather than asserting it as if self-evidently true (adapted from
`evidence-gap-review`). If an assumption is really just a guess with nothing behind it, either
verify it in STEP 1.5 or state it as a guess explicitly rather than dressing it up as settled fact.

#### 1.5 Risks
Bullet list. Each risk is a specific sentence about what could go wrong.
Always consider: guideline change risk, data quality risk, upstream dependency risk, timeline risk, integration risk.

Where useful, categorize by what kind of boundary the risk sits against — technical, regulatory/
compliance, organizational (process/people), financial, timeline, or integration/upstream-
dependency (adapted from `constraint-detector`) — this makes it obvious to a reviewer which risks
are actually the same class of exposure repeated, versus genuinely distinct concerns.

#### 1.6 General Guide Line

This is a 3-column table that states the non-negotiable system behaviours the feature must
respect — generally the things that *must not* break as a side effect of the enhancement. It is
distinct from Assumptions (what's already true) and Risks (what could go wrong): General Guide
Line states ground rules the implementation is bound by.

| Category | Guideline / Comment | Applicability / Notes |
|---|---|---|
| [Category name] | [The rule, stated as a system behaviour] | Mandatory |
| [Category name] | [The rule, stated as a system behaviour] | Mandatory |

**Confirmed defect to avoid:** a real V0.1 draft left the org template's generic 7-row
placeholder (Data Management, Search, Input Validation, Workflow & Approvals, Audit &
Traceability, Reporting & Dashboards, Consistency & Usability) completely unedited. Never do
this — always write rows specific to the feature.

Typical categories: existing functionality preservation, effective-date control, master data
validation, range/boundary validation, calendar/month-end integrity, frequency handling,
financial/historical data integrity, validation messaging, audit & traceability, security &
authorization, EOD/batch alignment, cross-UI consistency. Generate one row per category that's
actually relevant to the feature — don't pad with categories that don't apply.

---

### SECTION 2 — Open Questions
| # | Date | Question | Owner | Status |
|---|---|---|---|---|
| | | | | |

Leave blank rows if no open questions at time of drafting.

---

### SECTION 3 — Overview/Project Description
2–4 sentences covering:
1. What the feature is and which module it belongs to
2. What data it processes or what workflow it enables
3. What it produces/outputs
4. Business value (compliance, efficiency, accuracy, risk reduction)

This is the URS's problem statement — point 4 should name what's actually wrong or missing today
that this closes (adapted from `problem-statement-refiner`), not just assert a generic virtue.
"Reduces manual reconciliation effort" is a claim; "eliminates the manual reconciliation step
currently required after every reversal" is the same claim tied to something concrete happening
today. Prefer the latter.

---

### SECTION 4 — Flow Chart

Generate an actual flowchart image, not a placeholder, whenever the feature has a clear decision
or process flow (most enhancements do). Use the Visualizer (`diagram` module) to produce it, save
it as an image, and embed it in the .docx under a centered italic caption (style `Caption`, `44546A`, 9pt — not bold):

```
Figure 1 - Flowchart
```

Only fall back to `[Flow chart to be attached]` if the feature genuinely has no meaningful
process flow to diagram (rare — flag this to the user rather than assuming it).

---

### SECTION 5 — Scope

#### 5.1 What is in scope
Bullet list. Start each item with an action noun:
"Generation of...", "Capture and maintenance of...", "Validation of...", "Monthly processing of...", "Manual execution of..."

#### 5.2 What is out of scope
Bullet list. Explicitly state what is excluded to prevent scope creep.

---

### SECTION 6 — Epic: Narrative and Statement
| [Module Name] – [Feature Title] | |
|---|---|
| Who | As a [Role] |
| Needs | [What capability, stated tersely — not a full sentence in the samples] |
| Product | [System / Module Name in FusionX] |
| ROI | [Business value: regulatory compliance, reduced manual effort, data quality, operational efficiency] |

ROI is a benefit hypothesis, not a slogan (adapted from `benefit-hypothesis-writer`) — where the
scope statement gives you enough to say what specifically changes ("fewer full appraisal
restarts," "eliminates the manual reconciliation step"), say that instead of a generic category
word like "efficiency." If the scope statement genuinely doesn't support a more specific claim
than the generic category, use the generic category rather than inventing false precision.

---

### SECTION 7 — Features / Stories

Generate one story per distinct user action or workflow step. Minimum 2 stories; typical range 3–6.
Sub-section heading format: `7.1.  Story 01 – [Story Title]`, `7.2.  Story 02 – [Story Title]`, etc.

**How to think through each story before writing its table — this is where the actual BA
reasoning happens, not just in the before/after gates.** STEP 1.5 pressure-tests the scope
statement; the cognitive quality pass in STEP 2 audits the finished draft; neither one thinks
*through* a story while it's being constructed, and that's the part that most determines whether
a story is actually well-reasoned or just correctly formatted. For each story, before filling in
the table, work through this sequence — in your head, not as a separate visible artifact:

1. **What's the real trigger, and who initiates it?** Not just "user clicks a button" — which
   role, under what circumstance, arriving from where.
2. **What has to already be true for this to make sense?** (feeds Pre-Conditions) — if you can't
   name at least one precondition, you probably don't understand the story well enough yet.
3. **What are *all* the rules governing whether this succeeds** — not just the one rule the scope
   statement mentioned. A rule about who can act usually implies a rule about who can't; a rule
   about a happy path usually implies a rule about what happens when it isn't. This is the same
   question the Action-cell guidance below asks, but ask it *while drafting*, not as a later check
   against what you already wrote.
4. **What happens on every way this could fail or be rejected**, not only the success path.
5. **What does the system actually produce or change as a result** (feeds Result) — concretely
   enough that someone could check whether it happened.
6. **How would you prove this worked?** If you can't describe a way to verify it, the Expected row
   is going to end up vague, and it'll surface in the cognitive pass's ambiguity check anyway — better
   to notice now, while you still have full context on the story, than after.

This isn't a checklist to run through mechanically and forget — it's the difference between a
story that reads as "correctly filled in" and one that reads as "someone actually thought about
this." If a story comes out thin after this sequence, that's a signal to go back to STEP 1.5 and
ask the user, not to pad the table with plausible-sounding filler to make it look complete.

**Reflection — before moving to the next story, ask once more:** *Critic: did I just assume who's
allowed to do this, or did I actually establish it?* *Critic: is there a failure path I wrote as
"existing validation applies" because I didn't actually work out what that validation is?* If
either exposes a soft spot, fix it now, with full context on this one story — the STEP 2 cognitive
pass will likely catch it too, but catching it here produces a better fix than catching it later
across six stories at once.

Each story uses a 2-column table with exactly these 6 rows, **all 6 numbered — confirmed
independently by all three real sources (Master Template, Lending, Transaction Reversal), not
just the template — and every number here, on every row, must be real Word numbering, never typed
digits, no exceptions:**

```
1.  7.1.1. User & Function  |  7.1.1.1  [Login/role context.]
                                Navigation path on its own line, color 002060, not bold, → in Arial:
                                Fusion X → Home → [Module] → [Sub-module] → [Screen]
                                [Note: New Screen / modification to existing screen.]
------------------------------|--------------------------------------------------------------
    7.1.2. Action             |  7.1.2.1  [Numbered sub-points via real numPr list numbering —
                                  renders as 7.1.2.1., 7.1.2.2., ... Bold inline sub-headers like
                                  "Current Process" / "New System Behavior" / "Example Scenario"
                                  when the content has natural sections. Cover every field
                                  touched, every Mandatory/Optional/Conditional designation,
                                  every validation rule, every sub-condition by type/status, file
                                  naming conventions with a real example, integration rules with
                                  other modules. This is the most detailed cell in the whole
                                  document — do not summarise. Almost always more than one point.]
------------------------------|--------------------------------------------------------------
    7.1.3. Result             |  7.1.3.1  [At least one numbered point: what was created/changed/posted.]
------------------------------|--------------------------------------------------------------
    7.1.4. Pre-Conditions     |  7.1.4.1  [At least one numbered point: what must already be true.]
------------------------------|--------------------------------------------------------------
    7.1.5. Trigger            |  7.1.5.1  [Button click (name it), or "System-triggered, chained
                                  immediately after Story [X.Y.Z]" for an automated trigger.]
------------------------------|--------------------------------------------------------------
    7.1.6. Expected           |  7.1.6.1  [One numbered bullet per distinct output, each as
                                  "Label — what it is": e.g. "Corrected Accrual Ledger — per
                                  impacted interest type." Not a single consolidated sentence.]
```

**Numbering mechanism — this is the fix for reported "auto numbering defects, indentation"
issues:** every row label (User & Function through Expected) carries a real number, incrementing
1→6 in document order, and every row's content column carries at least one real numbered point
one level deeper (auto-resetting to `.1` each time the row label advances) — this was corrected
from an earlier, narrower version of this skill that only numbered the first row, based on
checking visible text rather than actual `numPr` presence in the two real generated samples;
checking `numPr` directly shows all three real sources (Master Template, Lending, Transaction
Reversal) agree all 6 rows are numbered — the earlier rule undercounted what was already there,
it wasn't a template-vs-practice tradeoff. Nothing here is ever typed digit text: row labels are
`numbering: { reference, level: 2 }`, content points are `level: 3`, both on one 4-level list per
story (level 0 = section, level 1 = story, level 2 = row 1–6, level 3 = content point) — reusing
the section-heading list one level deeper is the simplest option and is confirmed working on all
6 rows in both real generated documents; a dedicated per-story list with level 0/1 `start`
hardcoded to that story's actual section/story number is more robust for a generator. Typing
digits can't reproduce Word's own hanging-indent math and doesn't renumber
when a point is added/removed/reordered — that mismatch is almost certainly the cause of drift
reported in past output. See DOCX FORMATTING / `references/docx-formatting.md` for the exact
list-definition recipe.

The leading `1.` / `2.` / `3.`... in front of "User & Function" in the left column is a
document-level counter that increments once per story (i.e. story 2's "User & Function" row
starts with `2.`) — independent of the 7.x.x section numbering.

**Action cell content — what goes in it, not just how it's numbered:**
- **Write each rule as a complete, testable sentence, not a fragment** (adapted from
  `olbboy/BA-Kit`'s requirement-sentence pattern): `[If <condition/restriction>,] <subject>
  <shall/must> <action> [producing <observable result>] [subject to <qualifier>]`. E.g. "If the
  requester is not an Approval Officer, the system shall reject the Request Change action and
  display [message]" — not "Only Approval Officers can request a change." The template forces the
  implicit half of the rule (what happens otherwise) into the sentence itself instead of leaving it
  for the reader to infer, which is exactly what the next bullet also demands — use them together.
- **Extract implicit rules, not just what's explicitly stated** (adapted from
  `business-rule-extractor`). A scope statement that says "only Approval Officers can request a
  change" implies a rule about what happens if anyone else tries — write that rule down even
  though the scope statement never said the word "reject." The implicit half of a business rule
  is usually the half that gets missed.
- **Cover the exception flow, not just the success flow** (adapted from
  `use-case-specification`). Action almost always describes what happens when the input is valid
  and the actor is authorized — also cover what the system does when it isn't: invalid input,
  unauthorized actor, precondition not met. If that path is genuinely identical to another story's
  existing behavior, say so explicitly ("existing validation applies unchanged") rather than
  leaving it unaddressed.
- **Action is functional behavior; General Guide Line (1.6) is everything else** (adapted from
  `functional-vs-nonfunctional-splitter`). If a rule describes what the system *does* in response
  to this specific trigger, it belongs in Action. If it describes a quality the system must always
  have regardless of this specific feature (consistent sorting, audit logging on every
  create/update, standard validation messaging), it belongs in General Guide Line, not repeated
  inline in every story's Action cell.

---

### SECTION "7" (second one) — Data Dictionary

```
Table 1 - Data Dictionary
```

8-column table. **Column headers exactly:**
`Feature | Field Name | Data Type | Source / Retrieve From | Constraint / Description | Sample Data | Data Validation | Max Length`

| Feature | Field Name | Data Type | Source / Retrieve From | Constraint / Description | Sample Data | Data Validation | Max Length |
|---|---|---|---|---|---|---|---|
| [Feature/screen grouping] | [Field name] | [Alphanumeric / Numeric / Date / Dropdown / Boolean] | [System Generated / User Input / Master Data / Product Setup / System Derived / System Calculated / System Stored] | [What the field represents] | [A realistic example value] | [Mandatory / Optional / Mandatory, Read-only / Mandatory, Cannot be blank / specific rule] | [Number, or N/A for dropdowns/booleans] |

This is a different (newer, richer) format from the old 3-column "Field Name / M/O/C /
Description" table — use this 8-column version. Group rows by Feature so related fields sit
together (e.g. all "Due Date Template" fields, then all "Due Date Configuration" fields, then
"Audit" fields last).

Add a field-reference footnote after the table if applicable:
`Field reference: [source document / guideline name / Jira / SharePoint link if applicable]`

For Open Banking URS, use OBIE-aligned field names from `references/open-banking.md`:
- Interest: `AER`, `BankInterestRate`, `BankInterestRateType`, `RepAPR`, `CalculationFrequency`, `ApplicationFrequency`
- Tiers: `TierValueMinimum`, `TierValueMaximum`, `TierBandMethod` (Whole/Tiered)
- Fees: `FeeType`, `FeeAmount`, `FeeRate`, `FeeCapAmount`, `CappingPeriod`, `FeeMinMaxType`
- Repayment: `RepaymentType`, `RepaymentFrequency`, `AmountType`, `MaxHolidayLength`, `PrepaymentFee`
- Eligibility: `MinimumAge`, `ResidencyType`, `LegalStructure`, `ScoringType`, `TradingType`
- Product: `ProductName`, `ProductType`, `ProductId`, `MarketingState`, `PredecessorID`
- API envelope: `Data`, `Links.Self`, `Meta.TotalPages`
- FAPI headers: `x-fapi-auth-date`, `x-fapi-customer-ip-address`, `x-fapi-interaction-id`

---

### SECTION 8 — E2E Impact Identification Table

```
Table 2 - E2E Impact Identification
```

3-column table. **Column headers exactly:** `Area | What to Capture (BA Guidance) | Impact Description`
Header row text is centered (not left-aligned, unlike every other table in the document).

| Area | What to Capture (BA Guidance) | Impact Description |
|---|---|---|
| Primary Module | The main functional area where the change is implemented | [Module – Settings – Feature] |
| Upstream Touchpoints | Systems or channels that send data into this module | [List] |
| Downstream Touchpoints | Systems or modules that receive or are affected by the output | [List] |
| Reporting / MIS Impact | Business reports or balances that may change due to this update | [Specific reports, or "None identified" stated explicitly] |
| Batch / Scheduler Impact | Any business-known batch, EOD, or scheduled process | [Specific impact, or "None identified" stated explicitly] |
| Customer Impact | Will customers notice a change? (Yes/No + brief note) | [Specific impact, or "None directly" stated explicitly] |
| Operational Impact | Will branch or ops teams change how they work? | [Specific impact] |
| E2E Validation Required | Is end-to-end testing needed across the above areas? | [Yes/No — and what should be tested end-to-end] |

**This is an 8-row table, verified identically (same 8 Area categories) in both a V1.0 sample and
a V0.1 draft — do not use a 14-row or 15-row version.** A previous version of this skill used a
fabricated 14-row set (Repayment Schedule Engine, Loan Accounting/GL, Arrears & DPD Calculation,
Data Integrity, Audit & Compliance, Security & Authorization, Validation & Messaging, etc.) that
does not appear in any real sample. Use the module reference file's "E2E Impact Notes" section as
the factual basis for filling these 8 rows in — don't invent impacts that aren't grounded in the
reference file or the scope statement. Stating "None identified" explicitly is correct and
expected when a row genuinely doesn't apply (e.g. a screen-only feature has no Batch/Scheduler
Impact) — don't pad rows with invented impact just to fill space.

**Mapping note:** the module reference files' "E2E Impact Notes" bullets (e.g. lending.md's
"Repayment Schedule Engine", "GL / Loan Accounting", "DPD / Arrears") are domain facts to fold
into whichever of the 8 rows they belong under — usually Downstream Touchpoints or Reporting/MIS
Impact — not additional row categories in their own right. Don't recreate a row per bullet.

---

### SECTION 9 — Diagrams and Examples

Embed actual screenshots or mockups where the feature touches a specific FusionX screen, each
under a centered italic caption (style `Caption`, not bold) following the List of Figures numbering (`Figure 2 – [Screen
Name]`, continuing from the Section 4 flow chart which is Figure 1). If no screenshots are
available at draft stage, use `[Diagrams and examples to be attached]` and flag it to the user
rather than fabricating a screenshot.

---

### SECTION 10 — Annexure

```
10.1  Common Guide for FusionX
[Module Epic JQL link from reference file, or the Jira ticket URL if provided]
https://miro.com/app/board/uXjVPOGFdEE=/  [Miro flow diagrams — FusionX, if relevant]
```

---

### SECTION 11 — Test Scenarios

Generate 6–12 testable scenarios as a bullet list, each in `[scenario] → [expected outcome]` form.
At V0.1 draft this may be left as `[Test scenarios to be defined]` if the user prefers to defer it.

Before picking which scenarios to include, work through these 7 categories (adapted from
`olbboy/BA-Kit`'s test-design system) against the actual fields and rules just drafted in Section
7 — not generic placeholders. Not every category applies to every feature, but check all 7 before
deciding to skip one; state "Not applicable" for a skipped category rather than omitting it
silently if its absence would otherwise look like an oversight:

1. **Happy path** — the normal flow succeeds as specified.
2. **Edge case (boundary values)** — for every numeric/date/length limit in the Data Dictionary's
   Data Validation column, test one value below, at, and above the boundary (e.g. a 30-day cap:
   29, 30, 31 days).
3. **Error case** — invalid or malformed input, missing required field, precondition not met.
4. **Security/authorization case** — an actor without the required role attempts the action.
5. **Concurrency case** — two users acting on the same record at once, or a resubmission of an
   already-processed item, where the story's Action rules create that exposure.
6. **Data integrity/cross-module case** — a value that must stay consistent between this module and
   a downstream one named in Section 8's E2E Impact table.
7. **Batch/EOD timing case** — where the module reference file or E2E Impact table names a
   batch/EOD dependency.

At minimum: 1 happy-path scenario per story + 1 boundary-value scenario per numeric/date-limited
Data Dictionary field + invalid input + unauthorized user + maker-checker violation (if applicable)
+ any concurrency/data-integrity/batch scenario the check above surfaced as applicable.

---

## FUSIONX MODULE REFERENCE TABLE

All 8 modules have reference files in `<skill-root>/references/`.
**Always load the relevant file(s) before writing.**

| Module | Confluence Name | File | Jira Label |
|---|---|---|---|
| Lending ✓ | Loan Origination and Loan Management | `lending.md` | `LendingModule` |
| CASA ✓ | Accounts Module (Current Accounts & Savings Accounts) | `casa.md` | `AccountsModule` |
| COB / KYC ✓ | Customer Onboarding Module | `cob.md` | `CustomerOnBoardingModule` |
| Cash & Teller ✓ | Cash & Teller Module | `cash-teller.md` | `CashModule` |
| Term Deposit ✓ | Term Deposit Module | `term-deposit.md` | `TDModule` |
| MicroFinance ✓ | MicroFinance Module | `microfinance.md` | `RewardModule` |
| Common Settings ✓ | Common Settings Module | `common-settings.md` | `CommonModule` |
| Open Banking ✓ | Open Banking (OBIE PCA v3.1.2 + SME Loan v2.3.1) | `open-banking.md` | — |

**Modules without reference files yet** (use general conventions + flag for BA review):
Authorization Module, Yard Management, Blacklist Management, Supplier Module

---

## WRITING STANDARDS

- **"Shall"** / **"must"** for mandatory system behaviours: "System shall validate...", "The file must be generated..."
- **"Should"** for recommended behaviours
- Navigation paths: `Home → FusionX → [Module] → [Sub-module] → [Screen/Action]` — color the whole
  path `002060` (dark navy — distinct from the `2F5496` heading blue), not bold, when it appears
  inside a story's User & Function or Trigger text; the `→` glyph renders in Arial (see DOCX FORMATTING)
- Validation/confirmation messages: quoted exactly as they will appear on screen
- Field names in **bold** when referenced in prose
- Every requirement-bearing row in a story is numbered to 4 levels (e.g. 7.1.2.3.) — see Section 7
- Each individual numbered point is atomic — one behaviour per point
- Passive voice for system actions, active for user actions
- File naming conventions stated explicitly with real example:
  e.g., `CRBSIYYYYMMDDVVV.BBB` → `EX: CRBSI20260611280.014`
- Dates everywhere in the document body: DD/MM/YYYY (the cover page Release Date field also uses
  DD/MM/YYYY — this format is consistent across the whole document; there is no separate
  cover-page date format)
- M/O/C-equivalent designations (Mandatory / Optional / Conditional, stated in words, not letter
  codes) used in the Data Dictionary's Constraint/Description and Data Validation columns
- ISO standard references included where applicable

---

## VERSIONING RULES

| Version | Meaning |
|---|---|
| 0.1 | Draft Version |
| 0.2 | Reviewed with Comments |
| 0.3 | Finalized with Review Comment Controls |
| 1.0 | Final Version for Development / Client Sign-off |
| 1.x | Subsequent Updates |

---

## DOCX FORMATTING

Read `references/docx-formatting.md` for the exact fonts, sizes, colors, table styles, and column
widths to apply. Apply it exactly — don't improvise, since improvisation is exactly what caused
past output to drift in font, color, and table style from page to page. The reference file also
explains *why* the drift happened (theme font vs. explicit per-run overrides) so the same mistake
isn't repeated when generating new documents.

---

## CONTENT CHECKLIST (STEP 2.5 Pass 1 — run against the confirmed draft, before generating)

- [ ] `references/urs-format.md` loaded — section order and table formats match LOLC samples
- [ ] Module reference file(s) loaded — navigation paths and screen names exact
- [ ] For an update/change request, an independent change-impact matrix covers every affected
      occurrence across diagrams/mockups, captions, navigation, Scope, all story rows, Data
      Dictionary, E2E Impact, Test Scenarios, Open Questions, Assumptions, Risks, Annexure, and
      linked/module-reference artifacts; no stale old screen/field/role/rule name remains
- [ ] STEP 1.5 elicitation actually run before drafting, not skipped: high-risk gaps (role/permission rules, failure-path behavior, changed-vs-new-behavior, thresholds/conditions) were either asked about and answered, or explicitly deferred to Open Questions with the user's sign-off — not silently assumed; and whether the screen exists live/stable was actually resolved (walked through if yes, or navigation paths explicitly marked `[not yet verified against a live screen]` if no) — not left implicit
- [ ] Cognitive quality pass (STEP 2, all 8 checks) actually run as a self-critique, not a silent tally: no forbidden-word ambiguity (adequate/appropriate/easy/efficient/fast/flexible/intuitive/optimal/quick/reasonable/robust/seamless/simple/sufficient/timely/user-friendly/TBD/etc.) left unresolved in Action/Trigger/General Guide Line without a defined threshold or stated backing; every rule's implied dependency is either stated or listed in Assumptions; Test Scenarios cover all 7 categories from Section 11 (or explicitly mark inapplicable ones), not just happy-path-plus-one-error; no unflagged contradiction between Assumptions/Risks/Scope/Action; no orphaned Data Dictionary field an Action rule never references; no unfounded absolute/certainty language in Assumptions or Risks; the same role/actor/field/status name used identically across every story, the Data Dictionary, and E2E Impact; every in-scope item traces to a story, every story traces to a Data Dictionary field group, every field traces to a Test Scenario or is explicitly non-testable
- [ ] STEP 1 intake fields actually landed in the document: Drafted By/Reviewed By in 1.1 Document
      Information, Version in cover page + 1.2 Revision History (same value in both), Release Date
      on cover page, Jira ticket in Annexure — not left as intake answers that never got used
- [ ] Table of Contents, List of Figures, and List of Tables are all present and populated (not
      just headings) — captions match what's actually in the body (Figure N / Table N numbers
      line up with what's embedded)
- [ ] Cover page uses 137, Rajagiriya Road, Rajagiriya. 10100 address and DD/MM/YYYY date format;
      title/subtitle/sub-subtitle lines all present ("[Module] – [Feature]" / "User Story
      Document" / "User Story for [Feature]")
- [ ] 1.1 Document Information has all 5 fields (Drafted By, Reviewed By, Document Status, Client
      Name "LOLC Technologies Pvt LTD", Circulation); 1.2 Revision History populated with
      YYYY-MM-DD date (not DD/MM/YYYY); 1.3 Definitions and Acronyms present (table, or "N/A" only
      if genuinely zero relevant acronyms — always include URS/UI/CBS/FusionX plus module-specific
      ones from the reference file)
- [ ] All 12 sections present in correct order, including the duplicate number before Data Dictionary (intentional, matches Features/Stories' actual number — see Table of Contents note; not always "7.")
- [ ] Section 1.4 Assumptions and 1.5 Risks are plain bullet lists, not numbered sub-points — populated, not blank, and feature-specific (not generic risk boilerplate)
- [ ] Section 1.6 General Guide Line table present, Category | Guideline/Comment | Applicability/Notes columns, and rows are **feature-specific** — not the unedited generic 7-row template placeholder (Data Management/Search/Input Validation/Workflow & Approvals/Audit & Traceability/Reporting & Dashboards/Consistency & Usability copied verbatim is a real, confirmed draft-stage defect, not acceptable content)
- [ ] Section 2 Open Questions table present (even if empty)
- [ ] Section 3 Overview covers all 4 required points (what it is/module, what it processes,
      what it produces, business value) in 2-4 sentences
- [ ] Section 4 Flow Chart: either a real generated diagram embedded, or an explicit
      `[Flow chart to be attached]` flagged to the user with the reason — not silently skipped;
      decide (and note the decision) whether Flow Chart is a standalone heading or embedded
      inline per the Section 4 variance note
- [ ] Section 5 Scope: both What is in scope and What is out of scope populated with specific,
      non-overlapping bullets (in-scope items start with an action noun; out-of-scope items are
      explicit exclusions, not restatements of in-scope)
- [ ] Section 6 Epic table uses Who/Needs/Product/ROI format
- [ ] Every story has all 6 rows (User & Function, Action, Result, Pre-Conditions, Trigger, Expected); **all 6** row labels carry a real number (`7.1.1.` through `7.1.6.`, incrementing in document order) via real `numPr` at level 2 — never typed text; every row's content column carries at least one real numbered point at level 3 (Action typically has several; Result/Pre-Conditions/Trigger/Expected often just one)
- [ ] Action row is comprehensive — includes all field specs, mandatory/optional/conditional rules, validation rules, business rules — and uses bold inline sub-headers (e.g. "Current Process"/"New System Behavior") where the content has natural sections
- [ ] Expected row is one bullet per distinct output as "Label — description" — not a single consolidated sentence and not padded into an artificial Output/Description table
- [ ] Data Dictionary uses the 8-column format, grouped by Feature: Feature | Field Name | Data Type | Source/Retrieve From | Constraint/Description | Sample Data | Data Validation | Max Length
- [ ] E2E Impact Identification Table present with 3 columns, centered header row, and exactly the validated 8-row Area set (Primary Module, Upstream Touchpoints, Downstream Touchpoints, Reporting/MIS Impact, Batch/Scheduler Impact, Customer Impact, Operational Impact, E2E Validation Required) — not a 14-row invented list
- [ ] Settings dropdown fields cross-referenced to exact settings screen path from reference file
- [ ] E2E impacts grounded in the module reference file's "E2E Impact Notes" — not invented
- [ ] Section 9 Diagrams and Examples: figure captions continue numbering from Section 4's Figure
      1 (i.e. start at Figure 2), or `[Diagrams and examples to be attached]` is flagged explicitly
- [ ] Annexure includes Common Guide + Jira link (+ Miro board link if relevant)
- [ ] Section 11 Test Scenarios: 6-12 scenarios in `[scenario] → [expected outcome]` form; all 7
      categories (happy path, boundary/edge, error, security/authorization, concurrency, data
      integrity/cross-module, batch/EOD) checked against the actual drafted fields and rules, with
      each inapplicable category stated as such rather than silently omitted; at minimum 1
      boundary-value scenario per numeric/date-limited Data Dictionary field — or explicitly
      deferred with `[Test scenarios to be defined]`, not silently thin
- [ ] Navigation paths follow `Fusion X → Home → [Module] → [Sub-module] → [Action]` format
- [ ] Writing Standards spot-check: "shall"/"must" used for mandatory behaviours (not "will" or
      "should" where the behaviour is actually mandatory); validation/confirmation messages are
      quoted exactly, not paraphrased; field names bolded in prose
- [ ] Assigned Version (e.g. "0.1") matches its meaning in VERSIONING RULES (0.1 = Draft, 1.0 =
      Final/Sign-off, etc.) and Document Status in 1.1 agrees with it (e.g. Version 0.1 →
      Document Status "Draft")
- [ ] No section left entirely blank — use `[TO BE CONFIRMED]` or `[To be attached]` if needed

## FORMATTING CHECKLIST (STEP 2.5 Pass 2 — run against the generated .docx, before presenting)

- [ ] **Change-impact rendering check:** for update/change requests, inspect the rendered DOCX pages
      and every embedded flow diagram/mockup/screenshot to confirm changed screen, field, role, and
      rule names match the corrected text everywhere; any stale visible label or caption is a FAIL.

- [ ] **Font check (script-verified, not eyeballed):** run `check_fonts()` from `references/docx-formatting.md` against the generated file. Two passes: (1) every heading, table header, and body run must explicitly carry Candara (or Arial for `→` glyphs), none left to inherit from theme defaults (this is the #1 cause of inconsistent-looking output; see "Why past output drifted"); (2) every list level actually used via `numPr` must have its own explicit Candara in `numbering.xml`'s `<w:lvl><w:rPr><w:rFonts>` — the rendered number glyph is synthesized from this, not from any run in `document.xml`, so pass (1) alone can hit 100% while every number still renders in theme Calibri (confirmed as a real gap — even the reference file has it at several levels). This is exactly the checklist item that was previously eyeball-only and let a font mismatch through — a `PASS` requires the script's output, not a read-through.
- [ ] **Number-to-text gap (manual — no script can check this; compare siblings, not one item):** the space between a rendered number and its following text (e.g. `7.1.` then a gap then `Story 01`, not `7.1.Story 01`) is a rendering/layout property, not something inspectable from the XML tree. **Default recipe (matches all three real sources exactly, verified at the raw XML level): `suffix: LevelSuffix.TAB` plus the list level's own `indent: { left, hanging }` — no literal space/tab character in the text run.** This produces the wide, hanging-indent-aligned gap real samples have, and correct wrap-alignment for continuation lines. Compare at least two sibling numbered/bulleted items at the same level side by side to confirm the gap is present and consistent, not just check one. **Only if this specific generation pipeline includes a Word-COM-automation Save round-trip that's confirmed to strip paragraph-level `w:tabs`/`w:ind`** (a narrower, secondary failure mode — see `docx-formatting.md`), fall back to `suffix: LevelSuffix.NOTHING` + a literal two-space `TextRun`; treat that as a defensive exception for a known-broken pipeline, not the default, since it produces a visibly narrower gap than the real samples. Applies to headings, story row labels, story content points, and bullets alike.
- [ ] **Table style check (script-verified, not eyeballed):** run `check_table_styles()` from `references/docx-formatting.md` — **every** table must reference a named `tblStyle`, no exceptions; manual `tblBorders` alone renders visible borders but silently loses the style's own default cell margins (confirmed real defect: numbered content sat flush against the cell border with no padding, only caught by a user screenshot, not by any prior check). Revision History, Open Questions, Data Dictionary, E2E Impact use `GridTable4-Accent3` (dark grey `A5A5A5` fill, bold white text); **every other table — including the cover table, Document Information, Definitions & Acronyms, General Guide Line, story tables, and the Epic table — uses `TableGrid`, not `PlainTable1`** (corrected; an earlier version of this line was wrong and went uncorrected for several rounds). Manual `D5DCE4` shading is layered on top of `TableGrid` for the cover-table label column, Document Information label column, General Guide Line header row, and the Epic table's merged title row specifically — fill never appears on a value/body cell, and never as a full-table style. Also run `check_no_cell_margins()` — no table cell anywhere may have an explicit `tcMar`/`margins` override; this was a confirmed real cause of ~2.4x row-height inflation.
- [ ] **Cell padding is actually resolving, not just structurally absent of overrides (script-verified is NOT enough here):** `check_no_cell_margins()` passing only proves no *explicit* `tcMar`/`tblCellMar` override exists — it cannot detect that the *implicit* default padding isn't being inherited at all, which is a real, separate, confirmed defect class (padding measured at 0pt in a generated file vs. 5.4pt real, via direct Word-COM `Cell.LeftPadding`/`RightPadding` queries, with `check_no_cell_margins()` passing the entire time). `postprocess.py`/`postprocess_template.py` (in this skill's `scripts/` folder) must inject `TableNormal`'s own definition (the actual source of the real 5.4pt/108-twip default, via its `tblCellMar` — nothing inherits real padding without this present) plus `GridTable4-Accent3`'s own explicit `tblCellMar` override (that style's inheritance through `TableNormal` does not reliably resolve even when `TableNormal` is present and correct — root mechanism not fully understood, treat as a confirmed necessary fix regardless). If Word is available, verify with an actual COM query — `Cell.LeftPadding`/`Cell.RightPadding` on the first cell of every distinct table style used in the document — not just by eyeballing a screenshot or trusting the mechanical checks; see docx-formatting.md's "Real cell padding requires injecting TableNormal" section for the full methodology and why PDF-position inference is unreliable for this specific question.
- [ ] **Numbering check (script-verified, not eyeballed — covers every numbering context, no exceptions):** run `check_numbering()` (story sub-points **and all 6 row labels** User & Function through Expected — this check has no carve-out for any of them; every one must be real `numPr` continuing the story's list at level 2, and every row's content column at least one point at level 3, same as everything else), `check_heading_numbering()` (section headings/sub-headings), `check_bullets()` (Assumptions/Risks/Scope/Test Scenarios), and `check_second_list_start()` (Data-Dictionary-onward restart value matches Features/Stories' actual number, not a hardcoded 7) from `references/docx-formatting.md` against the generated file; all four `PASS` outputs are required — a visual read of any number is not sufficient evidence, since typed digits and real `numPr` numbering render identically at a glance.
- [ ] **Numbering-gap check (script-verified — the mechanism producing the number-to-text spacing, separate from whether the number exists):** run `check_numbering_gap()` from `references/docx-formatting.md` against the generated file. `PASS` requires every used list level to have `suff="tab"` (not `"nothing"`, unless explicitly marked `[EXCEPTION: confirmed Word-COM-Save pipeline]`), and no numbered paragraph with a literal leading space/tab typed into its text. Confirmed on a real generated file that a session can report the numbering check as passing while this specific mechanism is still broken — don't skip this as redundant with `check_numbering()`, they check different things.
- [ ] **Front-matter check (script-verified, not eyeballed):** run `check_front_matter()` from `references/docx-formatting.md` against the generated file. Table of Contents, List of Figures, and List of Tables must all be real Word `TOC` fields (updatable), not typed dot-leader text; List of Tables must be present (a real draft omitted it — confirmed defect, not acceptable); none of these 3 headings carry `numPr` (confirmed reported defect: "Table of Content" rendered as a numbered `1.1.` sub-heading under Document Control instead of sitting unnumbered before it) and Section 1's first heading does carry `numPr`; entries must be plain-colored, not blue/underlined `Hyperlink` styling — a real `TOC` field defaults to blue automatically (confirmed in every real sample), so this requires an explicit override (color `000000`, no underline), not just skipping a style; a `FAIL` here (a user reported exactly this — generated ToC came out blue unintentionally) means the override didn't actually get applied; empty-paragraph counts must match the exact shape confirmed across three real files — 0 between Table of Content and List of Figures, 1 trailing List of Figures' entries, 2 trailing List of Tables' entries — not a range, an exact count
- [ ] **ToC field live-state and real page numbers (script-verified, both required, neither optional):** run `check_toc_field_live()` — no leftover `<w:sdt>` content-control wrapper, no stale `w:dirty="true"`, balanced `fldChar` begin/end counts (explicit, repeated user requirement: the ToC/LoF/LoT must stay genuinely live — right-click > Update Field works after future edits — not stripped to static text; see docx-formatting.md's "must be genuine, live, updatable Word fields" section). Then run `check_toc_page_numbers_real()` — every entry must NOT show the identical page number; if it does, the required second generation phase (`get_page_numbers.ps1` + `patch_page_numbers.py`, this skill's `scripts/` folder, a read-only Word-COM pass) was skipped and must be run before presenting the file. Both checks are new and narrow (added after this exact mechanism took many rounds to get right once already) — don't treat either as redundant with `check_front_matter()`, which checks different things.
- [ ] **Section-transition spacing check (script-verified, not eyeballed):** run `check_section_transitions()` from `references/docx-formatting.md` against the generated file — every heading that follows a table or a bullet list (Assumptions/Risks/Scope/Test Scenarios) must have exactly 1 empty paragraph before it; every other heading must have exactly 0. Also run `check_body_spacing()` as a coarser safety net for any 2+ stacked empty paragraphs elsewhere. Then manually verify the exact-adjacency rules no script can check: 0 empty paragraphs between a heading and its table, between a table's caption and the table, between an embedded image and its caption, and between one figure's caption and the next figure's image; multi-paragraph table cells (e.g. story Action cells) explicitly set `after=120`/`line=276 auto` rather than inheriting the looser docDefaults spacing
- [ ] **Document-level default spacing check (script-verified — root cause of a confirmed ~2.4x row-height regression):** run `check_no_docdefault_paragraph_spacing()` — `styles.xml`'s `w:docDefaults/w:pPrDefault` must be empty/absent. Setting a spacing there (even once, to fix an unrelated cover-page gap) cascades into every table cell paragraph without its own protective style and silently inflates row height across the whole document — invisible to every other structural check, only caught previously by pixel-measuring an actual Word rendering. Any paragraph that genuinely needs specific spacing (e.g. a spacer `blank()` paragraph) must have it set directly on that paragraph, never at the document-default level.
- [ ] **Bullet check:** covered by `check_bullets()` above (script-verified) — Assumptions, Risks, Scope in/out-of-scope, and Test Scenarios are real bullet-list `numPr` formatting, not decimal sub-numbers and not typed dashes/bullets
- [ ] **Column width check:** no table header word wraps onto two lines; Data Dictionary and E2E Impact tables use the proportions specified in DOCX FORMATTING, not even/default column widths
- [ ] **Color check (script-verified for cover title + headings, manual for the rest):** run `check_colors()` from `references/docx-formatting.md` against the generated file — cover title must use `0070C0`, every numbered section heading must use `2F5496` (run-level or via its paragraph style's own default color — either is fine). Then manually verify what the script doesn't yet cover: navigation paths inside story text use `002060` and are **not** bold; the `→` glyph renders in Arial; captions use `44546A` italic (not bold) — four distinct, non-interchangeable values, not one "accent blue"
- [ ] **Heading indent check (script-verified, not eyeballed):** run `check_heading_indent_progression()` from `references/docx-formatting.md` — every numbering list used on Heading1/Heading2 paragraphs must indent level 1's number glyph further right than level 0's (`left - hanging` must strictly increase per level). A config with `hanging == left` at every level makes every heading number start at position 0 regardless of level — "1." and "1.1." both flush left — which rendered borders/fonts/colors all still pass while looking visibly wrong; this was previously only caught by a user screenshot comparison, not any script. Does not apply to table-cell-content numbering levels (story row labels, numbered sub-points), which genuinely use `left == hanging` in every real file — don't "fix" those to match.
- [ ] **Page/header/footer check:** page size is A4 (not Letter); header logo is a plain **inline** image in its own right-aligned paragraph (not floating/anchored — a floating image there was the direct cause of two separate hard-open-failure bugs); footer is **two stacked paragraphs, not a table** — line 1 (left) is "URS " + a live `DOCPROPERTY Title` field (not `FILENAME` — the real footer shows a human document title, not the `.docx` filename), line 2 (right-aligned) is "Page " + live `PAGE`/`NUMPAGES` fields
- [ ] **Divider row check:** the Epic table's title row (e.g. "Lending Module") is merged across every column and bold. Data Dictionary does **not** use divider rows in the target 8-column format — group by repeating the Feature value in each row instead (confirmed from the V1.0 sample); don't add merged story/feature-divider rows there
- [ ] **Hex ID check (script-verified, not eyeballed — mandatory whenever new paragraphs/images were hand-spliced into an existing real `.docx` via raw XML rather than generated fresh):** run `check_hex_ids()` from `references/docx-formatting.md` — every `w14:paraId`, `wp14:anchorId`, and `wp14:editId` attribute value in the generated `document.xml` must be exactly 8 hex characters (`^[0-9A-Fa-f]{8}$`). A confirmed hard-open-failure cause (same class as `rId0` and the missing `wrapPolygon` above, a different root cause): an "invented" value containing a non-hex letter (e.g. `6A1K0001`) makes Word refuse to open the file outright, with no more specific diagnostic than a generic recovery-converter prompt
