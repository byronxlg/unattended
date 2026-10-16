Fresh-context review of the fix commit on branch change/nz-election-4 for
https://github.com/byronxlg/unattended/pull/12 (NZ election increment 4, coalition explorer).
Worktree .worktrees/nz-election-4, read-only. Follow REVIEW.md. Important or Nit, at most five
nits, nothing bin/lint reports. Do not approve.

Scope is the fix diff only: `git diff 7dca242..5a4d299`. The first fresh review (logged on PR
#12) found one Important item, now fixed: coalitions.mjs draw() returned before rewriting
[data-unassigned] when scenario() had no seats, leaving a stale electorate count. The fix moves
the assignment above the early return and adds browser regressions plus
tests/test_coalition_unassigned.py. It also reworded pipeline/scripts.py and coalitions.md to
describe the filename allowlist precisely (no module hashing; bytes come from the code
checkout by PR).

Check, in this order:
1. Is the unassigned count now correct on every path, including a hash-restored state that
   produces no seats and a reset after one? Does the Python twin still emit the same bytes
   (parity tests)?
2. Did any existing test assertion change? `git diff 7dca242..5a4d299 --stat -- '*test*'`
   should show additions only; confirm by reading the diff.
3. Do the new browser checks actually drive the no-seats path (an allocation tie or no eligible
   party) rather than asserting the text in a state where it was already right?
4. Is the new wording in scripts.py and coalitions.md true of the code?

Host run at 5a4d299: 254 passed, lint ok, refresh, build, verify all PASS, coalitions_browser.py
PASS coalition browser, screenshots PASS 6 routes 12 baseline images. Chromium does not start
in your sandbox; reason from the code.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
