# nz-election-seat-sum: does the home seat projection add up?

Goal: the deployed home page (built on origin/data, 26 Oct) shows Opposition 59, Government 67 and TOP 7 seats with
67 needed for a majority. That is 133 seats. A 120-seat House plus overhang should not reach 133 from party-vote
polling alone, and 67 for a majority implies a 132 or 133 House. Find out whether this is correct Sainte-Lague with
overhang under the current electorate assumptions, or a defect (double counting electorate seats, TOP counted
outside the blocs and inside a total, Others remainder allocated seats, a threshold or coat-tail rule misapplied).
Election night reads the same arithmetic, so it has to be right before 7 November.

Read first: AGENTS.md; product/nz_election/pipeline/seats.py, allocator.py, coalitions.py, home.py,
home_graphics.py (majority_cards); the seats/coalitions tests; intent/nz-election/spec.md on seat projection;
the latest data/ seats and polls files on origin/data (git show origin/data:product/nz_election/data/...).

Do:
1. Reproduce the numbers from origin/data with the pipeline functions and write down the allocation table (party,
   party vote share, electorate seats assumed, list seats, total, overhang) in last.md.
2. If it is correct, say why in last.md with the arithmetic and add one test that pins the invariant you checked
   (House size = 120 + overhang; majority = floor(House/2)+1; blocs plus non-bloc parties sum to House size). No
   UI change.
3. If it is a defect, fix it in the pipeline with that same invariant test failing on origin/main and passing on
   your branch; tests on origin/main may move only where they encoded the defect, and say which in last.md.
   No markup or copy changes beyond what the corrected numbers need; no new routes.

Constraints: worktree .worktrees/nz-election-seat-sum, branch change/nz-election-seat-sum; commit, never push.
Do not touch funding, night_page.py or nav (open PRs #104, #105).

Done when: `uv run --with pytest pytest -q product/nz_election/tests -k "seat or coalition or allocator or home"`
passes (browser cases the sandbox denies are listed by name), `bin/lint` prints lint ok, and last.md has the table,
the verdict (correct or defect), and the invariant test name.
