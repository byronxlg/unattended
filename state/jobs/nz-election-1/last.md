Committed `281e6d8` on `change/nz-election-1`; not pushed.

Changed: Python/JS allocators, fixture loader, poll parser, models, four configs, 24 tests and parity runner, product instructions, root pointer and pytest collection.

Verification:

```text
uv run --with pytest pytest -q product/nz_election/tests/test_allocator.py product/nz_election/tests/test_poll_parser.py
........................                                                 [100%]
24 passed in 0.27s

uv run --with pytest pytest --collect-only -q | grep -c "^tests/"
84

uv run --with pytest pytest --collect-only -q | grep -c "^product/nz_election/tests/"
24

uv run --with pytest pytest -q
........................................................................ [ 66%]
....................................                                     [100%]
108 passed in 0.85s

bin/lint
lint ok (165 text files)

git status --short
```

Final status output was empty.

Departures: read missing plan from local commit `62d3ff6`; `tests/test_ci.py` was absent. Kept fixtures immutable, generating golden inputs in memory and synthetic cases in tests. Recorded a revision-specific exception using visible 8-11 August fieldwork dates instead of the conflicting 12 August sort date.

Open questions: supervisor review of that date exception.