# Build brief: nz-election-home increment H-b (night, candidates-first detail, per-route OG)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
Worktree: .worktrees/nz-election-home-b on branch change/nz-election-home-b (from main 1ab7749,
which has H-a as 29bf079 and increment 7 as 3bdcce8). Commit there; never push. One PR:
increment H-b of intent/nz-election/plan-home.md.

Read first: intent/nz-election/plan-home.md (whole; "Supervisor decisions" at the end bind,
especially 2, 3 and 5), intent/nz-election/home.md (H6, H7, H8, H12 and the Design section),
intent/nz-election/design.md, then the files the plan names for H-b, then REVIEW.md.

Goal: everything in the plan's H-b item. `/night/` becomes results-first copy (H6) with the
build-time countdown until results exist; electorate pages lead with candidates (H7) with the
"Held by {party}, {N} votes in 2023 on the original boundaries" line and explicit comparison
wording on changed boundaries; shared summary metadata for title and OG description; one
1200 by 630 OG image per route (H8) with absolute `og:image` and `twitter:image`; verifier
check `home-routes` in both the CLI choices and the registry; runbook instructions.

Deployment (supervisor decision 2, authorized): edit `.github/workflows/pages.yml` to install
Playwright with Chromium only and run `screenshots.py --og-only` between build and upload, then
fail the deploy if any referenced `og/<key>.png` is missing. Keep every existing guard in
pages.yml (the s197 freeze guard and its ordering) exactly as strong as now.

Constraints: no incumbent marker or name-based inference (`test_no_inferred_incumbents` stands);
no runtime library, no fonts, no fetch; data families unchanged; every module keeps its source
note with aria-describedby; no impute of Others (a separate change owns that). Increment 7 added
a markets module and the markets family; the route count is 79 on main, so OG variants are one
per registered route as the build registers them. Contracts move with the registered set: the
image-inventory and count pins (219 to the new total, OG specimen loop to all routes) change to
the new values, nothing weaker, no regression test removed. Fold geometry: measured numbers back
to the supervisor, never a weakened source-note or target check. Do not commit last.md or
anything under state/.

Definition of done, in the worktree:
- `uv run product/nz_election/pipeline/verify.py home-routes` prints `PASS home-routes`;
  `uv run product/nz_election/pipeline/verify.py all` ends with `PASS all`.
- The build prints `PASS build: 79 routes`.
- `uv run --with pytest pytest -q product/nz_election` passes; quote the summary line.
- `bin/lint` prints `lint ok`.
- Screenshots are host-run: name the commands in your final message (full harness, expected
  `PASS screenshots: 79 routes, <N> images` with N stated and derived; `--og-only`, expected
  `PASS screenshots: 0 routes, 79 images`; `coalitions_browser.py`, expected
  `PASS coalition browser`). The supervisor runs them and looks at /night/, one electorate page
  and three OG images at 390 by 844 and 1280 by 800.
- Final message: files changed, each pin moved (old to new value with file:line), the pages.yml
  diff summarised step by step, commands run with their actual output lines, any departure from
  the plan with the reason.
