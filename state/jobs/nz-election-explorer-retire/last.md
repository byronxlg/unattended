Committed `ff4aaab` on `change/nz-election-explorer-retire`. Not pushed; `last.md` remains uncommitted.

Removed `web/coalitions.mjs`, `tests/coalitions_browser.py`, `tests/coalitions_runner.mjs`, and `tools/render_coalition.mjs`.

Replacement checks:
- `verify.py`: script-free polls, preserved fragments and static majority.
- `home_checks.py`: legacy fragments resolve even without data.
- `landmark_checks.py`: rendered routes retain provenance and accessible regions.

Server strip, TOP labels and Night’s allocator remain. All 162 HTML documents match the original byte-for-byte; 325 fragment links pass.

Verification:
- `uv run --with pytest pytest -q product/nz_election`: `1 failed, 2024 passed, 2 errors`.
- Fixture build: `PASS build: 81 routes`.
- Fixture `verify.py all`: `PASS all`.
- `bin/lint`: `lint ok (870 text files)`.
- Module references remain only in historical notes.

All three pytest non-passes are Chromium launch failures: party-picker layout, Night XML parity and Night replay. Screenshots also remain blocked by sandbox Mach-port permissions. No open product questions.