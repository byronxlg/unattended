Fresh-context review of branch change/nz-election-2 against main (merge-base 5a93836), for
https://github.com/byronxlg/unattended/pull/10 (NZ election increment 2), HEAD 33b906b. Worktree
.worktrees/nz-election-2, read-only. Follow REVIEW.md. Important or Nit, at most five nits,
nothing bin/lint reports. Do not approve.

Context: two previous fresh reviews (state/jobs/review-nz-election-2/last.md, six Important,
fixed in 2daec23; state/jobs/review-nz-election-2-2/last.md, two Important, fixed in 33b906b).
state/jobs/nz-election-2-fix-2/last.md describes the second fix: publish.py orders successful
bundles by acquisition time then averages.generated_at and keeps repository bytes on exact
ties; downloads render the retrieval time in Pacific/Auckland with the manifest record kept
in UTC. New tests in product/nz_election/tests/test_generation_provenance.py.

Scope, in this order:
1. `git diff 2daec23..33b906b` (the second fix): for each of the two items confirm the fix
   closes the pattern, not just the reviewer's instance, and that each new test would fail on
   2daec23 (reason from the diff; run python3 reproductions where the sandbox allows). Check
   especially: success_order in publish.py when the incoming bundle has no polls, has polls
   but no averages, or carries a failed attempt over an older build; whether keep_status and
   keep_data can now disagree in a way that publishes a status row from an older attempt or
   loses the newer failure (the invariant from fix 1 item 3: status always reports the latest
   attempt); the runbook statement matches the code; observation_label and local_time on
   values without a Z suffix or with a date only.
2. `git diff 5a93836..33b906b` for anything this fix changed outside the two items, and
   whether any existing test was weakened (`git diff 2daec23..33b906b --stat -- '*test*'`
   must show only additions).
3. Screenshots: the supervisor ran screenshots.py on the host after the fix; PNGs and
   manifest.json are in artifacts/nz-election/screenshots/. Judge downloads-1280x800.png and
   downloads-390x844.png against spec "Provenance and downloads" (intent/nz-election/spec.md)
   including the new Pacific/Auckland rendering. Known nits already recorded on the PR by the
   supervisor: majority marker through the Labour label at 390 px; four stacked lanes on the
   phone. Do not repeat those.

Host run stands at 33b906b: 209 passed, bin/lint ok, refresh and build and verify all PASS,
no-data build PASS, screenshots PASS 6 routes 12 baseline images.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
