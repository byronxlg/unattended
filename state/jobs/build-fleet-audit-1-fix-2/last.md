Committed `71dfabe`; not pushed. Working tree clean.
Changed `plists.py`, `tests/test_plists.py`, and `tests/test_registry.py`: contained parser exceptions and rejected non-JSON-safe KeepAlive values.

Package `uv run --with pytest pytest -q`, exit 0:
```text
........................................................................ [ 36%]
........................................................................ [ 72%]
......................................................                   [100%]
198 passed in 1.06s
```

Package `uv run python -m fleet_audit.acceptance registry --offline`, exit 0:
```text
OK registry
```

Root `bin/lint`, exit 0:
```text
lint ok (101 text files)
```

Nothing outstanding.