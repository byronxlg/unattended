- **Important** | `product/nz_election/pipeline/allocator.py:11`: Large decimal strings break Python/JS parity. Python’s default 4,300-digit conversion limit leaks a non-`INVALID_INPUT` error; JS accepts the input.
  - **Reproduction:** Allocate `partyVotes={"A": "1" + "0"*4300}`, `electorateWins={"A":0}`, `lists={"A":["c"]}`, `electorateWinners={"A":[]}`, `nonListWinners=[]`, `baseSeats=1`. Python raises `ValueError: Exceeds the limit (4300 digits)…`; Node returns `seats={"A":1}`.
  - **Fix:** Define and enforce the same decimal-string length limit in both allocators, returning `INVALID_INPUT` when exceeded.

Read-only checks: 49 numeric parity cases, 18 nonfinite rejection cases, and Unicode ordering/float normalization reproductions passed. All 43 pinned poll IDs unchanged; no existing tests weakened. Supervisor’s 171-test and lint results were not rerun.

Important findings: 1