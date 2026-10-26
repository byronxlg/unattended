Build: vote/ layout nits from the PR #99 second fresh review. Worktree .worktrees/nz-election-vote-nits, branch
change/nz-election-vote-nits, stacked on change/nz-election-vote-enrolment (PR #100, head 4a47034, main merged in).
Commit, never push.

Page plan: intent/nz-election/pages/vote.md. Design: product/nz_election/DESIGN.md (tokens and components; reuse them,
add no new token). Read first: state/design-backlog.md (2026-10-27 entry, second bullet), vote_page.py, styles.css,
AGENTS.md.

Goal, three things a reader sees on vote/ at 390 and 1280:
1. The source credit for the countdown and timeline sits far below them. Put each module's source line in its own
   module foot (home.section() already does this) so a reader sees where the dates come from next to the dates. The
   complete snapshot credit may stay in div.source-note.
2. The help rows ("Overseas or need help voting?") leave large empty gaps under short answers at 1280. Let rows size to
   their content (no equal-height grid cells that stretch short answers).
3. Long deadline lines compete with the instructions. Make deadline lines secondary to the instruction they belong to
   (DESIGN.md's dek or meta style, not a new one), still readable at the 16 px reading floor.
No content added or removed; same answers, same links, same order (the page plan sets the order).

Tests: data, provenance and absence only, never markup, class names or pixel sizes. If none of the three can be stated
as data (each module still has a source link; every deadline still renders), say so in last.md; do not add markup pins.
Tests on origin/main stay untouched.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py`
passes except Chromium launches the sandbox denies (list them), `bin/lint` prints lint ok, and last.md lists for each of
the three items what changed and where. The supervisor judges the result by eye from 390/1280 screenshots.
