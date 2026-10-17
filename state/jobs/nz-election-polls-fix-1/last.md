Committed `05d9b0a`; working tree clean.
`models.py`: separate public locator; exception text unchanged.
`poll_parser.py`: scanner-generated positions; incident reports `table:15/row:19`.
`refresh.py`: public outputs use structural locators only.
Branch tests verify source markers never reach status, logs, or summaries.

`evals/polls-date-exception-revision/check.sh`
```text
PASS exception row parsed on revision 9999999999
```

`uv run --with pytest pytest -q product/nz_election`
```text
408 passed in 174.92s (0:02:54)
```

`bin/lint`
```text
lint ok (393 text files)
```

No push, fixture edits, main-test edits, or `last.md` changes.