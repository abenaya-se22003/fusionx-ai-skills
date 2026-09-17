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

## 2026-09-17 — swept other playwright-driving skills for the same gap

Checked every skill in this repo that references `playwright-cli` or
`browser-session.md` for the same orphaning pattern found above
(`functional-testing`, `user-manual-update`, `fusionx-urs`,
`api-field-mapper`; `banking-pillar-release-update` confirmed not to use
Playwright at all).

- `user-manual-update` had the identical gap: Workflow step 2 ("Walk UAT")
  cited `references/browser-session.md` Section 0 only, and Read First, In
  Order never listed the file — only this skill's own `gotchas.md`, which
  does correctly document "`open` launches headless by default" but is not
  itself the point where the launch command gets written. Fixed the same
  way: added `browser-session.md` (full file) to Read First, and inlined
  the `--headed --browser chrome` launch command plus the Section 5
  window-verification check directly into step 2.
- `fusionx-urs` was already correct: its live-walkthrough step says
  "read and follow `references/browser-session.md`; it is the
  self-contained, mandatory Playwright contract for this skill" with no
  section-scoping caveat — no orphaning, no fix needed.
- `api-field-mapper` was already correct: "Before any browser interaction,
  read and follow `references/browser-session.md`; it is this repository's
  mandatory session contract and takes precedence over this skill's
  browser-specific guidance" — full-file instruction stated before any
  citation narrows to a specific section, plus `--headed` is separately
  inlined at its own launch command. No fix needed.

Pattern going forward: any citation of `browser-session.md` that names a
specific section (e.g. "Section 0") without also either (a) telling the
reader to read the whole file first, or (b) inlining the Section 2 launch
command and Section 5 verification check at the point of use, reproduces
this gap. Check new citations against this before adding them.
