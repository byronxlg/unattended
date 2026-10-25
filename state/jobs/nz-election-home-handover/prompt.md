Page plan: intent/nz-election/pages/home.md

Goal: the home page hands over to results at polling close (19:00 NZDT 7 Nov, 2026-11-07T06:00Z) on its own, with no
deploy needed at that moment. Plan question 5 ("Who is winning now, and how much is counted?") moves to first from
19:00. Today it does not reliably: `night_summary` in product/nz_election/pipeline/home.py:184 returns '' without a
qualifying 2026 night row, and home.py:390 then falls back to the poll hero; an already-open home has no clock-driven
handover. The s197 publication freeze (from 6 Nov, see tests/test_night_operation.py:139 and :173) means the build
deployed before the freeze is the build readers see at 19:00, so the handover must live in that build.

Read first: intent/nz-election/pages/home.md (questions, page order, not shown), intent/nz-election/pages/night.md,
product/nz_election/pipeline/home.py (night_summary, the hero selection near :390), result_states.py, the home
template and its client script registration, night-live client code (the shared cutoff embedding from PR #80),
tests/test_home*.py, tests/test_night_operation.py, AGENTS.md, REVIEW.md pass 4 (question test).

Invariants (choose the shape):
1. Server: a build whose clock is at or after 2026-11-07T06:00Z and before the night stop has a results-first top
   section even with no qualifying night data: heading answering question 5, one sentence that polls have closed and
   counting is under way, a link to night/ and to the Electoral Commission's official results site. No "not
   available", "no data" or similar (the absent-text gate applies). With qualifying data the current night summary
   wins, unchanged.
2. Client: a home page built and loaded before 06:00Z swaps its hero to the same results-first section when the clock
   crosses 06:00Z (loaded at 05:59:30Z, still open at 06:00:05Z), with zero requests to result endpoints before
   06:00Z. After the swap it may fetch only what night/ already fetches, within the existing night cutoff (zero
   requests at or after the 8 Nov 06:00Z stop). No JS: the server rendering of invariant 1 stands alone.
3. Before 06:00Z nothing changes for readers (poll hero, questions 1 to 4 in plan order).
4. After the week-after copy switch (post_election) the existing past-tense behaviour holds.

Tests (new, each shown failing on main in last.md): injected-clock browser cases across close: absent feed, zero
state (reported_house 0), first complete package, recovery after a failed fetch; a request-count assertion before
06:00Z; server builds at 05:59Z and 06:01Z with empty night data. Pre-existing tests on main at the base sha stay
untouched unless one pins pre-close hero copy at a post-close clock; if so name it in last.md with why it moves.

Definition of done:
- `uv run --with pytest pytest -q product/nz_election/tests/test_home*.py product/nz_election/tests/test_night*.py product/nz_election/tests/test_result_states*.py` passes (host Chromium is available to the supervisor; say which browser cases you could not run).
- `bin/lint` prints ok.
- `python3 product/nz_election/pipeline/verify.py all` PASS on a fixture build.
- Screenshots of home at 390 and 1280 at clocks 05:59Z and 06:01Z 7 Nov with empty night data, saved under the
  worktree's artifacts/ (untracked, not committed); describe what is above the fold at 390 in last.md.
- One commit on change/nz-election-home-handover; do not push; do not commit last.md or artifacts/.
