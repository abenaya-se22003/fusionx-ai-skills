# Functional Testing — Gotchas

## Mandatory shared browser-session contract

Before any browser interaction, read and follow:

`references/browser-session.md`

This is the canonical contract for browser launch, viewport, session reuse,
session lifecycle, and recovery. The skill-specific lessons below may add
useful context, but must not override the shared contract.

Operational lessons specific to this skill. Read
`references/browser-gotchas.md` for the bundled FusionX UI/environment
quirks that apply to any Playwright walkthrough before dispatching a role.

## Selector drift after a UI release

If a FusionX release changes a screen's markup, both a `DATA-LINEAGE.md`
row's remembered path and a plan step's expected selector can go stale in
the same way. When Executor, Traceability, or Verifier can't find an
element that a prior round successfully located:

- Don't conclude the feature was removed. Treat it as "possibly moved" and
  re-derive it live (search the current screen, don't assume the old
  snapshot is still accurate).
- Record what actually happened in `AUDIT-LOG.md` either way — "element moved from X to Y after release Z" is exactly the kind of correction that
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

## Numeric validation rules need boundary-value testing, not just one example

When a field enforces a numeric rule with a rounding, threshold, or
percentage-of-another-field component (a minimum below which the value is
rejected, a fee calculated as a percentage and rounded to the nearest
currency unit), test values at and immediately either side of the actual
boundary — not just one clearly-valid and one clearly-invalid value.
Rounding-convention differences (round-half-up vs. banker's rounding) and
off-by-one threshold bugs only surface exactly at the edge (e.g. a value
that rounds differently depending on convention, or a value one currency
unit inside vs. outside a threshold); a test plan that only exercises one
comfortably-passing and one comfortably-failing value will miss them.

## Browser-driving basics

`playwright-cli` defaults to headless (`--headed` required). Browser window
size, maximization, and resizing are deliberately left to the user; the
skill must not alter them automatically. The `attach` command reliably kills
a self-opened session, and `playwright-cli` screenshot/snapshot files save
relative to their invocation directory. The full operational details are in
`references/browser-gotchas.md` — read it before dispatching any role that
touches the browser.
The `attach` bug in particular was the single biggest blocker in this
skill's first live pilot (six consecutive Executor dispatches failed
before it was root-caused) — every dispatch prompt for Executor,
Traceability, Verifier, and Defect-Triage must use plain `playwright-cli
-s=<name> <command>` and never `attach`.

## Session lifecycle is main-thread-only — never let a dispatched role open or close the browser

Executor, Traceability, Verifier, Source-Verifier, and Defect-Triage must
never open, close, or launch any browser instance themselves — including a
"diagnostic" browser to check whether the app is reachable. If a plain
`playwright-cli -s=<name> <command>` fails or the session looks dead, the
correct response for any dispatched role is to stop immediately and report
BLOCKED to the main thread — not to retry with `attach`, not to open a
replacement browser to investigate. Only the main thread opens/closes/
re-authenticates the shared session. A role that opens its own browser to
troubleshoot can produce a second, unexpected window appearing on the
human's screen while they're in the middle of something else entirely
unrelated (observed during pilot #1) — jarring and disruptive even though
no credentials were ever at risk.

Before dispatching a role that depends on the live session, re-run
`playwright-cli list` immediately beforehand — don't trust a check from
several tool calls ago. If a dispatched role reports it can't reach the
session, the main thread should independently re-verify with its own
`list` call before concluding it needs to re-authenticate (the daemon can
die between the role's check and yours). See `references/browser-gotchas.md`
for orphaned-window and `--persistent` handling.

## Network capture stays action-correlated

When Executor records raw network requests/responses, tag each captured
request with the specific action that triggered it (e.g. "clicked Submit
on Collateral > Add Charge") rather than dumping one undifferentiated log
for the whole session. Traceability and Verifier both depend on being able
to find "the request(s) this one action caused" without re-deriving that
mapping themselves — an uncorrelated dump pushes work downstream that
Executor was already in the best position to do at capture time.
