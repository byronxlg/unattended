# polls/ page: rebuilt from the accepted page plan

Page plan: intent/nz-election/pages/polls.md

Read first: `AGENTS.md`, `intent/nz-election/pages/polls.md` (accepted 2026-10-20T23:00Z; it decides what is on
the page and in what order, and its Graphics lines name the reference for each chart), the current polls/ route
(grep `polls` in `product/nz_election/pipeline/build.py` and the templates), `intent/nz-election/design-principles.md`
and `intent/nz-election/look-538.md` (style, applied last), the home charts merged in #64 (reuse their party trend and
seat bar helpers rather than writing new ones).

Branch: `change/nz-election-polls-page` in `.worktrees/nz-election-polls-page`, from main.

Goal: polls/ answers the plan's six questions in rank order, nothing else.
- 390x844 above the fold: answer 1 (party averages as horizontal bars, largest first, direct labels, value at bar
  end, one dated caption), then answer 2 starts (trend: average lines with poll dots behind, labels at each line's
  last point, threshold line at 5%).
- Then 3 (seat bar by bloc with the 61 majority marker; reuse the home seat bar), 5 (one sentence per party within
  two points of 5%, only those; none when none), 4 (recent polls table newest first: pollster, fieldwork dates,
  sample, party shares, link to the original report), 6 (one link line to the Methods average section).
- Not shown: win probabilities, pollster ratings, electorate inferences, preferred-PM polls, the full source history.
- Every existing fragment id on polls/ is kept (harness and other routes link to them; list them in last.md).
- Absent means absent: missing data drops its block, never a placeholder (main's ABSENT_TEXT gate).

Contracts that move with this change: polls/ markup and the harness checks keyed to the old polls layout. Tests on
main that guard other routes, byte and font budgets, and check thresholds do not move; if polls/ needs a budget
change, stop and say why with the numbers.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass (Chromium-only sandbox failures named), including new tests:
  answer order on polls/, threshold sentences only within two points, fragment ids preserved.
- Build from the live data branch, not fixtures: `git archive origin/data | tar -x -C <tmp>/data`, then
  `uv run product/nz_election/pipeline/build.py --data <tmp>/data/product/nz_election/data --out <tmp>/www/unattended/nz-election`
  and `uv run product/nz_election/pipeline/verify.py all --site <that out>` prints `PASS all` (the Pages gate; #64
  passed fixtures and failed this on deploy).
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` PASS, or
  name the Chromium launch failure so the supervisor runs it on the host.
- Question test: from polls/ at 390x844 say where answers 1 and 2 are and that 3 is within one scroll.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push; do not commit last.md or artifacts/.
