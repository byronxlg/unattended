Verdict: **accept**.

Findings: none.

Public outputs use `public_locator`; scanner counters cannot contain source text. Positions reset between tables. Unterminated rowspan errors identify the final row where detected, acceptable for operators. Marker tests cover `refresh()`, `main()`, persisted status and the summary file. Existing tests and fixture bytes are unchanged.

Verification commands were blocked by the sandbox:

- `bash evals/polls-date-exception-revision/check.sh`
  Output: `cannot create temp file for here document: Operation not permitted`
- `uv run --with pytest pytest -q product/nz_election/tests/test_date_exception_revision.py product/nz_election/tests/test_poll_parser.py`
- `bin/lint`

Both latter commands reported:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
```

Running the eval’s Python body in memory produced:
```text
PASS exception row parsed on revision 9999999999
```

Additional in-memory probes confirmed the incident locator `table:15/row:19`, empty locators for later scanner failures, structural locators for malformed rows, and rejection of malformed date inputs.

Full pytest and lint verification remain outstanding.