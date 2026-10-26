Third fresh-context review of PR #94 (nz-election-night-design), read-only. Worktree .worktrees/nz-election-night-design,
branch change/nz-election-night-design, head 51a52c9. Diff: git diff origin/main...51a52c9. Judge against REVIEW.md.
Brief: state/jobs/nz-election-night-design/prompt.md; page plan intent/nz-election/pages/night.md; design
product/nz_election/DESIGN.md.

The second review requested changes: search hid the map-key caveats, and branch tests pinned markup. Fix-4 merged main and
addressed those; fix-5 (6ee9bf4 merge of main, 51a52c9) restored exactly four source-action links on night/ and added a
scroll margin to the electorate jump target so search stays on screen at 390. Check both review-2 items are resolved, that
the fix-5 changes do not weaken any check on data, provenance, absence or accessibility, and that no new test pins markup,
class names or bytes.
Supervisor host run with Chromium: test_result_states, test_night*, test_design, test_home*, test_waterfall* 467 passed, 0 failed.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
