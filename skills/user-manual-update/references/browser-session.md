# Shared Browser Session Contract

This file is the canonical browser-session contract for every skill in this repo that uses `playwright-cli`.

## 1. Discover before opening

- Run `playwright-cli list` before creating a new browser session.
- Run `playwright-cli tab-list` when needed to inspect tabs in the reusable session.
- Reuse an existing authenticated session instead of creating another one.
- Never create a replacement session just because the current session needs a viewport fix.

## 2. Standard launch and viewport

For a new browser session, use the packaged browser-session config for the skill:

```bash
playwright-cli --config "<skill-root>/references/browser-session.config.json" open --headed <url>
```

The config fixes the Playwright context viewport at 1920x1080. This is intentional: **do not use `playwright-cli resize` as the normal desktop setup.** The CLI `resize` command changes the browser window/viewport, so using it as the primary fix allows manual OS-level maximize/resize actions to change the app's responsive layout again.

- Keep the browser headed when the user needs to log in or complete MFA.
- The browser may be manually maximized or restored by the user. The Playwright viewport must remain 1920x1080.
- Do not use `--start-maximized`.
- Do not use `contextOptions.viewport: null`.
- Do not use `playwright-cli resize` to establish the desktop viewport.
- Do not treat the physical Chrome window size as the Playwright viewport size.
- After opening, verify the effective viewport with:

```bash
playwright-cli eval "() => window.innerWidth + 'x' + window.innerHeight"
```

It must report `1920x1080` before browser-driven work begins.

If a manual resize/maximize somehow changes the effective viewport, stop browser interaction and restore the session to the configured 1920x1080 context rather than continuing against a different responsive layout. Do not silently continue with mixed viewport evidence.

## 3. Session reuse

Sessions created by `playwright-cli open` are reused directly:

```bash
playwright-cli -s=<session> <command>
```

- Do not run `playwright-cli attach <session>` to reconnect to a session created by `playwright-cli open`.
- Preserve the same session throughout the skill workflow whenever possible.
- A session opened with the browser-session config retains the configured viewport for the lifetime of that browser context.

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
- If the page layout changes unexpectedly, verify `window.innerWidth`/`window.innerHeight` before changing anything else. A viewport change is a browser-state problem, not evidence that the FusionX screen itself changed.

## 7. Evidence

- Use absolute paths for screenshots and snapshots when writing artifacts.
- Capture evidence only after verifying the effective viewport is `1920x1080`.
- Do not treat evidence captured from an accidentally resized or responsive viewport as final.

## 8. Precedence

This contract is mandatory for every browser-dependent skill in this repository. It takes precedence over skill-local browser launch, viewport, session-reuse, session-lifecycle, and recovery instructions.

Skill-specific gotchas may add useful lessons, but they must not override this contract.
