# Functional Testing — Gotchas

Operational lessons specific to this skill. FusionX UI/environment quirks
that apply to any Playwright walkthrough of this system (Ant Design
virtualized dropdowns, sticky-header click interception, slow-confirm
screens with no progress indicator) are already documented in
`../user-manual-update/gotchas.md` — read that first, this file doesn't
repeat it.

## Selector drift after a UI release

If a FusionX release changes a screen's markup, both a `DATA-LINEAGE.md`
row's remembered path and a plan step's expected selector can go stale in
the same way. When Executor, Traceability, or Verifier can't find an
element that a prior round successfully located:

- Don't conclude the feature was removed. Treat it as "possibly moved" and
  re-derive it live (search the current screen, don't assume the old
  snapshot is still accurate).
- Record what actually happened in `AUDIT-LOG.md` either way — "element
  moved from X to Y after release Z" is exactly the kind of correction that
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

## Network capture stays action-correlated

When Executor records raw network requests/responses, tag each captured
request with the specific action that triggered it (e.g. "clicked Submit
on Collateral > Add Charge") rather than dumping one undifferentiated log
for the whole session. Traceability and Verifier both depend on being able
to find "the request(s) this one action caused" without re-deriving that
mapping themselves — an uncorrelated dump pushes work downstream that
Executor was already in the best position to do at capture time.
