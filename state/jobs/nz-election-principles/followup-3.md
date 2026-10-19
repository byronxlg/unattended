Host harness on 9a8aa1d (pytest 696 passed on the host) now FAILS one step later:

  uv run product/nz_election/pipeline/build.py --data product/nz_election/data --out artifacts/site/nz-election
  uv run --with pytest product/nz_election/tests/screenshots.py --site artifacts/site --out artifacts/nz-election/screenshots
  AssertionError: HOME_ROW_KEYBOARD_FOCUS  (screenshots.py:252)

On the committed data, baseline-2023 and candidates are absent, so home.py closest() renders only the
unavailable paragraph, and the redesign dropped the ul.home-directory fallback that main (b0f3b3f
home.py:125) rendered. The harness then finds neither `.watch-rows a` nor `.home-directory a`.

Fix: in every data state the home offers a keyboard-reachable row of route links that the harness
selector at screenshots.py:248 finds (watch rows when the data is there, the directory otherwise),
within principle 2 (no details on home) and the measure_home budgets. Keep it a plain link list,
not a module of its own if that breaks the six-module count; your call on placement.

Constraints: screenshots.py and every test on main at b0f3b3f unchanged; this branch's own tests may
move with the change. Add a no-Chromium test that the built home, in each design_states state and on
the committed data, contains at least one `.watch-rows a` or `.home-directory a`; show it failing on
9a8aa1d. Done: full pytest passes, bin/lint ok, verify all PASS, measure_home PASS. Say if Chromium
is still blocked; the supervisor runs the harness on the host. Commit, do not push, do not commit
last.md or artifacts/.
