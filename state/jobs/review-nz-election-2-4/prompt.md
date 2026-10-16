Fresh-context review of branch change/nz-election-2 against main (merge-base 5a93836), for
https://github.com/byronxlg/unattended/pull/10 (NZ election increment 2), HEAD 61d405e. Worktree
.worktrees/nz-election-2, read-only. Follow REVIEW.md. Important or Nit, at most five nits,
nothing bin/lint reports. Do not approve.

Context: three previous fresh reviews (state/jobs/review-nz-election-2/last.md, six Important,
fixed in 2daec23; review-nz-election-2-2/last.md, two Important, fixed in 33b906b;
review-nz-election-2-3/last.md, two Important: export.py validators accepted any
datetime.fromisoformat string for operational timestamps, so publish.py string ordering and
build.py local_time could misbehave on naive, offset or fractional values from the data branch).
state/jobs/nz-election-2-fix-3/last.md describes the third fix: export.py gains timestamp(),
calendar_date() and validate_times(); INSTANT_FIELDS must match YYYY-MM-DDTHH:MM:SSZ exactly
(error INVALID_TIMESTAMP), DATE_FIELDS stay date-only (INVALID_DATE); producers validate on
emit; publish.py compares canonical strings; runbook updated. New tests in
product/nz_election/tests/test_timestamp_canon.py (23).

Scope, in this order:
1. `git diff 33b906b..61d405e` (the third fix). Confirm the invariant holds: every operational
   timestamp that enters through validate_envelope or validate_bundle is a UTC instant in the
   one canonical form, so string order equals instant order. Check especially: a field that
   carries an instant but is not in INSTANT_FIELDS (grep the pipeline and fixtures for *_at and
   other time keys); the observed_at branching in validate_times versus the per-stem rule in
   validate_envelope (can a manifest or status row carry an observed_at that one accepts and the
   other rejects, or that publish.py or build.py then treats differently); validate_times
   recursing into env['data'] rows and source refs (any legitimate value it now rejects, for
   example a poll row field named 'date' that is not a date, or a fixture capture's captured_at);
   whether datetime.fromisoformat after the regex can still accept a non-instant (it should not
   matter, but say so); publish.py's comparison comment matches the code; runbook statement
   matches the code; reject-versus-canonicalise is applied consistently (no path silently
   rewrites a value).
2. The 23 tests: would each fail on 33b906b (reason from the diff; run python3 reproductions
   where the sandbox allows)? Does the Auckland-versus-UTC rendering test actually vary TZ or
   only assert a fixed string?
3. `git diff 33b906b..61d405e --stat -- '*test*'` must show only additions; anything this fix
   changed outside the two items.

Host run stands at 61d405e: 232 passed, bin/lint ok, refresh and build and verify all PASS,
no-data build PASS, screenshots PASS 6 routes 12 baseline images. Screenshots are unchanged by
this fix (no UI files touched); do not re-judge them.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
