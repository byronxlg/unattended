Committed `7224985`. No push. Detailed records moved to Methods; attribution stays adjacent. All fragment IDs retained; home HTML unchanged.

Verification:

- `uv run --with pytest pytest -q product/nz_election`  
  `676 passed in 290.95s (0:04:50)`
- `verify.py all --site /tmp/nz-provenance/site`  
  `PASS all`
- `bin/lint`  
  `lint ok (498 text files)`
- No-Chromium provenance check: passes 72 routes; fails on base.

Details in [last.md](last.md), uncommitted. Chromium launch was blocked by sandbox permissions; screenshots and browser checks remain for the supervisor.