# Follow-up 1: night-nelson, two host Chromium failures

Host (Chromium launches here) ran your required command on 4b0327a:
`uv run --with pytest --with playwright pytest -q product/nz_election/tests -k "night or electorate or design"`
Result: 2 failed, 592 passed. Log excerpts:

1. `test_night_design_followup.py::test_night_design_browser`: `night_design_browser.py:81` asserts
   `Results last updated 10 November 2024 at 00:00.` is visible in the replay state. That sentence is the
   one this change removes (backlog item 2). This contract moves with the change: replace it with the
   behaviour you chose (the 2024 archive date is not presented as a results-updated time in the replay;
   the replay still says it is the 2023 final count). Moving it is authorised; do not weaken the rest of
   that script.

2. `test_night_deployed.py::test_browser_checks[probe]`: `night_deployed.py:284` check `dated-fallback`
   fails. When there is no live retrieval it requires the `#night-snapshot` text to carry a
   `YYYY-MM-DD` date, `Official results`, and `Final snapshot` or `Recorded demo`. That is a provenance
   invariant for the deployed fallback (a reader can see what the snapshot is and when it was taken) and
   it does NOT move. Keep the snapshot provenance dated with a true date (for example the capture
   retrieval date from the manifest, or the 2023 official declaration date if the archive carries one),
   labelled for what it is, while still not presenting the 2024 file timestamp as when results were
   updated. Read `night_deployed.py` around line 270-292 before choosing the shape.

Protected set: tests on main at fb1c2f8, except the one assertion in item 1. Your branch's own tests move
with it.

Done when, on the host:
`uv run --with pytest --with playwright pytest -q product/nz_election/tests -k "night or electorate or design"`
passes with 0 failed (your sandbox cannot launch Chromium; run the non-browser part and say so), and
`bin/lint` prints `lint ok`. Commit in the worktree, do not push. Do not commit last.md.
