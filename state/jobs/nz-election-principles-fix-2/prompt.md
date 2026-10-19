Follow-up 2 on change/nz-election-principles (59bb62b). Host results: build PASS 79 routes,
check_visible_text PASS, measure_home PASS (details 0, links 37, source 7, 10,699 bytes, h2 7).
The screenshot harness FAILS on the host:

  uv run product/nz_election/tests/screenshots.py --site artifacts/site --out artifacts/nz-election/screenshots
  AssertionError: BROKEN_FRAGMENT: http://127.0.0.1:.../unattended/nz-election/polls/#source-average

The fixture site's polls/ has id="source-average", so the failure is in one of the design states
the harness builds (screenshots.py:142, design_states.STATES): home.py:230 links the trend module
to 'polls/#source-average' unconditionally, and polls/ only renders that id when an average is
published. On main at b0f3b3f the harness passed every state.

Fix, as a build round on this branch:
1. Every home link to another route's fragment resolves in every design state: link to a
   fragment the target always renders, or to the route without a fragment when the target has
   none in that state. Check the other module "See all" links the same way.
2. A test over the design states (no Chromium) that fails when a built page links to a fragment
   the target page does not have; show it fails on 59bb62b and passes on the fix.
3. Nothing weaker: the harness's BROKEN_FRAGMENT check stays as it is.

Tests on main at b0f3b3f do not move; the branch's own tests move with it.

Done when: pytest passes, bin/lint ok, verify all PASS, measure_home PASS with numbers printed,
the new test printed failing on 59bb62b and passing on the fix. Chromium is blocked in your
sandbox: say so; the supervisor runs the harness on the host. Commit, do not push, do not commit
last.md or artifacts/.
