Fresh-context review of PR #82 (nz-election-post-schedules), read-only. Worktree .worktrees/nz-election-post-schedules,
branch change/nz-election-post-schedules, head ca7bec1 on main eb9dcf7. Diff: git diff eb9dcf7...ca7bec1. Judge against
REVIEW.md; read intent/nz-election/plan-week-after.md increment 3 and product/nz_election/runbook.md.

Goal: collection stops on fixed UTC sunsets from one shared module (pipeline/sunsets.py): hourly 7 Nov 06:00Z, night loop
8 Nov 06:00Z, social and daily to 14 Nov; workflows (hourly, daily, social daily, pages) gate on the window and never spend
paid credits (X, Jev) after their sunset, including retries and classification; a late run exits 0 without a failure row;
home and vote/ switch to past-tense copy after 7 Nov 06:00Z; the s197 freeze is not weakened.

Check: every workflow and Python path reads the same constants (no duplicated literals); boundary instants (exactly at the
sunset, one second before) behave as documented; paid transports cannot be reached after the social sunset by any entry
point; the three base tests changed (test_workflows hourly contract, test_daily_workflows schedule, test_look_followup caption)
moved only with the new contract and nothing weaker; post-election copy has no stale future tense. Do not run pytest; read and
probe (small python -c probes are fine).

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
