Committed `1e53a1e`; not pushed.

- `social.py`: request and accepted registry share pinned `MODEL_VERSION`. Strict validation and aggregate provenance preserved.
- Added rotation regression tests, `evals/social-model-rotation/`, and runbook upgrade guidance.
- Commands and outputs recorded in uncommitted `last.md`.

Verification:

- `evals/social-model-rotation/check.sh`: `PASS model rotation: 240 classified, pinned model recorded`
- Same eval on main `cbe10d7`: `FAIL model rotation: refresh returned SOCIAL_UPSTREAM_FAILED`
- Regression test also fails on main.
- `bin/lint`: `lint ok (637 text files)`
- `uv run --with pytest pytest -q product/nz_election`: `1 failed, 1920 passed, 2 errors in 553.39s`

Full-suite acceptance remains blocked: all three unsuccessful checks hit Chromium launch failures from sandbox Mach-port permission denial. All social tests passed. No open implementation questions.