Verdict: **request changes**.

Critical: None found.

Important:

- [advance_preflight.py:49](/Users/byron/repos/unattended/.worktrees/nz-election-advance-preflight/product/nz_election/tools/advance_preflight.py:49): Ambiguous semantics default to daily. Probed `Date,Total votes` with values 10, 30: draft selects `daily`, producing cumulative 40 if registered unchanged. Require explicit daily/cumulative evidence or reject ambiguous labels with `INVALID_ADVANCE`. The review warning does not prevent an incorrect draft.

- [advance.py:50](/Users/byron/repos/unattended/.worktrees/nz-election-advance-preflight/product/nz_election/pipeline/advance.py:50): `strict=True` does not reject all malformed quoting. Both preflight and pipeline accept `Date,Votes,Note\n2026-10-26,10,broken"quote` and a total row containing `Total,1"0`. Validate CSV syntax through one shared reader before ignoring fields or rows.

- [runbook/advance.md:36](/Users/byron/repos/unattended/.worktrees/nz-election-advance-preflight/product/nz_election/runbook/advance.md:36): No documented recovery path for a legitimate shorter correction. The loader checks every historical transition, so appending a later, longer capture cannot repair a registered shorter transition. Document a reviewed supersession procedure that preserves immutable captures and explains manifest handling.

Nit: None.

Read-only probes confirmed `SHORTER_ADVANCE_CAPTURE`, `MISSING_ADVANCE_CAPTURE`, duplicate-date and decreasing-cumulative rejection, BOM/blank-row handling, and `captured_at: null`. Observed validation errors did not echo raw CSV content. Preflight shares observation parsing but duplicates CSV/header validation.

No existing tests were weakened: 126 test lines added, none removed. No pytest run or files changed. Probes used `python3 -B` because `uv` required a temporary-directory write blocked by the sandbox.