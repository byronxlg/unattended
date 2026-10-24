# Follow-up 1: campaign checks must not echo upstream text

The fresh review of PR #75 requests changes, one Important, confirmed by the supervisor:

`product/nz_election/pipeline/campaign_checks.py:183` forwards `str(error)` from `check_absent_text`
into the failure message, so upstream page text reaches the log and the status row. Reproduced:
`<section><h2>RAW_UPSTREAM_SENTINEL</h2></section>` gives
`CAMPAIGN_ABSENT: EMPTY_MODULE: RAW_UPSTREAM_SENTINEL`.

The same shape exists elsewhere in this file: line 42 (the data key), line 58 (`checked_load`
forwards the loader's message), line 94 (the EC party label), lines 152 and 168 (forwarded
exception text). Audit every `require(...)` and `raise ValueError(...)` in the file.

Invariant: a campaign failure message is a code plus a fixed description, optionally with
structural locators we generate (a snapshot row id we own, an index, a field name from our own
schema). It never contains text taken from an upstream document, HTML, XML or a forwarded
exception string. You choose how (a fixed table of descriptions, or passing only the code through).

Definition of done:
- Tests that feed a marker string (for example `RAW_UPSTREAM_SENTINEL`) through each of the
  paths above and assert the marker is absent from the raised message while the code is present.
- Show one of them failing on eb27b19 (name it in last.md).
- `uv run --with pytest pytest -q product/nz_election` passes; `bin/lint` ok;
  `PYTHONPATH=. uv run python product/nz_election/verify.py campaign` still PASS.
- Tests on main at bec0594 are not edited; this branch's own tests may move with the fix.
- Commit in the worktree, do not push. Do not commit last.md.
