Committed `58a08dd`; not pushed.

Updated chart helpers, home rendering, CSS, and tests: fixed-size HTML labels, seven-row poll plot, threshold bars, and explicit seats-above/below-majority wording.

Checks:
- `pytest -q product/nz_election`: `674 passed in 314.37s`
- `verify.py all`: `PASS all`
- `bin/lint`: `lint ok (496 text files)`

The typography assertion rejects the old CSS/viewBox scaling and accepts the new sizes analytically. Chromium confirmation remains with the supervisor.

[last.md](/Users/byron/repos/unattended/.worktrees/nz-election-home-design/last.md) records evidence and host commands. Report and artifacts remain uncommitted.