Verdict: **accept**.

- Critical: none.
- Important: none.
- Nit: none.

Both reported escapes are closed: `campaign_checks.py:45` redacts ordinary exceptions; `verify.py:495` selects redaction using the parsed check. Owned codes survive, process-control exceptions propagate, and other individual checks retain their error handling. No existing check was loosened or removed from `all`.

Read-only probes via `python3 -B -c`:
```text
PASS 65 read-only exception/dispatch/shape probes
PASS committed snapshots and rendered markup: 146 donations, 20 scorecard rows
```

Pytest not rerun. No files changed.