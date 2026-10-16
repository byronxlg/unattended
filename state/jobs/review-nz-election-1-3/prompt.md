Fresh-context review of branch change/nz-election-1 against main, for PR #9 (NZ election
increment 1), third round, HEAD af8f50b. Worktree .worktrees/nz-election-1, read-only.
Follow REVIEW.md (bugs; security; compliance with intent/nz-election/spec.md "Allocator
contract", "Poll method and assumptions", and the plan via
`git show 62d3ff6:intent/nz-election/plan.md`). Important or Nit, at most five nits, nothing
bin/lint reports. Do not approve.

Focus on the fix commit `git diff 3b234f6..af8f50b`: Python now treats finite integral floats
as integers (booleans and fractional values rejected), JS sorts party ids by code point, the
parser recognises attribute names case-insensitively. Earlier rounds fixed: quoting forms in
attributes, self-closing named refs, INVALID_INPUT on every bad shape, "__proto__" ids.
Check the pattern, not the instance: every numeric field in both allocators under the float
rule (NaN, Infinity, 1e3, -0.0, 2**53 and above, numeric strings), whether the integral-float
normalisation can change an exact result, that the code-point comparator is used everywhere
order matters (quotient tie stability, unresolved tie candidates, listMembers), that no
existing test weakened, and that the 43 pinned poll ids are unchanged.

Running checks: uv's cache is not writable in this sandbox; review by reading plus node and
python3 reproductions. The supervisor's run at af8f50b stands: 171 passed, bin/lint ok.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
