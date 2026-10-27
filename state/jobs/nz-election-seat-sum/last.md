Correct under the recorded electorate assumptions: **120 + 9 National overhang + 4 TPM overhang = 133 seats**. Majority is **67**; blocs plus TOP total **67 + 59 + 7 = 133**.

Added `test_seat_sum.py` covering both published snapshots. Tables and verdict are in [last.md](/Users/byron/repos/unattended/.worktrees/nz-election-seat-sum/last.md), uncommitted. No production changes.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests -k "seat or coalition or allocator or home"
6 failed, 203 passed, 2865 deselected in 98.92s (0:01:38)

bin/lint
lint ok (1176 text files)
```

All six failures were sandbox-denied Chromium launches, listed individually in `last.md`. Both new regression cases passed.

Committed `2b861f6`. Not pushed. Open questions: none.