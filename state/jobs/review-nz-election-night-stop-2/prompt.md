Second fresh-context review of PR #80 (nz-election-night-stop), read-only. Worktree .worktrees/nz-election-night-stop,
branch change/nz-election-night-stop, head 4c997ab on main bd53141. Whole change: git diff bd53141...4c997ab; the fix
round alone: git diff 95387fe..4c997ab. Judge against REVIEW.md; read intent/nz-election/plan-week-after.md increment 1
(bounded stop) and product/nz_election/runbook/night.md.

The first review's Important: web/night-live.mjs learned the cutoff only from a good response, so it polled past the
cutoff when offline, on resume, or on a first visit after the cutoff. Fix: night_page.py embeds the shared Python cutoff
in the generated page and the client reads it before its first tick.

Check: the embedded value comes from the one shared constant (no second copy); zero requests are made after the cutoff
on first visit, offline, failures and tab resume; before-cutoff behaviour is unchanged; the new tests in
test_night_stop_bootstrap.py would fail on the old client; nothing weakens an existing check.
Host on 4c997ab: test_night_stop_bootstrap.py, test_night_operation.py, test_night_page.py 101 passed incl. Chromium;
the five new tests fail on 95387fe; bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
