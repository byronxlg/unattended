Third fresh-context review of PR #82 (nz-election-post-schedules), read-only. Worktree .worktrees/nz-election-post-schedules,
branch change/nz-election-post-schedules, head 8951028 on main eb9dcf7. Full diff: git diff eb9dcf7...8951028; latest fix
rounds: git diff a8b74ff..8951028. Judge against REVIEW.md; read intent/nz-election/plan-week-after.md increment 3 and
product/nz_election/runbook.md.

Goal: collection stops on fixed UTC sunsets from one shared module (pipeline/sunsets.py): hourly 7 Nov 06:00Z, night loop
8 Nov 06:00Z, social and daily to 14 Nov; workflows gate on the window and never spend paid credits after their sunset;
a late run exits 0 without a failure row; home, vote/ and night/ switch to past-tense copy after 7 Nov 06:00Z; the s197
freeze is not weakened.

The second review asked for three items; check each is fixed and nothing regressed:
1. night/ HTML, its route card and the live package carry no "due 27 November" once that date has passed (including
   cached client notices);
2. after the social sunset, --check-freeze allows publication of what was collected (outside the s197 freeze) while
   collection stays refused;
3. no claim that official results are published unless an official provenance source exists (result_sources.py).
Also: main's result_states_browser.py assertion that pinned 'due 27 November' at a 28 Nov clock was authorized to move
in fix-3 (contract moved); no other test on main at eb9dcf7 should be weakened. Do not run pytest; read and probe.
Supervisor host run on 8951028: 273 passed across sunsets/workflows/daily/social/result-states/night incl. host Chromium,
lint ok.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
