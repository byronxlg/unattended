Fresh-context review of PR #86 (nz-election-policy-links), read-only. Worktree .worktrees/nz-election-policy-links,
branch change/nz-election-policy-links, head 37fa71a on main 7af8109. Diff: git diff origin/main...37fa71a.
Judge against REVIEW.md, including pass 4 (the question test) against intent/nz-election/pages/electorate.md Q3.

The change links every electorate page to Policy.nz. Policy.nz has no verifiable electorate page (the electorate
paths render 404 in a browser while returning HTTP 200), so each record points at one candidate's profile, which
lists all candidates in that electorate. Check: the destination choice is neutral and the link text honest; every
record's electorate_slug matches a real electorate and its URL path; the validator in pipeline/snapshots.py rejects
malformed or off-domain records and the party rules still hold; no Policy.nz text is reused; no test on main was
weakened (test_electorate_page_plan.py changed one line).
Supervisor host run on 37fa71a: -k "electorate or snapshot or policy" 722 passed, lint ok, live-data build PASS 81
routes with 71 of 71 links, Waiariki 390 link above the fold looked at. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
