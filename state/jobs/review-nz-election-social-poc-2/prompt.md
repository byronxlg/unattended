Second fresh-context review of the social proof of concept, read-only. Worktree
.worktrees/nz-election-social-poc, branch change/nz-election-social-poc, four commits on top of
main 5c1fd99 (git diff main...HEAD). PR #24. The first fresh review (second comment on PR #24,
read it verbatim with `gh pr view 24 --comments`) found five Important items; the host found a
sixth (populated page figure without aria-describedby). Fix round 1 is commit 0642382; its brief
is state/jobs/nz-election-social-poc/followup-3.md (read it first, it names the invariant per
item). The engineer's account is .worktrees/nz-election-social-poc/last.md: claims to check,
not evidence. Judge against REVIEW.md, every pass.

Screenshots attached (--image) are from the host harness on 0642382 with the social fixture
loaded: social/poc/ at 1280x800 and 390x844, populated state.

Check, in this order:
(1) Each of the six items: is the invariant now enforced where the brief says, with a new test
that fails on 1271c0e (`git diff 1271c0e..0642382` is the fix; the new tests are
test_social_fix_round1.py). Is any fix weaker than the invariant, or does any existing test or
assertion change (it must not).
(2) The freeze: build.py now refuses any build inside the window and pages.yml has an inline
clock guard 2026-11-06T10:30Z to 2026-11-07T06:00Z. Confirm the NZDT arithmetic, that a
pages.yml run started before the window cannot deploy inside it, that the daily social workflow
cannot publish inside it, and what the site serves during the window (last pre-freeze deploy).
Does the whole-site pause break anything the election-night route needs before 19:00 NZDT.
(3) The credit ledger after the change: claim before collection, additive publication, refusal
of a merge that hides a spend, the midnight stop. Walk the retry-after-runner-loss replay the
first review ran and state the ledger total and actual spend it would now produce.
(4) Leaks: the model registry; any upstream string path left that bypasses the closed
enumerations; error paths; the sanitized error record.
(5) The populated page copy and both screenshots: proof-of-concept label, sample size, date
range, method, withheld rows, source notes.
(6) Anything new in 0642382 that touches existing routes, families or workflows beyond the
social route, its family and the two guards.

Report: findings labelled Important or Nit with file:line, then one paragraph on the page copy
and screenshots, then a last line "Important findings: N". No emojis, no em dashes.
