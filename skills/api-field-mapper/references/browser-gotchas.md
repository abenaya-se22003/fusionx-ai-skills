# API Field Mapper Browser Gotchas

## Mandatory shared browser-session contract

Before any browser interaction, read and follow
`references/browser-session.md`. It is the authoritative contract for browser
launch, session reuse, lifecycle ownership, recovery, and evidence paths. The
guidance below adds FusionX-specific interaction and coverage lessons; it does
not override that contract.

## Purpose

Use these instructions whenever Playwright is used to inspect, test, or document a business application. The objective is complete functional and navigational coverage within the scope authorized by the user.

## No Breadth-Only Passes — Default to Full Depth Immediately

**This is the most-repeated failure in this project's history and must not recur.** The recurring pattern: a first pass checks landing pages, tile/screen titles, or infers a screen is "clean" or "low risk" from its name alone, reports the sweep as done — and only goes to real depth after the user pushes back, sometimes multiple times in a row, naming the same class of gap each time. Every single time this happened, the deep pass found real, previously-missed findings. Breadth-only passes have never once turned out to be sufficient in this project.

**Rule: when the user asks to check, test, or sweep something — anything, not just when they say "deep" or "thorough" — treat that as a request for the full Coverage Standard below, applied immediately, not as license to do a fast title/landing-page pass first and go deeper only if asked again.** Do not make the user repeat the same instruction to get the same result. Concretely:

- Never conclude a screen has "no target content" from its name, tile title, or menu label. Open it.
- Never report a sweep as complete after checking only entry points, tile titles, or default/landing states. Every nested tab, modal, wizard step, dropdown branch, and rendered-output column must actually be opened/generated and read (see Coverage Standard, Dropdowns and Selectable Controls, and A Row-Action Inventory Is Not a Substitute for Completion Testing below) before anything is called clean.
- If time or scale genuinely forces a narrower pass, say so explicitly before starting and get the user's sign-off on the narrower scope — never narrow scope silently and present the result as if it were the full sweep.
- A completion report that only lists what was checked, without also stating what full depth would have required and confirming that bar was met, is not acceptable.

## Session and Access

1. Launch Playwright in an explicitly headed, user-visible browser session and navigate to the supplied URL. With `playwright-cli`, use the standard launch and session-reuse rules in `references/browser-session.md`; never rely on an implicit/default display mode for an interactive walkthrough.
2. Before asking the user to sign in, complete MFA, or observe the automation, verify that the headed browser has a real visible desktop window and bring that exact automation-controlled window to the foreground. Do not use a headless session for any user-interactive authentication step.
3. Wait for the user to confirm that login is complete before interacting with authenticated screens.
4. Preserve the authenticated browser session throughout the walkthrough.
5. Do not enter excluded external systems or modules until the user explicitly authorizes them.
6. Do not expose credentials, tokens, personal data, or other secrets in notes or screenshots.
7. Use the user's designated automation tool/CLI for the walkthrough. If the repository also contains an unrelated project-specific test framework or agent, do not use it in place of the designated tool unless the user says to.

## Coverage Standard

Cover every in-scope item, including:

- Dashboard or landing-page entry points.
- Every sidebar and top-navigation process.
- Parent menus and all nested menu items.
- Every screen, tab, accordion, card, modal, drawer, wizard step, and sub-screen.
- Every visible button, icon button, link, row action, and clickable field.
- Search, filter, sort, pagination, expand/collapse, reset, clear, cancel, back, and close controls.
- Add, create, save, submit, resubmit, view, edit, update, delete, approve, reject, assign, and remove-assignment actions where authorized.
- Nested records such as identifications, contacts, addresses, bank accounts, tax IDs, relationships, key persons, and Powers of Attorney.
- Empty, populated, no-result, validation-error, successful, pending, active, update, confirmation, and completion states where applicable.
- Every approval category/type exposed by the application, not only the default approval queue.
- Test both newly created records and existing populated records when suitable UAT data is available. Newly created records validate the end-to-end creation lifecycle; existing records validate inquiry, historical data display, maintenance, update, nested-entry, submission, and downstream workflow states.

## Dropdowns and Selectable Controls

For every dropdown, radio group, segmented control, switch, checkbox group, card selector, autocomplete, date picker, and time picker:

1. Open the control.
2. Record every static value exactly as displayed, including capitalization and spelling.
3. Select every value at least once when it can change fields, validation, navigation, or workflow behavior.
4. Follow and test every branch created by a selection.
5. Inspect fields or sub-screens that appear, disappear, become mandatory, or become enabled.
6. Capture an expanded-control screenshot when the values are important to the manual.
7. Distinguish static values from dynamic master-data results.
8. For dependent lookups, document the dependency and test representative parent values. Examples include Bank to Branch to Product and Country to Province to District.
9. Do not describe a temporary subset of a live lookup as a permanent complete list.

## Search and Filtering

For every search-criterion selector:

1. Record all criteria.
2. Execute each criterion with a valid matching value where test data exists.
3. Test a valid value with no match.
4. Test blank input and record the validation response.
5. Test clear/reset behavior.
6. Test result selection, Active/Pending or equivalent tabs, and pagination.
7. Verify the details displayed after selecting a result.

## Transaction Testing

1. Use both records created during the current walkthrough and designated existing populated UAT records.
2. Use newly created records to validate creation, validation, save, submission, and the resulting workflow state.
3. Use existing populated records to validate search, inquiry, complete data display, updates, nested add/view/update/delete actions, resubmission, approvals, and historical or downstream states.
4. If either record type is unavailable, document the missing coverage and reason rather than silently treating the other record type as equivalent.
5. Exercise creation and submission to completion where the UI and authorization permit it.
6. Exercise updates and resubmission where permitted.
7. Exercise nested add, view, update, and delete actions where present.
8. Exercise every approval type and both approve and reject paths using suitable test items.
9. Enter meaningful rejection or confirmation remarks when required.
10. Verify the resulting status, queue, audit information, or confirmation message.
11. Do not perform irreversible or production-impacting actions without clear authorization.
12. Do not click destructive controls merely to inspect them; use a disposable UAT record or stop at the confirmation dialog when mutation is not authorized.

## Evidence Capture

Capture screenshots for:

- Each major screen and process entry point.
- Important initial, populated, review, confirmation, and resulting states.
- Expanded dropdowns and branch-changing selectors.
- Add, view, edit/update, delete, submit, approve, reject, and assignment-removal interfaces.
- Nested-entry dialogs and completed nested-entry tables.
- Search criteria, representative results, filters, and relevant tabs.

Capture evidence continuously during the walkthrough. Do not postpone all screenshots until the end, because transient dropdown, dialog, validation, confirmation, and resulting states may no longer be reproducible.

Screenshot rules:

1. Capture the smallest view that clearly communicates the action and surrounding context.
2. Avoid duplicate screenshots that provide no new instructional value.
3. Use descriptive, sequential filenames.
4. Exclude secrets and unnecessary personal information.
5. Keep bug-only screenshots separate from the user-manual evidence set.

## Ant Design / Virtualized UI Quirks

Many enterprise apps built on Ant Design (or similar component libraries) render dropdown option lists as a virtualized list — only the options near the current scroll position exist in the DOM/accessibility tree at once.

1. Never rely on the accessibility-tree snapshot alone to enumerate a dropdown's full option list. Query the live DOM directly for all option elements (e.g. `document.querySelectorAll('.ant-select-item-option')`, adjusted to the actual component library's class names) and cross-check the count against what the snapshot showed. A snapshot-only count has produced confirmed undercounts (a dropdown recorded as having 2 options that actually had 3, and another recorded as 2 that actually had 5).
2. When a plain click on a dropdown/select element does not register (common with these libraries' custom-rendered selection controls), click the inner selection-item element by its title/text attribute instead of the outer container.
3. Before capturing a screenshot or reading page state, confirm no loading spinner is active (e.g. check that `.ant-spin-spinning` or the library's equivalent loading-indicator class has zero matches) rather than proceeding immediately after a click or navigation. Two screenshots were captured mid-load in this way (a dimmed "Loading..." overlay and a "personalization in progress" splash) and had to be retaken after adding this check.
4. If a screen loads for an unusually long time, refresh and retry rather than waiting indefinitely or assuming failure — but do give slow-but-working confirmations several minutes before concluding they are broken (some confirm actions in this application legitimately take minutes with no visible progress indicator).
5. When a sidebar/menu click does not register because an overlapping element intercepts the click (common with sticky headers or animated menus), navigate directly to the target screen's URL instead of retrying the click.
6. When resuming a browser session across tool calls, list open tabs specifically (not just active browser sessions) to find a tab that opened as a side effect of an action, such as a report opening in a new tab after a confirmation.

## Completion Sweeps Are Scoped to the Whole Ticket, Not to Named Examples

When a user asks for a completion re-verification (see the section above) after naming one or two example gaps, treat the request as covering **every action on every in-scope screen**, not just the named examples — the named items are illustrations of a problem class, not the full list to fix. This happened concretely on the Collateral module (2026-08-06): the user named "Request Edit" and "Change Status" as examples, then had to explicitly clarify "this is not just limited to what I mentioned... every action needs to be tested" after an initial pass only addressed the named items.

Concretely, before reporting a completion sweep as done:

1. Enumerate every screen in scope and every action on each (search, every row action, every toolbar action, every stage/tab variant) — build this list from the coverage log and a fresh live row-action inventory, not from memory of what was previously flagged.
2. For each action, resolve it to exactly one of: confirmed complete (real result verified), blocked (named defect or root-caused data issue), or not applicable (e.g. a stage genuinely has no actions — verify this too, don't assume).
3. Produce this as an explicit table (screen, action, status, evidence) in the coverage log, not just a prose summary — a table makes a silently-skipped action visible on review; prose lets it hide.
4. If the user's request only names a few examples, still sweep the whole ticket and say so explicitly in the response ("checked all N actions across all M screens, not just the ones named") rather than silently limiting scope to what was named.

## Coverage Tracking

Maintain a coverage record containing:

- Process and screen.
- Control or scenario.
- Values/branches tested.
- Test record used.
- Result.
- Screenshot filename.
- Remaining work.
- Blocker or defect reference.

Do not claim full coverage while any in-scope branch, selector, nested control, or permitted transaction remains untested. Clearly distinguish:

- Completed coverage.
- Not applicable.
- Excluded by the user.
- Blocked by permissions, missing data, or a defect.
- Dynamic/master-data dependent.

## Defects and Blockers

1. Record unexpected behavior with the screen, steps, expected result, actual result, and evidence.
2. Keep defects and blockers in a separate defect/coverage document unless the user requests otherwise.
3. Do not place bug screenshots or defect commentary in the normal user manual.
4. Continue with unaffected branches instead of stopping the entire walkthrough.
5. Revisit blocked items only when the user supplies the necessary permission, test data, or corrected build.
6. Before recording something as blocked, retry with more than one input combination (different records, filter values, or a fresh login/session) so the defect log reflects a reproducible defect rather than a one-off fluke. Note how many attempts were made.
7. Before recording an unexplained gap (e.g. a screen that never returns expected data), attempt to trace the actual cause — inspect the underlying network request/response, not just the rendered UI — so the log records a root cause where possible instead of only "no data returned."
8. When a blocker or gap is found, tell the user and ask whether to keep investigating or stop and document it as-is, rather than silently deciding either way.

## A Row-Action Inventory Is Not a Substitute for Completion Testing

A "row-action inventory" (scanning a grid's Action column / toolbar buttons per screen, e.g. via `document.querySelectorAll('.ant-table-tbody tr td:last-child')`) is a fast, cheap check that catches one specific class of gap: an action button that exists in the app but was never *documented at all*. It is not the same bar as this file's actual Completion Criteria, and passing it does not mean a screen's coverage is complete.

On the Collateral module (PF-56839, 2026-08-06), a row-action inventory across 5 screens correctly found one undocumented button (a real gap, closed same day) but was then reported as "clean, matches documentation" for other screens whose actions *were* documented yet had never actually been exercised to completion — several were only reached and screenshotted (dialog opened, then Back/Cancel clicked) in an earlier build, with the incompleteness noted only in the coverage log's "Remaining Work" column, not resolved. It took the user explicitly asking "did every action get tested end to end?" to catch this. Completing those flows then and there immediately found a real defect (Reject on one screen returned HTTP 200 "successfully updated" but silently never changed anything — invisible to any check short of actually confirming the action and re-verifying the result).

**Rule**: before reporting a screen's coverage as complete or "no gap," check two things independently, not just one:
1. Does every action/button that exists in the app appear somewhere in the manual or defect log (the row-action inventory checks this)?
2. Was every one of those actions actually carried through to a confirmed result — success message plus a verified state change (status, grid content, downstream screen), not just a dialog reached and cancelled (this file's existing Transaction Testing and Completion Criteria sections already require this; a row-action inventory does not check it)?

If the coverage log has any entry noting an action was "reached but not submitted," "dialog only, cancelled," or similar, treat that as still open — either complete it or get the user's explicit sign-off that it stays a deliberate, permanent exception (e.g. an irreversible action with no disposable test record available) — never let it silently carry forward across a doc rebuild as if it were resolved.

## Completion Criteria

The Playwright walkthrough is complete only when:

- Every in-scope navigation branch has been visited.
- Every static selectable value has been recorded and branch-tested where relevant.
- Dynamic dependencies have been identified and tested representatively.
- Every permitted transaction type has been exercised successfully using appropriate UAT data.
- Required screenshots have been captured and named.
- Remaining exclusions, defects, and blockers are explicitly recorded.
- Coverage claims are supported by evidence.
