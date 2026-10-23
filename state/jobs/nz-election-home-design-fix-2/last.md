Committed `b6563b0`; not pushed.

Updated chart rendering, CSS, and tests: stale endpoints stop at their observation date, markers retain their shape, and dates align with plotted positions.

Verification:
- `uv run --with pytest pytest -q`: `759 passed in 304.95s`
- `bin/lint`: `lint ok (496 text files)`
- Build: 79 routes; `verify.py all`: `PASS all`

Chromium remains blocked by sandbox permissions. Static marker ratio is 1.00; the browser measurement and harness PASS remain outstanding.

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-design/last.md) records the commit, failing-then-passing regression, and host instructions. Report and artifacts remain uncommitted.