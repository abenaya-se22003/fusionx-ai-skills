# Repurposing this skill for a different pillar

`SKILL.md` was built for one specific deck: the FusionX Version Release BA
Meeting deck's **Banking Pillar** section. It is not written generically —
several values are hardcoded because they were verified against that actual
deck and that actual Jira label taxonomy, not assumed. This file exists so
whoever builds `<pillar>-release-update` next knows exactly what to
re-derive for their pillar versus what mechanics carry over unchanged. Don't
copy the pillar-specific values below into a new skill "because they worked
for Banking" — re-verify every one of them against the new pillar's own
deck and Jira data, the same way they were originally verified here.

## Must change — pillar-specific

- **Skill identity.** `name`/`description` in the frontmatter, the title,
  and every "Banking Pillar" mention in prose (When to use, Goal) — rename
  to the new pillar.
- **Module label list (Step 0.3).** The 8 labels
  (`CustomerOnBoardingModule`, `AccountsModule`, `TDModule`, `CashModule`,
  `CommonModule`, `IslamicBanking`, `PaymentModule`, `CollateralModule`) are
  Banking Pillar's actual Jira label taxonomy. A different pillar will have
  a completely different label set — pull it from that pillar's own Jira
  board/project, don't guess from module names that sound similar.
- **Whether the new pillar's Jira project even uses `labels` for module
  attribution.** Every JQL query here (Step 2) assumes `labels = <MODULE>`.
  Confirm the new pillar's project actually models "module" as a label —
  it could be a `component`, a different custom field, or a separate
  project per module instead. Don't reuse the `labels =` clause shape
  without checking.
- **`customfield_10031` (Story Points).** Custom field IDs are usually
  stable across projects on the *same* Jira Cloud site, but not guaranteed
  — confirm it on a real issue from the new pillar's project before reusing
  it, especially if the new pillar lives on a different site than
  `lolcgroupdev.atlassian.net`.
- **`cloudId: lolcgroupdev.atlassian.net`.** Only reuse if the new pillar's
  deck pulls from the same Jira Cloud site.
- **The cross-cutting-label exclusion pattern (Step 2's Islamic Banking
  rule).** Banking Pillar has one category (`IslamicBanking`) whose tickets
  carry a module label *and* their own category label, and gets its own
  slide section pulled via `labels not in (..., IslamicBanking)` everywhere
  else. This is a real, specific fact about Banking Pillar's Jira data, not
  a generic pattern — a different pillar may have no equivalent
  cross-cutting category, or a different one entirely. Re-derive this from
  the new pillar's actual ticket data; don't assume `IslamicBanking` (or
  any exclusion) applies.
- **Card styling table (Step 4).** The exact fonts/colors (`#14243B`,
  `#0E8074`, `#3E4A57`, `#F7F9FB`, Arial) are Banking Pillar's Canva
  template's actual values, read directly off real cards. A different
  pillar's deck almost certainly uses a different template with its own
  colors — read them from a real existing card in the new deck via
  `read-design`, never assume the same palette.
- **Slide-role text anchors (Step 1) and the "MODULE X OF Y" divider
  convention.** Step 1 finds a module's slides by searching page text for
  *Past Release Summary* / *Key Enhancements* / *Upcoming Release Plan* /
  *Major Enhancements* and a divider slide. This only works if the new
  pillar's deck follows the *same* per-module slide-role and divider
  naming convention. If it doesn't, Step 1's search terms need to match
  whatever convention that deck actually uses — inspect a real module
  section in the new deck first.
- **"Leave alone unless asked" list.** *Proposed AI/ML Use Cases* and
  *Documentation & Module Health Status* are Banking Pillar's own
  non-release slide inventory. Check the new pillar's deck for its own
  non-release slides and list them here instead of assuming these two
  names apply.

## Reusable as-is — mechanics, not pillar facts

These carry over to any pillar's deck without modification, because they're
about *how Canva/PowerPoint/Jira behave*, not about Banking Pillar
specifically:

- The dual-target pattern (Canva default, PowerPoint optional, pick one for
  the whole session) and its "PowerPoint (optional)" per-step note
  structure.
- Step 0's overall input-gathering shape (design/file → modules → version
  pair → fixVersion month, asked all at once, never waited-for).
- Step 1's page-ID-vs-index caution — page/slide indices shift on every
  insert/delete, IDs don't (until a PowerPoint file is saved/reopened,
  which regenerates them entirely).
- Step 2's query shape (three queries: planned / delivered / upcoming),
  "sum points across Epics and Stories, treat blank as 0," "attribute by
  `labels` field not summary text," "never derive a corrected total by
  arithmetic on an old cached total — always re-query," and the
  large-response/pagination tool note.
- Steps 3–6's Canva edit mechanics (`open_transaction` →
  `replace_text`/`format_text` → `finalize: commit`; widening a text box
  when a number's digit count grows) and PowerPoint equivalents
  (`getSubstring` index recomputation).
- Step 7's grid-fitting discipline in full: never shrink cards to fit more
  in, add/consolidate/delete continuation slides as the item count changes,
  confirm before any deletion, never confirm before an addition, keep new
  cards' internal offsets identical to the template's.
- Step 8's hyperlink-target-vs-label mismatch check.
- Step 9's verification discipline: check *every* continuation slide of a
  touched section, not just the first; cross-check final numbers against a
  fresh query, never against memory or arithmetic on an earlier total.

## Suggested process for building the new pillar's skill

1. Get (or have the user share) the new pillar's actual Canva design link
   and a sample of its Jira project/board.
2. Walk through every item in "Must change" above against that real data —
   don't fill any of them in from assumption or by analogy to Banking
   Pillar.
3. Copy this skill's structure (steps 0–9, the two-column "Must
   change"/"Reusable" split above) rather than starting from a blank page —
   the *shape* of the process transfers even though the values inside it
   don't.
4. Validate the same way this skill would have been validated: dispatch a
   fresh subagent to actually run it against the new deck/Jira data before
   calling it done, per this repo's usual `superpowers:writing-skills`
   practice (see `HANDOFF.md`'s "Process that worked this session").
