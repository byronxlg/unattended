Fresh-context review of PR #101 (nz-election-vote-nits), read-only. Worktree .worktrees/nz-election-vote-nits,
branch change/nz-election-vote-nits, head 8eac454, stacked on #100 (4a47034). Diff: git diff 4a47034...8eac454
(vote_page.py, styles.css). Judge against REVIEW.md. Brief: state/jobs/nz-election-vote-nits/prompt.md and
followup-1.md; page plan intent/nz-election/pages/vote.md; design product/nz_election/DESIGN.md.

The change: source credits under the countdown and the key-dates timeline as plain text with retrieval dates
(no links before #help, per main's first-screen contract in test_vote_page.py), help rows in a two-column layout.
Check: every aria-describedby id resolves to an element that exists in every phase (countdown absent, dates absent,
election day, after), the retrieval date shown is the latest of the records actually drawn, no crash on sparse
records (missing retrieved_at, source_url, date), provenance not lost compared with the base, tests check data
and absence not markup. Host ran the browser tests (141 passed incl. Chromium). Do not run pytest; read and probe
with python. Screenshots of the head on live data: /tmp/vn/vote-390.png, /tmp/vn/vote-1280.png (look at them).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
