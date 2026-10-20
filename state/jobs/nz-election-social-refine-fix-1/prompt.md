# Fix-1 on PR #56 (fresh review, one Important)

The spent budget day exits 0 from the collector, but the status row keeps `error_code='SOCIAL_CREDIT_CAP'`,
and `.github/workflows/nz-election-social-daily.yml:62-65` then runs `publish.py --family social`, which
raises `FAIL refresh: handled failure status published` (publish.py:224-227) for any non-null error_code.
So the reserve job is still red on a spent day, which is the defect this change exists to fix.

Fix: carry the benign spent-day distinction through publication. You choose the shape; the invariants:
- A spent budget day (no reservation, nothing paid this run) ends with the workflow green and the status row
  published honestly (the reader sees the day's budget is spent and when data last arrived).
- A cap hit mid-run (credits spent this run, collection incomplete) stays a failure: the publisher still
  exits nonzero for it. Do not weaken the publisher's check for any other error code or family.
- Read where status error codes are consumed before choosing (publish.py status_of, export/verify, the
  site's status rendering, content checks) so nothing downstream starts showing the benign case as a failure
  or the fatal case as fine.

Tests: add coverage at the publisher/workflow level that fails on the current branch head: spent-day status
-> publisher exits 0; mid-run cap status -> publisher still exits nonzero. Tests on main at base sha 6afc912
are not edited except where the registered contract moves with this item; the branch's own tests move with it.
Update runbook.md:213 so the clean-exit claim is true end to end.

Done: `uv run --with pytest pytest -q product/nz_election` passes, `bin/lint` ok, the new publisher test
shown failing on the current head and passing after. Commit in the worktree; do not commit last.md.
