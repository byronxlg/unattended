# Fix: home page over its byte budget on live data (Pages blocked)

Page plan: intent/nz-election/pages/home.md

Goal: production incident. Since PR #64 merged (205237c), every "Publish the blog" run fails at
"Verify election pages": `product/nz_election/tools/measure_home.py:44` asserts
`html_bytes < 65_000`; on the data branch the home is 68,868 bytes (`links 110, source 5,
details 0, h2 2`). CI passes because fixtures are smaller. The live site serves the previous
build and its data goes stale until this ships. Read `evals/pages-home-bytes-live/task.md`.

Read first: `AGENTS.md`, `evals/pages-home-bytes-live/`, `product/nz_election/tools/measure_home.py`,
`product/nz_election/pipeline/home_checks.py`, the home renderer (`pipeline/home*.py` and its
templates), `intent/nz-election/pages/home.md` (what the page answers, in rank order).

Constraints:
- The 65,000-byte budget and every other check stay as they are. Do not raise or skip anything.
- Keep every answer the page plan ranks and its order; cut bytes, not answers. Likely
  candidates: repeated inline markup or attributes per row, inline SVG detail, duplicated
  static and client copies, long per-row link lists that the plan does not require on home.
  Measure what dominates before choosing; say in last.md what took the bytes and what you cut.
- Leave headroom: under 60,000 bytes on the data the eval pins, so the next week of polls does
  not break deploy again.
- Add a test that fails on main at e32e60e for the cause you fix (for example a per-row or
  per-module byte bound on a populated build that scales like live data). Tests on main at the
  base sha are protected; add new ones.
- Commit in the worktree; do not push. Do not commit last.md or artifacts/.

Done when:
- `bash evals/pages-home-bytes-live/check.sh` last line `PASS home under budget on data d7b8db9...`
- `uv run --with pytest pytest -q product` passes (Chromium sandbox launch errors excepted; name them).
- `bin/lint` prints `lint ok`.
- last.md states the home html_bytes before and after on the eval data.
