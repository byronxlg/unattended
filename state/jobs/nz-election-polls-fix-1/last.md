Committed `beb364c`; working tree clean.
`poll_parser.py`: exceptions match rows across revisions; malformed dates still fail.
`party-map.json`: explicit source URL preserves the documented exception.
`refresh.py`: reason and locator reach status, Actions log, and summary.
`test_date_exception_revision.py`: added 29 regression cases.

`evals/polls-date-exception-revision/check.sh`
```text
PASS exception row parsed on revision 9999999999
```

`uv run --with pytest pytest -q product/nz_election`
```text
401 passed in 172.27s (0:02:52)
```

`bin/lint`
```text
lint ok (393 text files)
```

No push, fixture edits, existing-test edits, or job-state changes. No open questions.