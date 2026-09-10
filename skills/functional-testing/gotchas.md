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

## playwright-cli defaults to headless — always pass `--headed`

`playwright-cli open` launches headless by default. For any stage that
needs the human to see or interact with the browser (login, MFA, watching
the automation), the browser never actually becomes visible unless `open`
is called with `--headed`. Discovering this after the fact means the human
has been staring at nothing while the automation waited silently for a
login it can't ask for.

## Maximize the window, don't just resize the viewport

`playwright-cli resize <w> <h>` sets the page's viewport via CDP — it does
not resize or maximize the actual OS browser window itself. Left at its
default launch size, the window opens small and often overlapping other
application windows, which risks responsive-layout differences from what a
real user sees at full screen.

**Use `playwright-cli resize 1920 1080` (or similar) right after `open
--headed`, and stop there.** Do not reach for a `--config` file with
`launchOptions.args: ["--start-maximized"]` + `contextOptions.viewport:
null` to get a "real" maximized OS window — confirmed by direct testing
against this project's actual FusionX UAT app: that specific combination
caused the browser session to die silently within under a minute, every
time, across multiple launch methods, while the exact same config survived
150+ seconds without issue on a lightweight test page (example.com). A
plain `resize` call with no custom launch args ran stable for 10+ minutes
of continuous use against the same FusionX app in the same session. The
fix for "layout looks wrong in a small viewport" is the viewport size, not
the OS window's chrome — `resize` alone already solves the actual problem
without the crash risk `--start-maximized` introduced on this app.

If a session becomes unstable and the cause isn't obvious, suspect any
non-default `launchOptions`/`contextOptions` first — a config change that
works fine against a trivial test page is not proof it's safe against a
heavier real app; test any new launch config against the actual target
app, not just a placeholder site, before trusting it.

## `playwright-cli attach` reliably kills a session opened via `open` — never use it for that

**This was the single biggest blocker in this skill's first live pilot: six consecutive Executor dispatches failed before this was found, each looking like a fresh, unrelated crash.** The actual cause was one wrong command.

`attach` is documented for connecting to a browser that's already running *externally* (`--cdp=chrome`, `--extension`) — it is not the way to let a dispatched role reconnect to a session `playwright-cli` itself already manages via `open`. Running `playwright-cli attach <session-name>` against a session that same `open` call created reliably kills it: `Error: Daemon process exited with code 1 [PlaywrightError: connect ENOENT <session-name>]`. This reproduces identically whether called from the main thread or a dispatched subagent, from Bash or PowerShell, with or without `--persistent`, immediately or after any delay — it is not a timing issue, a sandbox issue, a security-software issue, or a process-parenting issue (all were investigated and ruled out first, at real cost, before this was isolated).

**The fix:** never call `attach` on a session you (or the orchestrator) opened with `open`. To interact with it — from the main thread or from any dispatched role — just run plain commands with the session name:

```
playwright-cli -s=default snapshot
playwright-cli -s=default click <ref>
```

(`-s=default` is the implicit default anyway, so bare `playwright-cli snapshot` etc. also works — but write it out explicitly in dispatch prompts so a fresh subagent isn't left guessing whether it needs to "connect" first. It doesn't.) Confirmed stable across a 13+ minute, 139-command Executor run and multiple subsequent Traceability/Verifier/Defect-Triage dispatches on the same session with zero further session loss once `attach` was removed from every dispatch prompt.

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

## If a session still seems dead after removing `attach`: verify before assuming, watch for orphaned windows

Before dispatching a role that depends on the live session, re-run
`playwright-cli list` immediately beforehand — don't trust a check from
several tool calls ago. If a dispatched role reports it can't reach the
session, the main thread should independently re-verify with its own
`list` call before concluding it needs to re-authenticate.

If a session's daemon dies but the Chrome *window* it spawned doesn't
actually close (observed once, before the `attach` root cause was found:
`playwright-cli list` reported the session gone, but the browser window
was still open on screen, just no longer controllable), reopening starts a
**second**, independently-controllable window — while the first, orphaned
one is still sitting there too. `playwright-cli kill-all` clearing daemon
*registrations* does not guarantee the underlying Chrome *process* actually
exits. Before reopening after any suspected crash, ask the human to
confirm how many browser windows are actually visible on their screen —
don't assume a dead daemon means a dead window.

`--persistent` (with no explicit `--profile`) is a genuinely useful
mitigation for login fatigue across a round's dispatches — the default
persistent profile path is stable across separate `open` calls, so a
human's login carries over and a later `open --persistent` can come up
already-authenticated with no login screen at all.

## `playwright-cli screenshot`/snapshot files save relative to its own invocation directory, not your project folder

`playwright-cli screenshot --filename=<name>.png` (and default snapshot
files) save relative to wherever the `playwright-cli` process itself was
launched from — which, for a dispatched subagent, is whatever working
directory its shell happened to start in, not necessarily the target
project root where the rest of the round's artifacts live. Observed
directly: a round's screenshots ended up under the automation tool's own
working directory rather than the `FUNCTIONAL-TEST-PLAN`'s project folder,
even though every other artifact (network capture, reports, logs) was
correctly written to the right place because those were plain file writes,
not `playwright-cli`'s own relative-path defaults. Tell each dispatched
role to pass an absolute path via `--filename=` for anything that needs to
land in the project folder (`playwright-cli -s=default screenshot
--filename="D:\full\path\to\project\screenshots\name.png"`), and to state
the actual resulting path in its report rather than assuming the relative
name it typed matches where the file landed.

## Network capture stays action-correlated

When Executor records raw network requests/responses, tag each captured
request with the specific action that triggered it (e.g. "clicked Submit
on Collateral > Add Charge") rather than dumping one undifferentiated log
for the whole session. Traceability and Verifier both depend on being able
to find "the request(s) this one action caused" without re-deriving that
mapping themselves — an uncorrelated dump pushes work downstream that
Executor was already in the best position to do at capture time.
