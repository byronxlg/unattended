Committed `a86415d`; not pushed. **Blocked by six unchanged tests that conflict with the new invariant.**

- `poll_parser.py`: seven-day release lag; visible dates win.
- Accepted mismatches include source and reason diagnostics.
- Existing documented exception diagnostics remain intact.
- Added offline `evals/polls-release-date-sort/`.
- Added 22 boundary and malformed-input tests.

Verification:
```text
New eval on 57063db:
FAIL parse_drift invalid_dates table:15/row:2

evals/polls-release-date-sort/check.sh:
PASS release-date row parsed

evals/polls-date-exception-revision/check.sh:
PASS exception row parsed on revision 9999999999

Host-side saved live-file parse:
Live revision 1381086195: rows=44, Freshwater 2026-10-19 exists=True

uv run --with pytest pytest -q product/nz_election:
6 failed, 692 passed in 297.76s (0:04:57)

bin/lint:
lint ok (508 text files)
```

The six failures require the August Verian one-day mismatch to fail when its hand-written exception is altered or removed. That contradicts general release-date acceptance.

Left existing tests and fixture bytes unchanged; avoided a historical-row workaround. `last.md` is uncommitted. Supervisor must reconcile those legacy expectations before this meets done.