# Functional-Testing Browser Gotchas

Read this before a browser-driving role starts. It supplements, and never
overrides, `browser-session.md`.

## FusionX UI behavior

- Virtualized Ant Design dropdowns do not expose every option in an
  accessibility snapshot. Query the live option DOM, then cross-check the
  count before recording values.
- For a custom select that ignores a plain click, target its inner selection
  element or send `mousedown`, `mouseup`, then `click`.
- Before reading state or taking evidence, wait until no loading indicator is
  active. For an unusually slow screen, refresh and retry; allow slow valid
  confirmations several minutes before calling them broken.
- If a sticky header or overlay intercepts a sidebar click, derive the real
  target route and navigate there directly instead of repeatedly clicking.
- A click with no visible reaction must be diagnosed with `playwright-cli
  requests` and `console`: no request means a selector/UI problem; a request
  that produces no result is an application finding.

## Session and environment recovery

- A rendered page shell is not proof an old session is live. After a pause,
  verify an authenticated API request has not returned 401 before resuming.
- Distinguish backend outages (such as 502/429/503 across unrelated endpoints)
  from permission failures using browser network evidence. Do not hammer
  retries during an outage; re-check blocked screens individually after it
  recovers using a fresh suitable record.
- Before replacing a dead session, inspect visible browser windows as well as
  `playwright-cli list`/`tab-list`: an orphaned Chrome window may remain after
  its daemon has died. Never create a second browser just to diagnose it.
- `--persistent` may reduce login fatigue across an authorized multi-dispatch
  task, but it does not prove the UAT session remains authenticated.

## Evidence and role dispatch

- Use absolute screenshot and snapshot paths and confirm the produced path.
- Every dispatched browser role uses `playwright-cli -s=<session> <command>`;
  it never opens, closes, attaches to, or re-authenticates a browser. If the
  shared session is unavailable, report BLOCKED to the main thread.
- Immediately before dispatching a browser role, the main thread re-runs
  `playwright-cli list`.
