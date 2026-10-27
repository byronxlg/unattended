# Follow-up 2 (fix round on PR #88)

The fresh review (state/jobs/review-nz-election-home-handover/last.md) requested changes. Fix both Important items on this branch; commit in the worktree, do not push.

1. `product/nz_election/pipeline/home.py:179` compares the build time against a literal timestamp for the handover while the voting-dates line uses the shared cutoff. Invariant: one predicate decides post-election state for every home module (hero, night summary, voting dates). Read where the shared cutoff lives (the sunset/night constants used by night_live.py and the voting-dates line) and use it; no second literal anywhere in home.py or home-live.mjs. Add a test that patches the shared cutoff and shows hero and dates move together (it must fail on 59f1c1e).

2. `product/nz_election/web/home-live.mjs:24`: the request stop guard also stops content retirement. A page cached before the handover and opened after 8 November 06:00Z keeps the poll hero; a page showing the waiting summary keeps "counting is under way" forever. Invariant: the request cutoff limits network requests only; retiring obsolete content (poll hero to the post-election state, "counting is under way" to the settled wording the server build would render at that time) depends only on the clock and makes zero requests past the cutoff. Add browser regressions for both cases (cached pre-election page opened after the stop; waiting summary opened after the stop), both failing on 59f1c1e.

Constraints: tests on main at 3ee6372 are protected except the assertions this branch already moved; this branch's own tests move with it. Keep the home module under 2048 gzip bytes and exactly one home live module. No absent-state wording (main's ABSENT_TEXT gate).

Done when: `uv run --with pytest pytest -q product/nz_election/tests/test_home*.py product/nz_election/tests/test_design.py` passes (browser cases may be skipped in your sandbox; say so), `bin/lint` prints lint ok, and last.md lists the new tests and their failure on 59f1c1e.
