# nz-election-home-plan fix-2 (PR #64, host harness)

The supervisor ran your fix-1 (8d84eb5) on the host, where Chromium starts:

- `uv run artifacts/nz-election/fix1/check-review.py`: cf770ea picker EXPECTED FAIL at 360 and 390
  (8.25 and 9.04 px), HEAD `PASS before home 360: 71 links; minimum 26 x 26`, `PASS before methods
  360`, `PASS before home 390`, then stopped:
  `market_checks.py:36 AssertionError: HOME_MARKET_HEIGHT: 926.1875 > 844` on methods/ at 390x844
  (check_page on `/unattended/nz-election/methods/`, build `artifacts/nz-election/before`).
- Home fold at 390 looked at by the supervisor: date line, seat answer, movement sentence and seat
  strip all above the fold. Good; keep it.

Fix: cf770ea moved the markets module from home to Methods (`#markets` there). The 390 height budget
in market_checks.py still binds wherever `#markets` renders, and it stays at 844: make the Methods
markets module fit one phone screen at 390 (it was 733 px on home before the move; fix-1's
market_panel.py wording change may have added to it). Do not edit market_checks.py or lower
MAX_HOME_HEIGHT. Tests on main at de9a7c2 may not be weakened; this branch's own tests may move.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests/test_home_fix1.py product/nz_election/tests/test_home.py product/nz_election/tests/test_home_defects.py product/nz_election/tests/test_home_design.py product/nz_election/tests/test_markets*.py` passes.
- `uv run python -m product.nz_election.pipeline.verify all --site <populated build>` PASS all; `bin/lint` ok.
- Rebuild `artifacts/nz-election/before` with your code. If Chromium starts, run
  `uv run /Users/byron/repos/unattended/state/jobs/nz-election-home-plan-fix-2/check_methods.py $PWD/artifacts/nz-election/before`
  (expect `PASS`) and then `uv run artifacts/nz-election/fix1/check-review.py` (expect exit 0). If it
  cannot start, say so; the supervisor reruns both on the host.
- Commit on change/nz-election-home-plan; do not commit last.md or artifacts/.
