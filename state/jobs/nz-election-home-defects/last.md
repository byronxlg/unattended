Committed `48b05aa`; not pushed. Updated home rendering, market questions, CSS and regression tests. Details in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-defects/last.md).

Verification:

- `uv run --with pytest pytest -q product/nz_election`: `660 passed in 298.47s (0:04:58)`
- `uv run product/nz_election/pipeline/verify.py all`: `PASS all`
- `bin/lint`: `lint ok (493 text files)`
- Six regression checks fail on base and pass on HEAD.

Open: Chromium launch was denied by the sandbox. Geometry and screenshots remain unverified. Defect 11 has explicit width bounds, but its root cause and rendered fix still need supervisor confirmation.