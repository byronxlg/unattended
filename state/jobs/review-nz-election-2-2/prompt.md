Fresh-context review of branch change/nz-election-2 against main (merge-base 5a93836), for
https://github.com/byronxlg/unattended/pull/10 (NZ election increment 2), HEAD 2daec23. Worktree
.worktrees/nz-election-2, read-only. Follow REVIEW.md. Important or Nit, at most five nits,
nothing bin/lint reports. Do not approve.

Context: a previous fresh review of 0e82e89 found six Important items (state/jobs/
review-nz-election-2/last.md); the fix commit 2daec23 claims to address all six plus a CI
failure in publish.py's push-race detector (state/jobs/nz-election-2-fix/last.md describes the
fixes and the new tests in product/nz_election/tests/test_increment_two_regressions.py).

Scope, in this order:
1. `git diff 0e82e89..2daec23` (the fix): for each of the seven items, confirm the fix closes the
   pattern, not just the reviewer's instance, and that the new regression test would fail on
   0e82e89 (reason from the diff; run python3 reproductions where the sandbox allows). Check
   especially: exact integer scaling in average.py (no Decimal precision anywhere before the
   published integer; refresh normalisation too); the threshold helper filters by the average's
   included poll IDs in every caller; publish.py status merge cannot lose a newer failure and
   cannot let an older run replace newer data; the output allowlist in build.py (what exactly
   may --out be, and can any path under site/ that the blog owns still be exchanged or
   cleaned; symlinks); downloads render every manifest field per record; the label-lane
   arithmetic in build.py (Fraction anchors, lane packing) and styles.css (--anchor, --reach,
   --endpoint clamp) cannot place a label off-strip or overlap another lane at 288 px or 736 px.
2. `git diff 5a93836..2daec23` for anything the fix changed outside the seven items, and
   whether any existing test was weakened (the rule: a fix job never edits tests; the engineer
   reports existing tests unchanged, verify with `git diff 0e82e89..2daec23 --stat -- '*test*'`).
3. Screenshots: the supervisor ran screenshots.py on the host after the fix; 20 PNGs and
   manifest.json are in artifacts/nz-election/screenshots/. Judge the seat strip in
   earlier-coherent-window-390x844.png and -1280x800.png against spec Design (anchored labels,
   no cards, 40 px counts, majority mark) and the downloads pages at both widths against spec
   "Provenance and downloads". The supervisor already noted as nits: the majority marker line
   runs through the Labour label box at 390 px; four stacked lanes cost about 400 px of
   vertical space on the phone. Do not repeat those.

Host run stands: 207 passed, bin/lint ok, refresh and build and verify all PASS, no-data build
PASS, screenshots PASS 6 routes 12 baseline images.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
