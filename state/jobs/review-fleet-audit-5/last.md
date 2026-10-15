1. **Important** - `product/fleet_audit/fleet_audit/scan.py:52`: Plist field errors are omitted from uncertainties. Reproduced with the caffeinate fixture, `StandardOutPath=42`, and an explicit enabled override: `verdict: running uncertainties: [] exit_code: 0`, despite `StandardOutPath: invalid value`. Rule 6 bypasses rule 9, violating the requirement that ancillary errors prevent exit 0.
   Suggested fix: Preserve plist field errors in job uncertainties before evaluating verdicts.

2. **Important** - `product/fleet_audit/fleet_audit/receipts.py:21`: UTC conversion can raise uncaught `OverflowError`. Calling `normalize_tick` with `ts="0001-01-01T00:00:00+01:00"` produces `OverflowError: date value out of range`. Neither receipt parsing nor the CLI catches it, so a receipt can crash the audit instead of producing uncertainty.
   Suggested fix: Catch `OverflowError` alongside `ValueError` and classify the timestamp as invalid.

Verification from `product/fleet_audit`: `.venv/bin/python -B -m fleet_audit.acceptance <stage> --offline` produced:

```text
OK fleet
OK registry
OK observer
OK verdicts
OK drift
```

`.venv/bin/python -B -m fleet_audit.cli scan --fixture fixtures/fleet/real-twelve` emitted 12 rows and exited **1**. Pytest import failed with `ModuleNotFoundError: No module named 'pytest'`; tests reviewed by reading, nothing installed.

Important findings: 2