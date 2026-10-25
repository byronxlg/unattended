Second fresh-context review of PR #82 (nz-election-post-schedules), read-only. Worktree .worktrees/nz-election-post-schedules,
branch change/nz-election-post-schedules, head a8b74ff on main eb9dcf7. Full diff: git diff eb9dcf7...a8b74ff; fix round:
git diff ca7bec1..a8b74ff. Judge against REVIEW.md; read intent/nz-election/plan-week-after.md increment 3 and
product/nz_election/runbook.md.

Goal: collection stops on fixed UTC sunsets from one shared module (pipeline/sunsets.py): hourly 7 Nov 06:00Z, night loop
8 Nov 06:00Z, social and daily to 14 Nov; workflows gate on the window and never spend paid credits (X, Jev) after their
sunset, including retries and classification; a late run exits 0 without a failure row; home and vote/ switch to past-tense
copy after 7 Nov 06:00Z; the s197 freeze is not weakened.

The first review asked for four Important items; check each is fixed and nothing regressed:
1. the social paid guard must use the run's real clock, not a fixed/default clock;
2. a run crossing the social sunset mid-collection must stop cleanly, not report SOCIAL_UPSTREAM_FAILED;
3. the night-loop cutoff must come from sunsets.py, not a literal in night_live.py;
4. no "due 27 November" (or other future-tense official-results) copy once that date has passed.
Also: every workflow and Python path reads the same constants; boundary instants (exactly at a sunset, one second before)
behave as documented; tests on main at eb9dcf7 moved only where the contract moved. Do not run pytest; read and probe
(small python -c probes are fine). Supervisor host run: 403 passed across sunsets/workflows/daily/social/result-states/night,
new test_sunsets cases fail on ca7bec1, lint ok.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
