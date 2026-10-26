Follow-up 1 on 58e918d (change/nz-election-rehearsal-contract). Host Chromium run (the browser cases your sandbox
could not launch), twice, same result:

  uv run --with pytest --with playwright pytest -q "product/nz_election/tests/test_night_deployed.py::test_browser_checks"
  -> 1 failed, 2 passed; FAILED test_browser_checks[faults]
  night_live_browser.py:104 (in transition_proof, scenario reference-retention):
      assert page.locator('#night-snapshot').inner_html() == before   -> AssertionError

So after advance(cases['incomplete']) the snapshot markup changed. Find out what changed (dump both HTML strings
to a temp file and diff them in a local Chromium if you can, otherwise reason from night-live.mjs and the render path).
Then one of:
- the client drops or replaces the retained reference on an incomplete package: a product defect; fix it in the client
  and keep the assertion;
- only a legitimate per-response field changed (update time, coverage line, aria-live text): the invariant is that the
  retained reference (candidate names, leaders, seat figures) is unchanged and the renamed candidate does not appear;
  assert exactly that, not whole-markup equality. Say which fields legitimately change and why.
This is this branch's own test; it may move. Tests on main at 497f3ff stay untouched. Do not weaken the
renamed-not-shown check.

Done when: the scenario passes in a browser you can launch, or, if Chromium still cannot launch in your sandbox,
the reasoning names the changed markup with evidence from the code path, and the non-browser night tests still
pass (uv run --with pytest pytest -q product/nz_election/tests/test_night*.py -k 'not browser'), bin/lint ok.
Commit on the branch, do not push. Report in last.md which case applied.
