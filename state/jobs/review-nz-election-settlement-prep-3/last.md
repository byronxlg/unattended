Verdict: **accept**. Review opinion only, not approval.

No Important or Nit findings in the full product diff against `origin/main`.

- Fix-2 sanitizes CLI failures to `NIGHT_CAPTURE_PREP_FAILED`, without upstream text.
- Runbook SHA assignments and dispatch arguments match the import workflow.
- Deterministic serialization, preserved provenance, exact baseline comparison and exclusive output creation remain intact.
- Tests check behavior, including malformed inputs and preparation/import round-trip.

Verification: `python3 -B -c '<in-memory CLI-boundary probes>'`
```text
PASS 8 malformed-input CLI-boundary probes (in memory, no writes)
```

Attempted:
```text
uv run --offline --with pytest pytest -q -p no:cacheprovider product/nz_election/tests/test_settlement_capture.py
```
Blocked by read-only permissions:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
```

Full-suite and round-trip confidence relies on the supplied supervisor evidence. No files changed. No open questions.