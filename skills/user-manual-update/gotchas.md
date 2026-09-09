# Gotchas — Environment, Session, and Subtle Content Bugs

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
