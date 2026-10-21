# vote/ page: how and when to vote (advance voting opens 26 October)

Page plan: intent/nz-election/pages/vote.md

Read first: `AGENTS.md`, `intent/nz-election/pages/vote.md` (accepted 2026-10-20T14:33Z; it decides what is on the page and in what order), `product/nz_election/snapshots/` voting snapshot with its loader in `pipeline/snapshots.py` and `tests/test_voting_snapshot.py` (PR #53: EC key dates and official links), `pipeline/campaign_page.py` and `pipeline/build.py` route registration (the route set pin at build.py:558), `pipeline/route_cards.py`, `intent/nz-election/design-principles.md` and `look-538.md` (style, applied last), `product/nz_election/tests/screenshots.py`.

Branch: `change/nz-election-vote-page` in `.worktrees/nz-election-vote-page`, from main.

Goal: a new route `/unattended/nz-election/vote/` that answers the plan's five questions in rank order from the voting snapshot, nothing else. At 390x844 the first screen holds answer 1 before 26 Oct NZ and answer 2 from 26 Oct NZ (chosen from the build time against the snapshot's dates, so the scheduled hourly flips it without a code change), the other second, then answer 3; below, answer 4 with each NZ-time deadline, then answer 5 (link to the reader's electorate page via the electorates index, and Policy.nz). One graphic: the days-left countdown with the three EC dates on one timeline (plan "Graphics"). Every link in the first screen goes to an official EC page from the snapshot. Not shown: eligibility checker, stored addresses, copied voting-place hours, any recommendation. Absent means absent: a date or link missing from the snapshot drops its line, never a placeholder. Link vote/ from home and the header nav; campaign/ keeps its advance-voting observations and links to vote/.

Contracts that move with this change: the registered route set gains `vote/` (build.py pin, route cards, screenshot registry, route counts in tests and the harness). Tests on main at the base sha must not be weakened; the branch's own tests move with it.

Definition of done, commands and expected output in last.md (uncommitted):
- `uv run --with pytest pytest -q product` all pass, including new tests: first-screen order flips at 2026-10-26T00:00 NZDT (two injected clocks), a missing snapshot date drops its line, every first-screen href is on an EC domain.
- `uv run product/nz_election/pipeline/verify.py all` on a populated build prints `PASS all`.
- Screenshot harness `uv run --with pytest product/nz_election/tests/screenshots.py --site <built site>` prints PASS with the new route count; name the screenshots of vote/ at 360, 390 and 1280 for both clock states.
- Question test (plan): from the 390x844 screenshot alone, answers 1 to 3 are readable; say where each is.
- `bin/lint` prints `lint ok`.
Commit on the branch; never push.
