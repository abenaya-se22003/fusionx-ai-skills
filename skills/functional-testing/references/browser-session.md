# Shared Browser Session Contract

This file is the canonical, workflow-scoped browser-session contract for every skill in this repo that uses `playwright-cli`. It governs one workflow's session at a time. It never describes, and must never be read as describing, a single machine-wide session that any workflow may pick up.

## 0. Core model: one named session per workflow

`playwright-cli` sessions are named (`-s=<name>`) and tracked by a daemon that every `playwright-cli` invocation on the machine can see — `playwright-cli list` shows every session anyone has open, not just yours. Because of that, an anonymous/default session, or "whatever `list` shows as authenticated," is never safe to reuse: it may belong to a different workflow that is running right now, concurrently, on the same machine.

Every workflow (one top-level run of a skill, intake through delivery) gets exactly one **named** session for its whole lifetime:

- **Name shape:** `<skill-prefix>-<task-identifier>-<tag>`
  - `<skill-prefix>` — fixed per skill: `fx-func` (functional-testing), `fx-um` (user-manual-update), `fx-urs` (fusionx-urs), `fx-api` (api-field-mapper). This alone keeps two different skills' workflows apart even when they reference the identical ticket number.
  - `<task-identifier>` — the human-readable identifier the skill already establishes before it ever touches a browser: functional-testing's round-id, user-manual-update's ticket number or module task name, fusionx-urs's ticket/story id, api-field-mapper's numbered task folder name. Lowercase, letters/digits/hyphens only. Don't invent a new identifier scheme — reuse the one the skill already mints for its own artifacts.
  - `<tag>` — a short (4-6 char) random or timestamp suffix, generated once at the start of the workflow. It exists purely so two concurrent workflows that land on the identical skill-prefix + task-identifier (two operators both starting "round-1" against the same project at the same moment, a ticket number reused later by a different round) still get distinct sessions. Always include it, even when a collision looks unlikely.
- Compute the name once, before the first `playwright-cli` call of the workflow, and record it plainly somewhere the workflow already writes (a line in the round report, ticket tracking file, task-folder notes, `AUDIT-LOG.md` entry) so a human — or this same workflow resuming later — can find it again in `playwright-cli list`. Don't regenerate it mid-workflow.
- From the very first command, every invocation is `playwright-cli -s=<name> <command>`. Never a bare `playwright-cli <command>` — that targets the anonymous `default` session, which is exactly the shared/global session this contract exists to eliminate.

## 1. Discover before opening

- Run `playwright-cli list` and look for your own exact computed session name in the output.
- **Match the exact name only.** Any other session name in that list belongs to a different workflow, possibly running concurrently right now. Do not adopt it, inspect its tabs, resize it, navigate it, or close it — not even if it looks idle, unattended, or already authenticated. "A session exists and is logged in" is never sufficient; it must be logged in **for this workflow**, i.e. carry this workflow's own name.
- If your exact name is present, reuse it directly (`playwright-cli -s=<name> <command>` — do not call `open` again; see Section 2).
- If it is absent, create it (Section 2).
- If you're resuming a paused workflow, check that workflow's own standing artifact for a previously recorded session name before minting a new one — confirm via `list` that it's actually gone before deciding you need a new session.

## 2. Standard launch

To create the workflow's session for the first time:

```bash
playwright-cli -s=<name> open --headed --browser chrome <url>
```

- Launch Google Chrome explicitly with `--browser chrome`; do not rely on the CLI default browser.
- `--browser chrome` should launch the machine's actual installed Google Chrome, not download a separate copy. If `open` ever starts downloading/installing a bundled Chromium even though Chrome is genuinely installed on the machine, do not let that install proceed — it's solving the wrong problem and wastes a multi-hundred-MB download. Stop, confirm Chrome is actually present (e.g. `where chrome` on Windows, or the standard install path), and treat a channel-detection failure like this as an environment problem to surface plainly, not something to silently work around by installing a redundant browser.
- If Chrome is genuinely not installed on the machine at all (confirmed absent, not just a channel-detection hiccup), that's a real Prerequisites gap — surface it to the user rather than silently installing a substitute browser on their machine.
- Keep the browser headed when the user needs to log in or complete MFA.
- Do not configure automatic maximization, forced window sizing, or a custom viewport as part of the skill launch.
- Leave browser window size, maximization, and resizing to the user.
- Do not use `--start-maximized`.
- Do not use `contextOptions.viewport: null` as a workaround for a browser-launch problem.
- Do not use `playwright-cli resize` as part of the skill's normal browser setup.
- Do not silently change the user's browser window size just to make a page fit better.
- **Never call `open` for a session name that already exists** (confirmed via `list` per Section 1). `open` on an already-open name does not attach to or reuse that browser — it silently starts a brand-new browser process under the same name and orphans the old one (confirmed directly: the process id changed on a second `open` call against an unchanged session name, with no error or warning). Calling `open` twice for your own workflow is exactly as destructive as another workflow guessing your session name: it throws away whatever login/navigation/in-memory state the first `open` produced.

## 3. Session reuse

Sessions are addressed by name for every command:

```bash
playwright-cli -s=<name> <command>
```

- Do not run `playwright-cli attach <session>` to reconnect to a session created by `playwright-cli open`. `attach` is for connecting to a browser running *externally* to `playwright-cli` (`--cdp=`, `--extension`) — not for reconnecting to a session `playwright-cli` itself already manages via `open`. Calling `attach` on an `open`-created session reliably kills it.
- Preserve the same named session throughout the workflow whenever possible; don't switch names mid-workflow.
- Never run `playwright-cli close-all` or `playwright-cli kill-all` as part of a skill's normal flow. Both act on every session the daemon knows about, not just yours — under this repo's normal usage that means every other concurrently-running workflow's browser too. Use `playwright-cli -s=<name> close` to close only your own session, and only once the workflow has actually finished (or not at all, if the user wants the browser left open). Only run `close-all`/`kill-all` when the user explicitly asks to clean up every session on the machine.

## 4. Lifecycle ownership

- The main skill thread owns the workflow's session for its entire lifetime: it computes the name, creates the session, authenticates it, and is the only one that closes or replaces it.
- Subagents dispatched by that workflow receive the session name as a literal value stated in their dispatch prompt (e.g. "use `playwright-cli -s=fx-func-round-1-9k2p` for all browser commands") and use only that name. A subagent never discovers its session by running a bare `playwright-cli list` and picking a plausible-looking entry — it is handed the name it needs and uses it as-is.
- Subagents must not independently open a second browser, close or replace the workflow's session, re-authenticate, or touch a session under any other name — including one that looks authenticated or idle — unless the skill explicitly requires a second identity and the user has authorized it (e.g. a maker/checker step needing a second login).
- If a subagent finds its assigned session name missing or dead, it does not create a replacement itself and does not fall back to a different session it finds in `list` — it reports BLOCKED to the main thread, which owns recovery.

## 5. Login and MFA

- Keep the browser headed for login and MFA.
- The user completes credentials and MFA; automation waits for explicit confirmation before authenticated actions.
- Only the thread that first creates the workflow's session authenticates it. Every later consumer of that session — later stages, subagents — reuses that authentication; none of them logs in again.
- Never record or expose credentials, tokens, cookies, or other sensitive authentication data.

## 6. Recovery

- If the workflow's named session becomes detached, or `-s=<name>` starts failing, inspect `playwright-cli list` first — confirm your name is actually gone, not just slow, before doing anything else.
- If it's genuinely gone, recreate it under the exact same name (Section 2) — never under a new name, and never by adopting a different session that happens to appear in `list`.
- An orphaned browser window can remain on screen after its daemon-side session has died (`list` no longer shows it, but the OS window is still there). That window is a dead session's leftover, not evidence the session is still usable. Reopening under the same name starts a fresh, controllable browser; check how many windows are actually on screen before assuming a stale one has already gone away.
- If the session is genuinely unusable and recreating it would lose in-progress state the user cares about, stop and surface the problem before replacing it.
- Do not treat a small or resized browser window as a reason to replace the session.

## 7. Evidence

- Use absolute paths for screenshots and snapshots when writing artifacts.
- Capture evidence using the browser viewport currently chosen by the user.
- Do not resize or maximize the browser solely for evidence capture.

## 8. Concurrency

Two workflows never collide, because each computes its own session name independently and every command that touches a session states that name explicitly:

- Two functional-testing rounds running at once compute different round-ids — or, in the rare case those would coincide, different random tags — so they hold two different named sessions. Neither round's dispatch prompts ever contain the other round's session name, so neither can address the other's browser even by accident.
- functional-testing and user-manual-update running at once use different skill-prefixes (`fx-func-...` vs. `fx-um-...`) even if they happen to reference the same ticket number.
- A subagent only ever receives the one session name its own dispatch prompt states — it has no mechanism to enumerate or guess a sibling workflow's name, since names aren't derived from anything globally predictable (the random tag guarantees this even when the human-readable part is identical).
- `playwright-cli list` always shows every session on the machine, by design — this contract's safety comes from exact-name matching (Section 1) and the ban on bulk operations (Section 3), not from `list` filtering anything out for you.

## 9. Precedence

This contract is mandatory for every browser-dependent skill in this repository. It takes precedence over skill-local browser launch, viewport, session-reuse, session-lifecycle, and recovery instructions.

Skill-specific gotchas may add useful lessons, but they must not override this contract.
