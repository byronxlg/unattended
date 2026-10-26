Build: vote/ enrolment copy after the enrolment close. Worktree .worktrees/nz-election-vote-enrolment, branch
change/nz-election-vote-enrolment, stacked on change/nz-election-vote-design (PR #99, head 1406aff). Commit, never push.

Page plan: intent/nz-election/pages/vote.md. Design: product/nz_election/DESIGN.md (tokens and components; no new styles
unless the copy needs none of the existing ones). Read first: state/design-backlog.md top entry, the vote page module
(vote_page.py on this branch), snapshots/voting.json and its loader, AGENTS.md.

Goal: on 27 Oct the "Am I enrolled, and is it too late?" answer still says "Enrol or update your details by midnight at
the end of 25 October". Once the enrolment close in voting.json has passed (build clock, the same clock the page already
uses for phases), the answer is in the past tense and says what a reader who missed it can still do, only what the EC
sources in voting.json state (with their links); if the snapshot states nothing for that case, say only that the close has
passed and link the EC page already cited. Before the close nothing changes. No date or rule invented; no "not available"
text.

Tests: data and absence, not markup or class names. One test builds vote/ at a clock before the close (copy unchanged),
one after (past tense, no future-tense close sentence, every link has a source). New tests fail on 1406aff. Existing
tests on main at origin/main stay untouched; this branch's own tests may move if the contract moves.

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_vote_page*.py product/nz_election/tests/test_design.py`
passes except Chromium launches the sandbox denies (list them), `bin/lint` prints lint ok, and last.md quotes the vote/
answer text before and after the close as the build produces it.
