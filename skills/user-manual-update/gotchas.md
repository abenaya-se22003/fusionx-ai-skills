# Gotchas — Environment, Session, and Subtle Content Bugs

## Mandatory shared browser-session contract

Before any browser interaction, read and follow:

`../../shared/browser-session.md`

This is the canonical contract for browser launch, viewport, session reuse,
session lifecycle, and recovery. The skill-specific lessons below may add
useful context, but must not override the shared contract.

Collected across the Collateral, Accounts, Lending, SCO, Term Deposit, and
Cash module updates. These are operational/environment lessons not restated
in SKILL.md's "Coverage Standard" or "Manual Production Rules" sections —
read this alongside `SKILL.md`.

## Finding and driving the browser

- `playwright-cli` is a real CLI tool (installed globally,
  `npm install -g @playwright/cli`), driven via the shell — it is **not** an
  MCP tool and will never show up in an MCP tool search. Before telling the
  user a UAT task is blocked for lack of browser tooling, check
  `which playwright-cli` / `playwright-cli list` in addition to any MCP tool
  search — these are separate capability surfaces.
- `playwright-cli list` / `tab-list` often shows a browser session already
  open and authenticated to UAT from a prior task — check before opening a
  fresh one.
- `playwright-cli open` launches headless by default — the browser never
  actually becomes visible unless `open` is called with `--headed`. Needed
  for any stage where the human has to see or interact with the browser
  (login, MFA, watching the automation); discovering this after the fact
  means the human was staring at nothing while the automation waited
  silently for a login it couldn't ask for.
- A headed browser window may launch successfully but not be visibly on top.
  Force it to the foreground via PowerShell:
  `Get-Process | Where-Object { $_.MainWindowTitle -like "*<title fragment>*" }`
  then `ShowWindow`/`SetForegroundWindow` via a small `Add-Type` P/Invoke
  block. Don't assume `--headed` alone guarantees visibility.
- Sidebar clicks often fail silently from an intercepting sticky
  header/overlay. Don't retry the click — dump every sidebar item's real
  route in one shot (`document.querySelectorAll('.<sidebar-item-class>')`,
  reading `id`/`textContent`) and navigate by URL directly instead.
- Some antd `Select` components don't respond to a plain synthetic `.click()`
  (focus fires, dropdown never opens). Dispatch the full sequence instead:
  `mousedown` → `mouseup` → `click`, all `bubbles:true, cancelable:true`.
- Never call `playwright-cli attach <session>` to reconnect to a session
  opened via `open`. `attach` is for connecting to a browser running
  *externally* to `playwright-cli` (`--cdp=chrome`, `--extension`) — not for
  reconnecting to a session `playwright-cli` itself already manages.
  Confirmed by direct reproduction (functional-testing skill's first live
  pilot): calling `attach` on a self-opened session reliably kills it
  immediately (`Error: Daemon process exited with code 1 [PlaywrightError:
  connect ENOENT <session-name>]`), from the main thread or a dispatched
  subagent, from Bash or PowerShell, regardless of `--persistent` or
  timing — it is not a timing issue, a sandbox issue, a security-software
  issue, or a process-parenting issue (all were investigated and ruled out
  first, at real cost, before this was isolated). It cost six consecutive
  failed subagent dispatches before being root-caused. To use an existing
  session, just run plain commands with the session name —
  `playwright-cli -s=<name> <command>` (`list`, `snapshot`, `tab-list`,
  etc.) — no attach step needed at all, ever. Confirmed stable across a
  13+ minute, 139-command Executor run and multiple subsequent
  Traceability/Verifier/Defect-Triage dispatches on the same session, with
  zero further session loss once `attach` was removed from every dispatch
  prompt.
- Don't reach for a `--config` file with `launchOptions.args:
  ["--start-maximized"]` + `contextOptions.viewport: null` to get a "real"
  maximized OS window instead of the small default launch size. Confirmed
  by direct testing across multiple launch methods: that specific
  combination crashed the browser session against a real FusionX app
  within under a minute every time, while surviving 150+ seconds without
  issue on a lightweight test page (example.com) — a launch config that's
  safe on a placeholder site is not proof it's safe against a heavier real
  app; suspect any non-default `launchOptions`/`contextOptions` first if a
  session becomes unstable and the cause isn't obvious. Use `playwright-cli
  resize <w> <h>` (e.g. `1920 1080`) right after `open --headed` instead —
  it sets a large viewport via CDP, which solves the actual "layout looks
  wrong in a small viewport" problem without the window-chrome crash risk;
  a plain `resize` call with no custom launch args ran stable for 10+
  minutes of continuous use against the same FusionX app in the same
  session.
- `playwright-cli screenshot --filename=<name>.png` (and default snapshot
  files) save relative to wherever the `playwright-cli` process itself was
  launched from, not necessarily the project folder you expect — this
  matters most for a dispatched subagent, whose working directory may not
  match the main thread's. Observed directly: a round's screenshots ended
  up under the automation tool's own working directory rather than the
  intended project folder, even though every other artifact (network
  capture, reports, logs — plain file writes, not `playwright-cli`'s own
  relative-path defaults) landed correctly. Pass an absolute path
  (`--filename="D:\full\path\to\screenshots\name.png"`) for anything that
  needs to land in a specific project folder, and confirm the actual
  resulting path rather than assuming the name you typed is where it
  landed.
- If a session's daemon dies but the Chrome *window* it spawned doesn't
  actually close (observed once, before the `attach` root cause above was
  found: `playwright-cli list` reported the session gone, but the browser
  window was still open on screen, just no longer controllable), reopening
  starts a **second**, independently-controllable window — while the
  first, orphaned one is still sitting there too. `playwright-cli kill-all`
  clearing daemon *registrations* does not guarantee the underlying Chrome
  *process* actually exits. Before reopening after any suspected crash,
  confirm how many browser windows are
  actually visible on screen rather than assuming a dead daemon means a
  dead window — especially before opening a replacement while a human might
  still be mid-login on the original.
- `--persistent` (with no explicit `--profile`) is a genuinely useful
  mitigation for login fatigue across a multi-dispatch task — the default
  persistent profile path is stable across separate `open` calls, so a
  human's login carries over and a later `open --persistent` can come up
  already-authenticated with no login screen at all.

## A click that produces zero visible reaction

No dialog, no error text, no navigation. Don't keep retrying the click or its
event sequence — check `playwright-cli requests`/`console` first. Zero new
network requests after the click means the click isn't registering (a
UI/selector problem — keep debugging the click). A request that fires but
does nothing means the app's own handler is broken (a real defect — stop
retrying, log it). Rule out a session-wide cause fast by trying the identical
action on a different, already-working screen in the same session.

## Session and backend stability

- A UAT session can expire mid-task even with a persistent browser profile —
  the page shell can still render from cache while API calls 401 underneath
  it. After resuming a paused session (especially across days), verify
  liveness with a real authenticated API call, not just "the page loaded."
- Distinguish a genuine backend outage (HTTP 502/429/503 across multiple
  unrelated endpoints, confirmed via both the browser session and a raw
  unauthenticated `curl`) from a real permissions problem — a 429 can render
  as a generic "403 Sorry, you are not authorized" page that looks identical
  to a real permission error until the network log is checked.
- Don't hammer retries during an active outage — use scheduled waits and
  re-check via the real browser session (not just a health endpoint, since
  auth/session state differs). After recovery, retry every blocked screen
  individually — read and write paths recover independently, and a fix
  should be confirmed against a fresh, previously-untested record each time
  before concluding a failure is a standing defect rather than a one-off.
- A crash reproduced 3x under one session is good evidence but not proof of a
  screen-wide defect — it can be session/account-context-specific
  (permissions, cached state). If given evidence the same action works under
  a different login, narrow the defect entry instead of leaving it as
  "screen is broken."

## Word / docx build environment

- `to_pdf_export.py` (or any Word-COM script) can leave a `WINWORD.exe`
  process holding the docx open, blocking the next python-docx save with
  `PermissionError: [Errno 13]`. Kill it before retrying:
  `Get-Process -Name WINWORD | Stop-Process -Force`. Safe to do without
  asking — this is always this project's own automation-launched instance.
- A document's cover page title and its repeating running header are
  separate elements. A version-string fix applied to the running header does
  not touch a stale version baked into the cover title's own run — check the
  cover page as its own explicit step whenever fixing a version string.
- "Keep it at vX across the doc" means literally everywhere the version
  appears: header, footer, cover, delivered filenames, AND prose in the
  tracking docs (`UAT Coverage and Defect Log.md`, `Outstanding Items and
  Blockers.md`) that names the version.
- A bulk find/replace on a version string can produce a visible duplicate
  ("1.7v/1.7v") in any sentence that originally listed multiple version
  numbers together (e.g. "bumped 1.6v → 1.7v → 1.8v"). After a bulk replace,
  re-grep specifically for the new string appearing twice close together —
  don't just confirm the old string disappeared.

## Content and data pollution risks

- Any typed free-text field (Note/Comment/Remark) captured in a screenshot is
  a leak risk — a tester's throwaway input (e.g. "UAT documentation test -
  approved") can end up baked into a shipped figure. Check this explicitly
  when asked to verify the manual is clean, in addition to the known
  document-upload risk below.
- Uploaded "supporting documents" in a UAT environment can be systemic test
  noise (random staff screenshots), not per-record. If a second record shows
  the same pattern, stop hunting for a "clean" example and document the
  feature from safe metadata only (e.g. the row showing Document Date/Type,
  unopened) rather than opening and screenshotting unrelated file content.
- Two screenshots meant to show a before/after or unselected/selected pair
  can end up state-swapped on disk if captured during a chaotic multi-retry
  debugging episode. Visually diff the specific region that's supposed to
  differ before trusting such a pair — don't assume capture order matches
  file-naming order just because the click sequence "worked eventually."
- A single list-view read immediately after a Create/Update is not proof the
  action committed. Reload the page (or navigate away and back) and re-search
  before writing down "confirmed" — a same-render read can be stale, cached,
  or not yet reflect an approval-gated write.

## Sweeping for a banned phrase across the whole document

When hunting for every instance of a banned pattern (e.g. defect-log
language), a hand-assembled list of phrasings will miss real instances worded
differently. Find the smallest substring that's actually invariant across
every known real instance (for this project: the case-insensitive substring
`"defect log"`) and grep for exactly that — including table cells, not just
`doc.paragraphs`, since the same violation can hide in a Version Control
table's own change-description cell.

## Gap-hunting discipline

- A "gap" found via a coverage log or Outstanding Items file is not proven
  until checked against the manual's actual text — the tracking doc can be
  the thing that's incomplete, not the manual. Grep the actual `.docx` for
  the action/field name before reporting a docx edit is needed.
- When a QC script's heading range is left too wide (e.g. no `--end-heading`,
  checking to end of document), it will correctly surface real defects
  outside the current task's scope. That's not a bug in the check — confirm
  which heading a finding falls under before folding it into the current
  round's fix list; report an out-of-range finding separately.
- A field whose structure looks conditional on one specific value should
  also be tested with no value selected / the default state first — this can
  settle in one check what would otherwise take testing every possible
  parent value one at a time.
