# Shared Browser Session Contract

This file is the canonical browser-session contract for every skill in this repo that uses `playwright-cli`.

## 1. Discover before opening

- Run `playwright-cli list` before creating a new browser session.
- Run `playwright-cli tab-list` when needed to inspect tabs in the reusable session.
- Reuse an existing authenticated session instead of creating another one.
- Never create a replacement session just because the current session needs a viewport fix.

## 2. Standard launch

For a new browser session:

```bash
playwright-cli open --headed <url>
playwright-cli resize 1920 1080
```

- Keep the browser headed when the user needs to log in or complete MFA.
- Always set the Playwright viewport explicitly after opening the headed browser.
- Do not use `--start-maximized` in launch configuration.
- Do not use `contextOptions.viewport: null` as a workaround.
- Do not assume OS-level window maximization equals a 1920x1080 Playwright viewport.

## 3. Session reuse

Sessions created by `playwright-cli open` are reused directly:

```bash
playwright-cli -s=<session> <command>
```

- Do not run `playwright-cli attach <session>` to reconnect to a session created by `playwright-cli open`.
- Preserve the same session throughout the skill workflow whenever possible.

## 4. Lifecycle ownership

- The main skill thread owns browser lifecycle.
- Subagents may drive the already-authenticated session only when explicitly delegated.
- Subagents must not independently open a second browser, close or replace the shared session, or re-authenticate unless the skill explicitly requires it and the user authorizes it.
- Never invalidate a working authenticated session to solve a viewport or rendering issue.

## 5. Login and MFA

- Keep the browser headed for login and MFA.
- The user completes credentials and MFA; automation waits for explicit confirmation before authenticated actions.
- Never record or expose credentials, tokens, cookies, or other sensitive authentication data.

## 6. Recovery

- If a session becomes detached or an orphaned window appears, inspect `playwright-cli list` and `playwright-cli tab-list` first and reuse the existing session.
- Do not blindly attach, reopen, or spawn another session.
- If the browser state is genuinely unusable, stop and surface the problem before replacing the session.

## 7. Evidence

- Use absolute paths for screenshots and snapshots when writing artifacts.
- Capture evidence at the required viewport after `playwright-cli resize 1920 1080`.
- Do not treat evidence captured from an accidentally small or windowed viewport as final.

## 8. Precedence

This contract is mandatory for every browser-dependent skill in this repository. It takes precedence over skill-local browser launch, viewport, session-reuse, session-lifecycle, and recovery instructions.

Skill-specific gotchas may add useful lessons, but they must not override this contract.
