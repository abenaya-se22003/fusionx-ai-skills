---
name: banking-pillar-release-update
description: Update the FusionX Banking Pillar release deck with live Jira data for a given module and release version pair. Runs against a Canva design by default; a PowerPoint file is an optional alternate target.
---

# Banking Pillar Release Update

Refresh one module's release slides in the FusionX Version Release BA Meeting deck from live Jira data.

> Built specifically for the Banking Pillar's deck, module labels, and card
> styling. If you're adapting this for a different pillar's release deck,
> read `references/repurposing-for-other-pillars.md` first — it lists
> exactly what's pillar-specific versus reusable as-is.

## When to use

Trigger on: "update the deck for \<module\>", "refresh \<module\> module slides", "run the release update for TDModule", "update slides 31-34 for Cash and Teller", or any request to pull Jira story points / epics into this deck's per-module release slides.

## Goal

The module's slides show story point totals and Epic/Story counts that match Jira exactly, and one correctly-sized enhancement card per real ticket — no placeholders, no leftover cards, no stale text, and every hyperlink resolving to the ticket its label names.

## Target platform

This skill runs against a **Canva design by default**. A PowerPoint file is supported as an optional alternate target only when the user explicitly asks for it (e.g. they upload a `.pptx` instead of giving a link, or say "do this in PowerPoint/Office instead"). Every step below gives the Canva mechanics first; where the PowerPoint mechanics differ, they're called out in a "PowerPoint (optional)" note at the end of that step. Don't run both — pick one target for the whole session based on step 0.

## Steps

### 0. Collect the inputs by asking — always the first action

Five values are needed: the target Canva design, the Jira module label(s), the past (delivered) version, the upcoming version, and the fixVersion month string.

**Never** open with a message saying you're waiting on details, and never wait for the user to volunteer them. Immediately gather them yourself:

1. **Get the Canva design.** If the user's message already contains a `canva.com/design/...` link, extract the design ID from it (the path segment right after `/design/`) and use that directly — don't ask again. If no link was given, ask for it: "What's the Canva link for the deck?" A design ID pasted alone (no full URL) is also fine. Only if the user explicitly says they want to work in PowerPoint instead should you skip this and ask for the `.pptx` file upload instead.
2. **Read the deck first** so the version options are concrete: call `mcp__Canva__read-design` with `filter.fields: ["design_content"]` over a broad page range (or the whole design_metadata page count first, then a few representative pages) to see which module sections currently exist and which version numbers appear on their *Past Release Summary* / *Upcoming Release Plan* slides.
3. Then ask the user (a single set of questions, or `ask_user_input_v0` where the options fit its format):
   - **Module(s)** — multi-select over all 8 labels: `CustomerOnBoardingModule` (Customer Onboarding / COB), `AccountsModule` (Account / CASA), `TDModule` (Term Deposit / TD), `CashModule` (Cash & Teller), `CommonModule` (Common Settings), `IslamicBanking` (Islamic Banking), `PaymentModule` (Payment), `CollateralModule` (Collateral). The user may pick more than one module to update in the same run.
   - **Version pair** — free-text, not preset options. Show the deck's current version pair as a hint (e.g. "Deck currently shows Past V65 → Upcoming V67") and let the user type the actual pair to use.
   - **fixVersion month** — free-text, not preset options. Show the deck's current month as a hint (e.g. "Deck currently shows July 2026") and let the user type the actual month to use.

If the user already supplied some values in their request, only ask for the gaps.

**Rule:** Never infer the version numbers silently from what's on the slides — they're usually stale, which is why the deck is being updated. Confirm them.

**Rule:** When multiple modules are selected, apply steps 1–9 once per module, end to end, before moving to the next — never batch step 1 across all modules then step 2 across all modules. Each module's slides get fully updated and verified before starting the next.

**Done when:** the target design is identified, and all values are confirmed by the user for every selected module.
**Produces:** `design_id` (Canva) or an open PowerPoint file (optional path), `module_labels` (list), `past_version`, `upcoming_version`, `fixversion_month`.

### 1. Locate the module's slides by content

Read page content to find them — call `mcp__Canva__read-design` with `filter.fields: ["design_content"]` across candidate page ranges, looking for the module name and the slide roles in each page's text: *Past Release Summary*, *Key Enhancements*, *Upcoming Release Plan*, *Major Enhancements*. A module's own divider slide (its "MODULE X OF Y" section start) is the fastest anchor — its neighboring pages are that module's other slides in a fixed order.

**Rule:** Never trust a page index carried over from earlier in the same session, from an earlier message, or from your own memory of "where this module was last time." Every `insert_pages`, `delete_pages`, or continuation slide added anywhere earlier in the deck shifts every page index after it. Re-read the current `design_content` for the specific page index you're about to edit immediately before editing it — don't assume a page number is still what it was even one tool call ago if anything was inserted or deleted in between. Page **IDs** (the long `PBxxxx...` string) are stable once you have them from a read within the same uninterrupted sequence; page **indices** are not.

**Rule:** Never overwrite a page holding a different module's content. Duplicated template pages often keep another module's text; confirm the module from the page's own content first.

**Done when:** each target page is identified by its current `page_id` *and* its content confirms which module and slide role it is.

**Produces:** current page IDs and indices, and the `locator_id` for each element you'll write (format `<page_id>-<element_id>`, read from the `design_content` response).

**PowerPoint (optional):** get the slide list via `execute_office_js`, then read the first few text shapes per slide looking for the same module name and slide roles. The same page-ID-vs-index caution applies even more strongly here — PowerPoint slide IDs regenerate entirely if the file is saved or reopened, and a stale ID throws `GeneralException` on `SlideCollection.getItem`. Re-read before every edit batch.

### 2. Pull the Jira data

cloudId is `lolcgroupdev.atlassian.net`. Story points live in `customfield_10031`.

Run three queries via `mcp__Atlassian_Rovo__searchJiraIssuesUsingJql`:

| Metric | JQL |
|---|---|
| Planned Story Points | `labels = <MODULE> AND fixVersion = "<MONTH YEAR>" AND labels not in (hotfixed, IslamicBanking)` |
| Delivered (past) | `labels = <MODULE> AND labels = Version_<PAST> AND labels not in (hotfixed, IslamicBanking)` |
| Upcoming | `labels = <MODULE> AND labels = Version_<UPCOMING> AND labels not in (hotfixed, IslamicBanking)` |

**Rule:** Islamic Banking tickets carry the `IslamicBanking` label *in addition to* whichever module they touch (e.g. a TD product-definition ticket also tagged `IslamicBanking`), because Islamic Banking is implemented as integration work across every module's Jira data. But it's presented as its own separate module slide section — so exclude `labels not in (..., IslamicBanking)` from every module's queries *except* when `<MODULE>` being updated is `IslamicBanking` itself, where you run the same three queries with `labels = IslamicBanking` and no exclusion. If a module was updated in a prior run before this exclusion existed, re-pulling its data now will change its ticket set — when that happens, re-check every slide in every section for that module (see step 9's full-section sweep rule), not just the slide you originally touched.

**Rule:** The two Planned metrics on the Upcoming Release Plan slide come from *two different queries* — "Planned Story Points (\<month\>)" is the fixVersion total, "Planned Story Points (\<Vxx\>)" is the Version-label total. Never mirror one into the other, even when they happen to be equal.

**Rule:** Sum story points across **both** Epics and Stories. Treat a blank/null `customfield_10031` as 0. Count Epics and Stories separately for the count fields.

**Rule:** Attribute every ticket to a module strictly by its `labels` field, never by reading the module name out of its summary text. A ticket's summary can reference another module by name (e.g. a `CommonModule`-labeled ticket titled "... Dashboard - TD | Post-EOD Monitery Dashboard") without actually belonging to that module — the JQL query result is authoritative, the English description is not. When pulling a card's content from search results, double check the ticket's `labels` array (not just its summary) matches the module currently being updated.

**Rule:** When a rule change (like the Islamic Banking exclusion) requires updating a total that was already computed in an earlier run, re-run the query with the new filter and use its result directly — never derive the corrected number by adding or subtracting from the old cached total. Arithmetic on a previous total silently carries forward any error in that original number, and there's no way to catch it without the fresh query anyway.

**Tool note:** this connector ignores the `fields` parameter and returns full ticket descriptions regardless, so responses are enormous. Use `maxResults` of 2–5 and paginate via `nextPageToken`, checking `isLast`. If an Excel peer has shared a CSV export of the fixVersion bucket, filter that locally with `bash` + `grep` instead — far cheaper than paginating the API.

**Done when:** you have, for each query: total points, Epic count, Story count, and per-ticket key + summary + description — with Islamic Banking tickets excluded from every non-Islamic-Banking module's results.

**Produces:** the numbers for step 3 and the card content for steps 4 and 6.

### 3. Past Release Summary slide

Update the title's month and version, Planned Story Points, Delivered Story Points, Epics (Count), Individual Stories (Count).

Open a transaction with `mcp__Canva__read-design` (`open_transaction: true`) on the target page to get its current `design_content` and a `transaction_id`. Use `mcp__Canva__edit-design` with `type: "replace_text"` operations against each value's `locator_id`, then `finalize: "commit"` once the returned thumbnail confirms the change. For a number that grows past its previous digit count (e.g. 2 digits → 3), check whether its text box is wide enough not to wrap — widen and reposition (keeping the same right edge if it's right-aligned) if it does.

**Done when:** all four metrics and the title version/month read back correctly in the post-edit thumbnail.

**PowerPoint (optional):** use `getSubstring(index, length)` for surgical swaps inside a longer string (e.g. changing only `May 2026, V61` inside a title). Recompute the index from freshly-loaded text between sequential substring edits on the same shape — a stale index corrupts the string.

### 4. Key Enhancements — one card per delivered ticket

Each card in the current template carries: numbered badge, category tag, bold title, description paragraph, and a ticket link.

Card styling standard (Arial throughout):

| Element | Spec |
|---|---|
| Badge number | 18pt bold, `#FFFFFF`, in a `#14243B` circle |
| Category tag | 18pt bold, `#0E8074` |
| Title | 24pt bold, `#14243B` |
| Description | 18pt regular, `#3E4A57` |
| Ticket link | 18pt bold, `#0E8074`, underlined, text `View ticket → PF-xxxxx` |
| Card background | `#F7F9FB` fill |

**Rule:** The category tag names the item's *functional theme* (e.g. "TELLER TRANSACTIONS", "MONITORING & OVERSIGHT"), never the module name repeated on every card.

**Rule:** Write descriptions from the ticket's own Purpose/Scope, condensed to 1–2 sentences. Never fabricate an item to fill an empty slot.

Set the ticket link's target with a `format_text` operation carrying `formatting.link: "https://lolcgroupdev.atlassian.net/browse/<PF-xxxxx>"` on that text element — do this in the same edit batch as setting its display text so the two never drift apart.

**Done when:** every delivered ticket has a card with all five elements present, no card is missing its description, and every link's `formatting.link` matches the PF-number shown in its own text.

### 5. Upcoming Release Plan slide

Update the title version, the objective paragraph (written from the upcoming tickets' scope), both Planned Story Points metrics, and the Focus Areas list.

When there are more tickets than Focus Area slots, either add a compact pill per ticket (shrinking pill height/font and growing the Focus Areas card's own height to fit — this is the one place in the deck a denser layout within a single card is preferred over adding a continuation slide, since these are short one-line tags, not full cards) or, if grouping is a better fit for very closely related tickets (e.g. paired Core Product + Main Product epics under one "Business Unit Segregation" theme), group them — but never drop a ticket to fit.

**Done when:** both metrics match their respective queries and every upcoming ticket is represented in a Focus Area.

### 6. Major Enhancements slide

One block per upcoming ticket: bold theme title plus a description from the ticket. Same styling standard as step 4.

**Rule:** This is a complete list, not a highlights reel. Never pick a "top N by story points" subset and drop the rest — every upcoming ticket gets its own block, full stop. If the slide's current layout only has 1–2 slots, that is a sign the card count needs to grow (and possibly the slide count too, per step 7), not a cue to select which tickets matter most.

**Done when:** each upcoming ticket has a block, and the title's version/month is correct.

### 7. Fit the content to the item count

Card count *and slide count* vary per release — Key Enhancements, Major Enhancements, and Proposed AI/ML Use Cases can carry one item or several, and the slide's fixed grid (e.g. a 2-card or 3-card layout) will not always hold the current item count. When the grid has too many slots, remove the extras; when it has too few, add a continuation slide at the template's normal card size — never shrink cards to force extra items onto one slide, and never silently drop items to fit the existing layout.

**Fewer tickets than slots (this slide has more slots than items):**
- Remove the extra card slots (background, divider, badge circle, badge number, and all text shapes for that card) and redistribute the remaining cards' heights/positions to fill the space evenly.
- If an entire slide's slots are now unused (e.g. a continuation slide from a previous release cycle with zero items this cycle), delete the whole slide rather than leaving it blank or stale.
- If a section that used to need continuation slides now fits back on the original slide (item count dropped), consolidate back onto the one slide and delete the continuation(s) — don't leave a slide half-populated when its content could live on the previous slide instead.

**More tickets than slots (this slide's grid can't hold everything):**
- Never shrink the card layout to squeeze extra items onto the same slide — a denser grid degrades readability and defeats the point of a fixed template.
- Instead, duplicate the slide as a continuation immediately after the original, following the deck's existing pattern for continuation slides (matching header style, e.g. "Part 2" or an incremented item numbering), and split the items across both slides at the template's normal card size.
- Never leave items out silently because the grid was full — add a continuation slide, but always place every item somewhere.

**Either direction:**
- Keep every new card's internal offsets identical to the template's originals: same `left`, same gap from its divider line to its first text element, same spacing between elements — don't invent a tighter spacing to fit more in.
- When adding a card via cloning, verify the title fits on one line at the template's card width before moving on — a wrapped title will overlap the description below it if the description's position wasn't adjusted for the wrap. Widen the title box or shift the description down; don't leave a collision.

**Confirm first:** list exactly which card slots or whole slides would be deleted, and wait for approval before deleting — this isn't recoverable once the session moves on. Adding cards or slides to cover every item doesn't need this confirmation, since nothing is lost by adding.

**Canva mechanics for a continuation slide:** use `mcp__Canva__merge-designs` with `type: "insert_pages"`, `source: {type: "design", design_id: <this same design_id>, page_numbers: [<the template page's CURRENT index>]}`, `after_page_number: <that same current index>` — this duplicates the page with all its styling intact. Re-read the current index of the template page immediately before this call (per step 1's rule); a stale index duplicates the wrong page. After duplicating, read the new page's `design_content` to get its fresh `locator_id`s before editing it — a copy gets new element IDs, not the original's. To delete a page (the "fewer tickets" case), use `merge-designs` with `type: "delete_pages"` and the page's current index; this always needs the explicit "I approve the deletion" confirmation flow before it will run.

**Canva mechanics for adding a card without a new slide** (e.g. shrinking Key/Major Enhancements from N to fewer, or growing Focus Areas per step 5): use `insert_shape` for the new card's background/divider/badge shapes and `add_text` for its text, then a follow-up `format_text` pass — new shapes/text from `insert_shape`/`add_text` come in with default styling (black, 16px, no bold), never matching the template automatically. Always format them to match a sibling card in the same batch or the very next one.

**Rule:** Check container and background shapes for text, not just the obvious text shapes. Card background rectangles in this deck sometimes hold stale content from an older release that renders underneath the real text and looks like garbled overlap.

**Done when:** card count equals ticket count on every slide for that section (with continuation slides added, consolidated, or removed as needed), and all cards share identical internal offsets.

**PowerPoint (optional):** `addTextBox` output carries default internal margins and a paragraph indent that template shapes don't have. Zero all four `textFrame.margin*` values **and** set `paragraphFormat.leftIndent = 0` and `firstLineIndent = 0`, then match the sibling shape's `left` exactly. Duplicate slides via the slide collection's duplicate method rather than rebuilding from shapes.

### 8. Verify hyperlink targets

For every ticket link, confirm the hyperlink's actual target matches the PF-number in its visible label. The display text and the underlying link can disagree — a card reading `PF-50505` can be wired to a different ticket entirely.

In the `design_content` returned by `read-design`, each text element's `formatting.link` field is its actual target — read it directly rather than assuming it matches the visible text. Fix any mismatch with `format_text` and `formatting.link` set to `https://lolcgroupdev.atlassian.net/browse/<the PF number shown>`.

**Done when:** every card's link target and label reference the same ticket.

### 9. Verify and report

For every page touched, do a fresh `read-design` (or use the thumbnail returned by your last `edit-design` call on that page) and visually check it: no overlapping text, no wrapped titles colliding with descriptions, no leftover default-styled (black/16px) text from a shape you added, and every number/label matches what step 2 produced.

**Rule:** A "section" (Key Enhancements, Major Enhancements, Proposed AI/ML Use Cases) can span more than one slide once step 7 has added continuation slides — in this deck or a past run of it. Before marking a section done, explicitly check whether it has continuation slides (look for the same title/header repeated on the next slide, or a "Part 2" pattern) and verify **all** of them, not just the first one you land on or the one you happen to already have open. Fixing slide one of a section and calling the section done is the same mistake as fixing one card and calling the slide done — it silently leaves stale content behind. This applies with extra force whenever a rule change (e.g. the Islamic Banking exclusion in step 2) alters which tickets belong in a section that already has continuation slides from a prior run — re-check every slide in that section against the new ticket set, not just the one the original edit touched.

**Rule:** Cross-check every number against a *fresh* Jira query result before reporting it as final, never against a number you calculated by adding/subtracting from an earlier total (see step 2's rule) or against your own memory of what a slide "should" say from earlier in the session. Page content can be stale relative to your own notes just as easily as it can be stale relative to Jira.

Report per slide: which metrics changed to what, which tickets became which cards, and anything deliberately left alone.

**PowerPoint (optional):** run `verify_slides` on every slide touched. It measures against an assumed 960x540 canvas, which is wrong for this deck — its *overflow* warnings are noise; only shape-vs-shape *overlaps* are meaningful, and even then thin accent bars overlapping card frames by ~5pt and badge circles straddling divider lines are intentional design. If screenshot tools fail (`verify_slide_visual` / `getImageAsBase64` need PowerPointApi 1.8+, which some clients cap below), say so plainly and ask the user to eyeball the slides — don't claim visual verification you couldn't perform.

## Leave alone unless asked

*Proposed AI/ML Use Cases* and *Documentation & Module Health Status* slides track separate backlog/status items, not release metrics. Don't rewrite their content as part of a release update. If asked to update them, apply the same adaptive card rules from step 7, and fix any stale release reference (e.g. a leftover "February release") to the current version.
