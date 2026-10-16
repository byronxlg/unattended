- **Important** - [poll_parser.py:211](/Users/byron/repos/unattended/.worktrees/nz-election-1/product/nz_election/pipeline/poll_parser.py:211), also line 140: Attribute parsing silently ignores single-quoted values. Reproduced: `rowspan='2'` on a share cell is accepted without `parse_drift`; `data-sort-value='2026-10-11'` is accepted against visible end date 12 October. This bypasses merge validation and date safeguards.
  **Fix:** Parse attributes consistently across quoting forms, validate every merge attribute, and add regression cases.

- **Important** - [poll_parser.py:151](/Users/byron/repos/unattended/.worktrees/nz-election-1/product/nz_election/pipeline/poll_parser.py:151): The named-reference regex treats `<ref name="x"/>` as an opening definition and consumes through a subsequent `</ref>`. Reproduced: the first poll acquires the second poll’s citation URL; an intervening inline reference instead causes a false `conflicting_named_ref`.
  **Fix:** Distinguish self-closing references from definitions using the scanner, and test forward references across multiple rows.

- **Important** - [allocator.py:15](/Users/byron/repos/unattended/.worktrees/nz-election-1/product/nz_election/pipeline/allocator.py:15), [allocator.mjs:12](/Users/byron/repos/unattended/.worktrees/nz-election-1/product/nz_election/web/allocator.mjs:12): Input validation neither guarantees `INVALID_INPUT` nor matches across implementations. Reproduced: `{}` raises Python `KeyError`; a candidate object raises `TypeError` before identity validation. Explicit `baseSeats: null` is rejected by Python but silently becomes 120 in JS.
  **Fix:** Validate complete input shapes before access, hashing or allocation; distinguish missing fields from null identically and expand shared invalid-input parity cases.

- **Important** - [allocator.mjs:51](/Users/byron/repos/unattended/.worktrees/nz-election-1/product/nz_election/web/allocator.mjs:51): Ordinary output objects mishandle the accepted party ID `__proto__`. Reproduced with one party, 100 votes, one candidate and one base seat: Python returns its seat and list member; JS serializes both maps as `{}`.
  **Fix:** Use prototype-free dictionaries and own-property checks consistently; add this identifier to parity coverage.

`uv run --with pytest pytest -q` was blocked by the sandbox:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
  Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
```
Read-only Python/Node reproductions confirmed the findings above. The supervisor’s reported 108 passed and lint result were not rerun successfully here.

Important findings: 4