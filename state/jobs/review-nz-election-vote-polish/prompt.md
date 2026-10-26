Fresh-context review of PR #102 (nz-election-vote-polish), read-only. Worktree .worktrees/nz-election-vote-polish,
branch change/nz-election-vote-polish, head f728f4d, stacked on change/nz-election-vote-nits (PR #101). Diff:
git diff origin/change/nz-election-vote-nits...HEAD (vote_page.py, styles.css, DESIGN.md, test_vote_page_credits.py).
Judge against REVIEW.md. Brief: state/jobs/nz-election-vote-polish/prompt.md; page plan intent/nz-election/pages/vote.md;
design product/nz_election/DESIGN.md.

The brief asked: each deadline said once in the shortest form the EC source supports (no new facts, nothing the source
states dropped); help label and answer share the width at 1280; one credit per module. Check in particular that the
hard-coded deadline_phrases in vote_page.py agree with the EC records they replace (the `at` times and the summaries in
product/nz_election/snapshots/voting.json), that a deadline skipped as already shown is still stated somewhere visible on
the page in every phase (before/after enrolment close, advance, election day, after), that every aria-describedby id
resolves, that sparse records (missing at, date, source_url, retrieved_at) do not crash, and that tests check data and
absence, not markup. Host ran the vote and design tests: 147 passed incl. Chromium; vote/ 390/1280 looked at.
Do not run pytest; read and probe with python.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
