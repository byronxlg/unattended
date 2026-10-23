Committed `2f6c050`, directly after `6bbc873`. No rebase or push.

Fixed all three findings: handled descriptor failures, structural absence checks, and per-row voting-window filtering with disclosure.

Verification:
- `uv run --with pytest pytest -q`: **922 passed**
- `bin/lint`: **lint ok (531 text files)**
- `m3_checks`: **PASS** on populated and production builds

Exact commands and outputs are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-m3-advance/last.md), uncommitted. Prior 2026 capture and host screenshot gaps remain unchanged.