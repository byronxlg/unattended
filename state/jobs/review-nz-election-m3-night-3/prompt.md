Fresh review of PR #59 (branch change/nz-election-m3-night, head 2280987, base main 527ffe9) against REVIEW.md. You have not seen this change before.

Read first: REVIEW.md, state/jobs/nz-election-m3-night/prompt.md (the brief), intent/nz-election/plan-m3.md increment 2, intent/nz-election/pages/night.md (Data section only), then `git diff origin/main...HEAD`.

Scope: data half of election night: EC results XML validation, 2017/2020 archives and media demo replay labelled as such, atomic night-family publication, CSV exports, runbook. No page code is expected; flag any.

Focus: XML validation that fails closed with a named reason; nothing illustrative (demo replay) able to publish as real results; atomic publication; party vote and seat totals against the archive; main's tests unweakened.

Third review: the second fresh review (state/jobs/review-nz-election-m3-night-2/last.md) requested changes: a final-snapshot label could be inferred by stripping metadata, and electorate seats were unbounded; the host nit was the `verify.py night --data <empty dir>` traceback. Fix 2280987 claims all three (`git diff 6e1547b 2280987`). Confirm each is fixed, and check the fix introduced nothing new. Raise only defects with a concrete failure scenario; do not re-open items earlier reviews accepted.

Output: Verdict (accept or request changes), then findings as Critical / Important / Nit with file:line and a concrete failure scenario. Read-only; do not edit files.
