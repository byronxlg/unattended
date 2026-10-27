# nz-election-parties-credit (build, stacked on change/nz-election-funding-page, PR #105)

Page plan: intent/nz-election/pages/parties.md (and intent/nz-election/pages/home.md for item 2).
Design: product/nz_election/DESIGN.md (tokens and components; do not add new ones unless DESIGN.md is updated with them).

Goal: two presentation defects seen by the supervisor in screenshots at 390 px (state/design-backlog.md).

1. parties/ at 390: the portrait credit block ("New Zealand Labour Party. CC BY-SA 4.0. Square crop, resized to 320
   pixels and converted to WebP.") sits between the leader and the polling number, ahead of the party's answer.
   Move the credit to one small line after the card's answer (or with the page's source notes); the processing
   note ("Square crop, resized ...") is not reader copy: keep it in the snapshot/Methods record, not on the card.
   Licence and author must stay visible on the page for every portrait (attribution is a licence condition).
2. Home "Where do the parties stand?" cards at 390: the share wraps ("28.5" then "%" on its own line) and the
   change wraps ("-0." then "4"). A number and its unit/sign never break; the card layout at 390 keeps share and
   change readable (stacking them is fine). Check the same component wherever else it renders (parties/).

Read first: AGENTS.md, DESIGN.md, the parties page module and the home party-card markup/CSS (rg "portrait" and
the card class in product/nz_election), REVIEW.md pass 4.

Constraints: tests check data, provenance, absence and accessibility, never markup, class names or byte counts.
Tests on origin/main may move only if they pin the exact markup being changed; say which and why. Do not touch
funding files beyond what a rebase needs.

Definition of done:
- A test that fails on the base (change/nz-election-funding-page 3dcc564) and passes after: every portrait's
  licence text appears after (in document order) the party's poll share on parties/; and no share or change value
  on home/parties contains a breakable space between number and unit (or use the browser harness at 390 to
  assert the value fits one line).
- uv run --with pytest pytest -q product/nz_election/tests -k "parties or home or design" (list any
  sandbox-denied Chromium launches), bin/lint prints "lint ok". Commit in the worktree, report the sha. Do not push.
