Fresh-context review of a build round on the social proof of concept, read-only. Worktree
.worktrees/nz-election-social-fix2, branch change/nz-election-social-fix2, two commits on top of
main (git diff main...HEAD; 5071194 is the eval, 983f112 the change). The PR is the one whose head
is this branch (`gh pr list --head change/nz-election-social-fix2`); read its body and comments.
The brief is state/jobs/nz-election-social-fix2/prompt.md on main (read it from the main checkout:
`git show main:state/jobs/nz-election-social-fix2/prompt.md`); it names five invariants. The
engineer's account is last.md in the worktree: claims to check, not evidence. Judge against
REVIEW.md, every pass.

Incident: the proving run of the social daily spent the day's X credits collecting 24 pages,
then failed on the first Jev classification response (HTTP 200) at a structural check the log
could not name. The sample is never stored, so the post cannot be replayed.

Check, in this order:
(1) Each invariant in the brief: enforced where it says, with a test that fails on main. Is any
weaker than before: does any response that main rejected now get accepted, or any path that
main treated as fatal now continue silently (non-200, transport exception, decode of a
non-object, over-size body).
(2) The 10 percent bound in refresh_social: the denominator (posts sent, after duplicate and
unsupported), the comparison at exactly 10 percent, and what happens when every classification
fails (how many Jev calls are made before the run stops, and whether that is acceptable for a
run per day). State whether the fatal line after the bound trips carries the right check and
window.
(3) The diagnostic dict after classify returns with exclusions: it now carries the last
exclusion's code and check. Does any later failure in refresh_social (aggregate, write,
publication) then misreport its code, and does the success path leave stale state that a later
caller could print.
(4) Leaks: every `check` value is a local constant; print_diagnostic cannot print an upstream
string; the exclusion counter and caption never carry text; the eval's check.sh and the new
tests hold no real post text, handles or keys.
(5) The page caption and the bundle validator: the new key is enumerated once (EXCLUSIONS) and
every consumer uses it; the sample arithmetic (eligible + sum of exclusions == returned) still
holds with the new key; old daily rows without the key, if any exist on the live site, still
validate or are handled.
(6) The moved assertions in test_social.py, test_social_diagnostics.py and
test_social_fix_round1.py: each still pins the full dict or the full line, nothing dropped.

Output: a verdict (accept, or request changes), then findings as Important or Nit, each with
file:line, what is wrong, what the invariant is, and how you would verify a fix. No code.
