Committed `5e3ef85`, not pushed. Updated the compact market panel, USD formatting, failure retention, validation parity and regression checks. `last.md` remains untracked.

Verification:

- `uv run --with pytest pytest -q`: **639 passed in 209.72s**
- `bin/lint`: **lint ok (434 text files)**
- Artifact verifier: **PASS all**
- Content regression check rejects `176944f`; passes all 79 revised pages.

**Browser acceptance remains incomplete:** Chromium failed with macOS `Permission denied (1100)`. No screenshot PASS, measured heights or inspected screenshots are claimed. The harness now enforces the 844 px mobile bound and saves both module closeups. Details and host commands are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-7/last.md).