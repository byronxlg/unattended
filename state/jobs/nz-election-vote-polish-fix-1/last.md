Committed `5fdc15c`. Never pushed.

Fixed deadline visibility across all phases, consolidated shared closing times, and handled missing retrieval metadata. Protected tests unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests -k vote
244 passed, 2828 deselected in 6.29s

bin/lint
lint ok (1164 text files)
```

New regression tests on `f728f4d`: **32 failed, 1 passed**.

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-vote-polish/last.md) records the SHA, regression evidence and deadline placement by phase. Screenshots remain blocked by Chromium’s sandbox launch denial.