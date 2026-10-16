Fresh-context review of the fix commit on branch change/nz-election-5 for
https://github.com/byronxlg/unattended/pull/13 (NZ election increment 5, geography and
directory). Worktree .worktrees/nz-election-5, read-only. Follow REVIEW.md. Important or Nit, at
most five nits, nothing bin/lint reports. Do not approve.

Scope is the fix diff only: `git diff e8d1d77..ba8914b`. The first fresh review (logged on PR
#13) found four items, now addressed in one commit:
1. validate_bundle (pipeline/export.py) no longer compares a retained geography bundle with the
   current checkout registry and config hashes; the current-input check stays with the producer
   (pipeline/daily_refresh.py around line 37). Invariant: families fail and retain independently
   (plan-m2 line 40); a bundle inconsistent with its own recorded hashes is still rejected.
2. fixtures/stats-nz/{general,maori}-2025.reference.json gained manifest entries and are loaded
   through captures(); bytes unchanged; manifest 25 to 27.
3. test_svg_page_budget now measures the built page plus every linked .svg (new
   tests/svg_budget.py) against index_svg_max_bytes; outline gate kept.
4. search_key parity: geography.py strips category M* instead of combining(); electorates.mjs
   gained a casefold exception table and Python-split whitespace handling; parity test over the
   71 names plus probes.

Check, in this order:
1. Item 1: with the checkout check gone from validate_bundle, is every path that produces a
   geography family still gated on the current registry and config (daily_refresh.py, refresh.py,
   publish.py)? Can a bundle whose recorded input_hashes disagree with its own electorates.json
   bytes still pass? Does publish.py still refuse to publish a mixed-generation bundle?
2. Did any existing test assertion change? `git diff e8d1d77..ba8914b -- '*test*'` should show
   additions only; confirm by reading the diff. Did any budget constant move?
3. Item 3: does svg_budget.py count the bytes the browser would fetch for the electorates route
   (inline svg elements, linked .svg via img, object, use, or CSS url), and would the reviewer's
   probe (the map embedded twice, 568,632 bytes) now fail?
4. Item 4: is the JS fold table a faithful copy of Python str.casefold for the code points it
   lists, and does the parity test run the JS side through Node rather than reimplementing it in
   Python? Does the search still behave for a plain ASCII query and a macron query in the page
   (reason from the code; Chromium does not start in your sandbox)?
5. Item 2: do the manifest notes record how the companions were produced, and does
   test_reference_capture_hash_pinned fail on a one-byte change?

Host run at ba8914b: 295 passed, lint ok, verify all PASS (geography 64 general, 7 Maori),
refresh, daily_refresh and build PASS (6 routes), screenshots PASS 6 routes, 12 baseline, 12 state
images. Existing tests confirmed additions only by the supervisor (0 removed lines under tests/).

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
