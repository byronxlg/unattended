Fresh-context review of PR #72 (nz-election-coalitions-fix), read-only. Worktree .worktrees/nz-election-coalitions-fix,
branch change/nz-election-coalitions-fix, head deecb15. Diff: git diff 8a8d484...deecb15 -- product. Judge against REVIEW.md.

Context: product/nz_election/tests/coalitions_browser.py check_unassigned_after_unavailable_allocation failed on main
since 18 Oct. The change routes the synthetic data beside the client module (nz-election/data/) instead of beside
polls/, and restores the 'Seats are unavailable' live-region text in web/coalitions.mjs. Host ran the browser check:
PASS coalition browser. Questions: does any assertion get weaker; does the routed URL match what coalitions.mjs
actually fetches on the live site; does the live message conflict with REVIEW.md pass 4 or the absent-text gate
(never show "not available" style text to readers; is this an aria-live string only).

Output: verdict (accept or request changes), Critical / Important / Nit with file:line. Modify nothing.

Second review round. The branch head is now deecb15 on change/nz-election-coalitions-fix (diff against main 8a8d484). The previous review's one Important finding was the reader-visible "Seats are unavailable" in coalitions.mjs and the static ABSENT_TEXT gate missing runtime text. Check that it is resolved: the new copy is actionable and contains no absent wording, the browser check now runs check_absent_text on [data-live], and the one moved assertion is not weaker than the one it replaced. Report findings per REVIEW.md with a verdict line: accept or request changes.
