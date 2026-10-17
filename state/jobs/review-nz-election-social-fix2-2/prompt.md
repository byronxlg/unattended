Second fresh-context review of the social proof of concept fix branch, read-only. Worktree
.worktrees/nz-election-social-fix2, branch change/nz-election-social-fix2, three commits on top
of main (git diff main...HEAD; 5071194 the eval, 983f112 the change, 58cc131 fix round 1). The PR
is the one whose head is this branch (`gh pr list --head change/nz-election-social-fix2`); read
its comments: the first fresh review (four Important) and the supervisor's disposition (items 1 to
3 fixed in 58cc131, item 4 accepted: no legacy three-key rows exist on the data branch). The fix
brief is state/jobs/nz-election-social-fix2/followup-1.md on main
(`git show main:state/jobs/nz-election-social-fix2/followup-1.md`). The engineer's account is
last.md in the worktree: claims to check, not evidence. Judge against REVIEW.md.

Check, in this order:
(1) Item 1: a 200 whose body fails decode (over MAX_BYTES, invalid JSON, non-object JSON) is fatal
with its original code (SOCIAL_RESPONSE_LIMIT or SOCIAL_INVALID_RESPONSE) and check=decode; no
row written. Only post-decode structural checks are per-post exclusions. Nothing weaker than main.
(2) Item 2: after classify returns with exclusions, a later aggregate, write or publication
failure reports its own code; the bound's fatal line (in-loop and the backstop in refresh_social)
still carries the last exclusion's check and window. Does the new check='complete' value reach
any reader (print_diagnostic, status row, tests) in a way that misleads.
(3) Item 3: the denominator is computed before the first Jev request; 480 invalid candidates make
49 calls at most; isolated first failure continues; exactly 10 percent passes; the eval path
(enforce_bound False) still reports the whole sample. Is diagnostic['last_exclusion'] ever None
when refresh_social applies it.
(4) The three regressions the first review did not find: anything the fix changed in the
diagnostic dict shape that test_social_diagnostics.py or the status row depends on; the window
index after the two-pass loop (origins indexed by the original post index, not the candidate
index); leaks (every check value a local constant, no upstream string printed).
(5) Protected tests: main's tests at eecc6fb unchanged beyond what 983f112 already moved.

Output: a verdict (accept, or request changes), then findings as Important or Nit, each with
file:line, what is wrong, what the invariant is, and how you would verify a fix. No code.
