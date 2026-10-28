# Follow-up 1: home-stale (PR #126)

Fresh review, confirmed by the supervisor at `product/nz_election/tests/home_handover_dom.mjs:85`:
after the cutoff the populated scenarios accept `House: 120 seats|0 national seats reported`
against raw innerHTML, so party seat counts and the reporting percentage could vanish at the cutoff
and the check would still pass. The invariant: at and after the live-update stop, home keeps the
same result numbers the reader saw before it (per party seats, House total, percent counted),
taken from the scenario's source data; only the status/notice text may change.

Do:
1. In each populated scenario, record the visible counts before the stop (per party seats, House
   total, reporting percentage) and assert the same values after the stop, and that they match the
   scenario's input data. Assert on text a reader sees, not a whole-markup string.
2. Status assertions should read the element the page actually renders into, not a detached mock,
   if the harness allows; if not, say so in last.md.

Ignore the review's second item (state files, journal, prompts): that is the reviewer diffing
against a newer main; the PR diff touches only product files. Do not touch state/.

Constraints: tests on main at the base sha are unchanged; this branch's own tests (including
home_handover_dom.mjs changes on this branch) may move. Commit in the worktree, do not push.

Done: `uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_home_handover.py product/nz_election/tests/test_night_page.py` passes (Chromium cases may be sandbox-denied; list them), and the new count check fails if home-live.mjs is changed to blank the party list at the stop (state how you showed this).
