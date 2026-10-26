Second fresh-context review of PR #99 (nz-election-vote-design), read-only. Worktree .worktrees/nz-election-vote-design,
branch change/nz-election-vote-design, head 1406aff. Diff: git diff origin/main...1406aff. Judge against REVIEW.md
(pass 4 included). Brief: state/jobs/nz-election-vote-design/prompt.md; page plan intent/nz-election/pages/vote.md;
design product/nz_election/DESIGN.md. Previous review: state/jobs/review-nz-election-vote-design/last.md.

Fix-1 (1406aff) claims: sparse snapshots keep every question heading and exactly one h1; populated rendering unchanged;
92 regression cases. Check the previous findings are fixed, the populated output did not change, and nothing new: no
words, links, dates or provenance lost in any phase; absent data stays absent; question order holds; new tests check
data, headings and absence, not markup or class names. Host already ran the browser tests (132 passed). Do not run
pytest; read and probe. Screenshots of the pre-fix page: /tmp/vd-shots/vote-390.png, vote-1280.png.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
