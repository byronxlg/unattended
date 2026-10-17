# Build brief: nz-election-home increment H-a (feed home and the /polls/ move)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
Worktree: .worktrees/nz-election-home on branch change/nz-election-home. Commit there; never
push. One PR: increment H-a of intent/nz-election/plan-home.md.

Read first: intent/nz-election/plan-home.md (whole; "Supervisor decisions" at the end bind),
intent/nz-election/home.md (H1 to H12 and the Design section), intent/nz-election/design.md
(tokens, states, source notes), then the files the plan's pin table names, then REVIEW.md.

Goal: `/` becomes the feed home (hero with countdown and the home sentence, seats, polls,
electorates to watch, directory, social, method modules); `/polls/` is today's polls page with
every fragment id preserved; navigation gains Home; shared partials so the strip, rows and
threshold watch cannot drift between the two. Everything in the plan's H-a item, nothing from
H-b (night copy, detail order, per-route OG, pages.yml) except what H-a's tests need.

Constraints: the design tokens and the "module is a rule-separated region, no boxes" rule in
home.md; countdown computed by the build in Pacific/Auckland, three fixed-time tests; the
electorate selection rule exactly as plan decision 3 (six smallest 2023 margins on unchanged
boundaries, East Cape eligible, changed boundaries excluded and said so, no incumbent marker);
every module has a source note with aria-describedby; no runtime library, no fonts, no fetch;
data families unchanged. Contracts move with the registered set: the route, fragment, image and
nav pins the plan lists change to the new values, nothing weaker, no regression test removed.
Do not commit last.md or anything under state/.

Definition of done, in the worktree:
- `uv run product/nz_election/pipeline/verify.py home` prints `PASS home`;
  `uv run product/nz_election/pipeline/verify.py all` ends with `PASS all`.
- The build prints `PASS build: 79 routes`.
- `uv run --with pytest pytest -q product/nz_election` passes; quote the summary line.
- `bin/lint` prints `lint ok`.
- Screenshots are host-run: name the command (`uv run product/nz_election/tests/screenshots.py`,
  expected `PASS screenshots: 79 routes, 219 images`) in your final message; the supervisor runs
  it and looks at the home at 390 by 844 and 1280 by 800.
- Final message: files changed, each pin moved (old to new value with file:line), the commands
  run with their actual output lines, any departure from the plan with the reason.
