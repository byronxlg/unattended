Fresh-context review of PR #76 (nz-election-night-deployed), read-only. Worktree .worktrees/nz-election-night-deployed,
branch change/nz-election-night-deployed, head 88f9367. Diff: git diff f406321...88f9367. Judge against REVIEW.md.

Context: adds product/nz_election/tests/night_deployed.py with three modes against the deployed origin: --probe
(browser fetch of the EC XML feed from the site origin, fallback shown, provenance), --rehearse (timed replay at 60x,
golden end state 2,851,211 votes House 122, pause/reset, 2017/2020/2023 archives, console errors, screenshots 390 and
1280) and --faults (failed data responses keep the last good snapshot with its time), plus tests and runbook/night.md.
This is the acceptance evidence for election night (pages/night.md). Check: each check can actually fail (no check that
passes on an empty page or on a network error), records carry code and data SHAs, nothing writes outside artifacts/,
no secret or upstream raw text is written, the runbook commands match the CLI, and the fault mode exercises the real
fallback path rather than a stub.
Host: test_night_deployed.py 13 passed; --probe, --rehearse --speed 60, --faults each PASS on the live site 21:08Z
(probe: browser fetch blocked, fallback shown). Do not run pytest or the browser; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
