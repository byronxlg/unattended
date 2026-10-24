Fresh-context review of PR #72 (nz-election-coalitions-fix), read-only. Worktree .worktrees/nz-election-coalitions-fix,
branch change/nz-election-coalitions-fix, head 78a9b94. Diff: git diff 8a8d484...78a9b94 -- product. Judge against REVIEW.md.

Context: product/nz_election/tests/coalitions_browser.py check_unassigned_after_unavailable_allocation failed on main
since 18 Oct. The change routes the synthetic data beside the client module (nz-election/data/) instead of beside
polls/, and restores the 'Seats are unavailable' live-region text in web/coalitions.mjs. Host ran the browser check:
PASS coalition browser. Questions: does any assertion get weaker; does the routed URL match what coalitions.mjs
actually fetches on the live site; does the live message conflict with REVIEW.md pass 4 or the absent-text gate
(never show "not available" style text to readers; is this an aria-live string only).

Output: verdict (accept or request changes), Critical / Important / Nit with file:line. Modify nothing.
