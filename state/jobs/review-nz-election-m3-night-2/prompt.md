Fresh review of PR #59 (branch change/nz-election-m3-night, head 6e1547b, base main 527ffe9) against REVIEW.md. You have not seen this change before.

Read first: REVIEW.md, state/jobs/nz-election-m3-night/prompt.md (the brief), intent/nz-election/plan-m3.md increment 2, intent/nz-election/pages/night.md (Data section only), then `git diff origin/main...HEAD`.

Scope: data half of election night: EC results XML validation, 2017/2020 archives and media demo replay labelled as such, atomic night-family publication, CSV exports, runbook. No page code is expected; flag any.

Focus: XML validation that fails closed with a named reason; nothing illustrative (demo replay) able to publish as real results; atomic publication (no half-written family on failure); party vote and seat totals against the archive (2,851,211 valid party votes, House 122 for the replay smoke); main's tests unweakened.

Output: Verdict (accept or request changes), then findings as Critical / Important / Nit with file:line and a concrete failure scenario. Read-only; do not edit files.

Second review: the first fresh review (state/jobs/review-nz-election-m3-night/last.md) requested changes on four Important items (demo mode relabel, zero-vote totals, night verify ignoring --data, empty counts XML_COUNT); fix 6e1547b claims all four with regression tests. Confirm each is fixed (`git diff 272eb6e 6e1547b`), and check the fix introduced nothing new. Host found: `verify.py night --data <empty dir>` exits with a ValueError traceback (INVALID_INVENTORY) rather than a named failure line; judge whether that matters.
