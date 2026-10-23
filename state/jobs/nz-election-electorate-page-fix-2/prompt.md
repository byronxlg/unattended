# Fix-2 on PR #67 (electorate page), same build thread

Page plan: intent/nz-election/pages/electorate.md

Supervisor screenshots of b10fc2b on a build from origin/data d7b8db9 (wellington-north, te-tai-tonga,
port-waikato at 390x844 and 1280x800): provenance line once and candidate names fixed. One defect left:

1. The 2023 result sentence still shows the winner in EC sheet form, e.g. "PAUL, Tamatha-Kaye Erin won by ...".
   Show the winner as given name(s) then family name in the same casing rule fix-1 applied to candidates
   (reconciliation `snapshot_name` when the winner is a 2026 candidate; otherwise the same conversion
   applied to the 2023 results name, keeping hyphens and macrons). Apply it wherever a 2023 winner or
   runner-up name renders on electorate pages, and on any other route that reuses that helper.
   Add a test that fails on b10fc2b: no rendered electorate page contains a "SURNAME, Given" pattern
   (an all-caps token followed by a comma) in a person name.

Constraints: tests on main at e32e60e are protected; tests this branch added move with it. No budget,
check or threshold weakened. Do not commit last.md or artifacts/.

Done: `uv run --with pytest pytest -q product/nz_election/tests` passes except Chromium-launch
failures in your sandbox (name them); `uv run product/nz_election/pipeline/verify.py all` on a populated
build PASS all; `bin/lint` ok; the new test shown failing on b10fc2b. Commit on change/nz-election-electorate-page.
