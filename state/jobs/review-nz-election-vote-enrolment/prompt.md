Fresh-context review of PR #100 (nz-election-vote-enrolment), read-only. Worktree .worktrees/nz-election-vote-enrolment,
branch change/nz-election-vote-enrolment, head 06a1a8b, stacked on #99 (1406aff). Diff: git diff 1406aff...06a1a8b.
Judge against REVIEW.md. Brief: state/jobs/nz-election-vote-enrolment/prompt.md; page plan intent/nz-election/pages/vote.md;
data product/nz_election/snapshots/voting.json (EC sources).

The change: after the sourced enrolment close, vote/ says the close has passed and links the EC enrolment source instead
of the update-your-details call; before the close unchanged. Check: the boundary (row `at` instant vs date fallback,
timezone), every place the enrolment-close summary is printed (main section and help deadlines) turns at the same
instant, no claim beyond what voting.json's EC sources state, missing fields (no `at`, no source_url) do not crash or
show stale copy, provenance kept, tests check data and absence not markup. Host ran the browser tests (135 passed). Do
not run pytest; read and probe with python. Screenshots of the base at 6 Nov eve: /tmp/vd99/shots/eday-390-light.png.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
