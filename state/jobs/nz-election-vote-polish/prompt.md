Build: vote/ polish from the PR #101 fresh review nits. Worktree .worktrees/nz-election-vote-polish, branch
change/nz-election-vote-polish, stacked on change/nz-election-vote-nits (PR #101, head 76b5126). Commit, never push.

Page plan: intent/nz-election/pages/vote.md. Design: product/nz_election/DESIGN.md (tokens and components; reuse them,
add no new token). Read first: state/design-backlog.md (2026-10-26 "PR #101 fresh review nits" entry), vote_page.py,
styles.css, AGENTS.md, product/nz_election/tests/test_vote_page.py (line 44 area: the first-screen link contract allows
only snapshot action urls before #help; keep it true).

Goal, three things a reader sees on vote/ at 390 and 1280:
1. Deadline paragraphs repeat the same wording and dominate the phone help section. Say each deadline once, in the
   shortest form the EC source supports; no new facts, nothing dropped that the source states.
2. At 1280 the label column leaves whitespace beside long answers. Let label and answer share the width so long answers
   do not run as a narrow column beside empty space (DESIGN.md layout components only).
3. Repeated source wording adds height on mobile. Where several rows cite the same source, credit it once per module
   (module foot, as home.section() does); every row keeps a resolvable source and its aria-describedby target.
Same answers, same links, same page-plan order.

Tests: data, provenance and absence only, never markup, class names or pixel sizes. Tests on origin/main at the base
sha stay untouched; tests this stack added (test_vote_page_credits.py) move with it if a credit consolidates, nothing
weaker (every rendered aria-describedby still resolves, every module still has a source). If an item cannot be stated
as data, say so in last.md; do not add markup pins.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py`
passes except Chromium launches the sandbox denies (list them), `bin/lint` prints lint ok, and last.md lists for each of
the three items what changed and where. The supervisor judges the result by eye from 390/1280 screenshots.
