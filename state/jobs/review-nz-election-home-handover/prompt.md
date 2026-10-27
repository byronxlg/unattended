Fresh-context review of PR #88 (nz-election-home-handover), read-only. Worktree .worktrees/nz-election-home-handover,
branch change/nz-election-home-handover, head 59f1c1e. Diff: git diff origin/main...59f1c1e.
Judge against REVIEW.md, including pass 4 (the question test) against intent/nz-election/pages/home.md.

The change hands home over from the poll hero to the results summary at 7 Nov 06:00Z (server build and client on an
already-open or cached page), turns the voting-dates line past tense, and bundles the shared NightLive scheduler into
home-live.mjs. Check: the handover boundary comes from the shared cutoff constant, not a second copy; the client makes
no result requests past the night stop and none extra at handover; no "not available"-style absent text; the two moved
assertions (test_home.py:49, test_design.py:121) still forbid everything except the single bundled module under 2,048
gzip bytes; no other test on main at 3ee6372 was weakened.
Supervisor host run on 59f1c1e: test_home*.py and test_design.py 107 passed incl. Chromium; 06:01Z screenshot at 390
looked at. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
