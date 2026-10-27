Committed `8749065`; not pushed.

- Unified the home handover cutoff.
- Cached poll/waiting heroes now retire after the stop without requests.
- Single module remains under cap: **1,814 gzip bytes**.

Verification: **107 passed; 6 browser launches blocked** (`absent`, `zero`, `complete`, `recovery`, `cached-after-stop`, `waiting-after-stop`). All 12 non-browser handover checks pass. `bin/lint`: **lint ok**.

Baseline failures and details recorded in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-handover/last.md). Report and artifacts remain uncommitted.