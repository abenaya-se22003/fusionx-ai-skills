# Audit Log

## 2026-09-17 — functional-testing: browser-session.md orphaned from Read First / Stage 0

A live functional-testing round against `taxSummary` opened the workflow
browser session without `--headed`. `playwright-cli open` reported success
(pid, page title, snapshot) with a real page load, so the session looked
healthy from its own output — but no OS-level window existed for the user
to log into or complete MFA on. The user only discovered this because
nothing appeared on screen.

Root cause traced to `SKILL.md`, not to `references/browser-session.md`
itself: `--headed` (Section 2) and the pre-login window-verification check
(Section 5) were correct and complete in `browser-session.md`, but that
file was never in `SKILL.md`'s "Read First, In Order" list — only
`browser-gotchas.md` and this skill's own `gotchas.md` were. Every place
`SKILL.md` did cite `browser-session.md` (Prerequisites, Stage 0, Subagent
Dispatch Rules — three citations total) pointed only at Section 0 (session
naming), never at Sections 2 or 5. Stage 0, the exact point where the main
thread mints the session name and opens it, said "before opening it" with
no inlined launch command and no pointer to the section that defines one.
The Read First list's own line 189-190 additionally claimed session/login
handling was "covered separately by Prerequisites... and Subagent Dispatch
Rules" — that claim was false; neither section restates Sections 2 or 5.

Fixed in `SKILL.md`:
- Read First, In Order now lists `references/browser-session.md` in full as
  item 2, with an explicit note that Sections 2 and 5 are not covered by
  what Prerequisites/Subagent Dispatch Rules cite.
- Removed the false "covered separately" claim from the Read First list's
  first item.
- Stage 0 now inlines the actual launch command
  (`playwright-cli -s=<name> open --headed --browser chrome <url>`) and the
  window-verification check at the point where the session is opened,
  instead of a bare pointer to Section 0.

`references/browser-session.md` required no changes — the contract was
already correct; it was simply unreachable from the workflow that was
supposed to follow it.
