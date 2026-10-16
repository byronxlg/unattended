Fresh-context review of branch change/nz-election-1 against main, for PR #9 (NZ election
increment 1: fixtures, MMP allocator in Python and JS, Wikipedia poll parser), second round,
HEAD 3b234f6. You are in the worktree .worktrees/nz-election-1, read-only.
Follow REVIEW.md in the repository root: three passes (bugs; security; compliance with
intent/nz-election/spec.md sections "Poll method and assumptions", "Allocator contract",
"Testing and acceptance", and the plan: `git show 62d3ff6:intent/nz-election/plan.md`).
Severity Important or Nit, at most five nits, nothing bin/lint reports. Do not approve.

Focus: the fix commit 3b234f6 (`git diff 281e6d8..3b234f6`). The first round found four
Important items, all confirmed and fixed by the engineer: (1) attribute parsing ignored
single-quoted and unquoted values, bypassing rowspan and data-sort-value checks; (2) the
named-ref regex treated <ref name="x"/> as a definition; (3) both allocators raised
KeyError/TypeError instead of INVALID_INPUT and disagreed on baseSeats null; (4) JS output
maps lost a "__proto__" party id. Check that each is fixed for the pattern, not the instance
(for example: attribute names in other cases, whitespace around =, refs nested in templates,
every input shape in both allocators, Object.keys ordering versus Python sorted parties),
that nothing weakened an existing test, that the Python and JS allocators still agree on
every added invalid-input case, and that the parser still produces identical poll ids for the
pinned revision.

Running checks: uv's cache was not writable last round; try `uv run --with pytest pytest -q`
and fall back to reading plus node/python3 reproductions. The supervisor's run at 3b234f6
stands: 146 passed, bin/lint ok.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
