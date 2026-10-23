Fresh-context review of nz-election-m3-advance, read-only. Worktree .worktrees/nz-election-m3-advance,
branch change/nz-election-m3-advance, head 6bbc873 on main 0f21ab5. PR #48. Diff: git diff 0f21ab5..6bbc873.
Judge against REVIEW.md and intent/nz-election/plan-m3.md "Increment 1". Brief:
state/jobs/nz-election-m3-advance/prompt.md (main checkout); the engineer's account
.worktrees/nz-election-m3-advance/last.md is a claim to check.

Check: (1) daily vs cumulative semantics come from the manifest descriptor, never guessed; a missing day
is never zero-filled and derived totals across gaps are withheld; (2) production (no 2026 capture) renders
no advance module, heading, empty chart or placeholder text, and m3_checks enforces it; (3) capture
selection rejects ties and invalid newest bytes and retains last-good bytes on failure; (4) the publish.py
family mapping change cannot retain a stale capture or mislabel another family; (5) contract tests on main
at 0f21ab5 that changed assert the same or stronger invariants; (6) figures carry aria-describedby,
div.source-note and p.source-actions; licence and provenance of the 2023 Wayback capture are disclosed.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
