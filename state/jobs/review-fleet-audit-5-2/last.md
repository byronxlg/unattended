- **Important** - `product/fleet_audit/fleet_audit/scan.py:54`: Unsupported plist fields still disappear from uncertainties. Replaying the running Ollama row with `KeepAlive={"SuccessfulExit": false}` produces `uncertainties=[]`, summary count `0`, no text uncertainty line, and exit `0`, despite retaining an `Unsupported` policy in evidence. Suggested fix: include unsupported plist fields in uncertainties, deduplicating existing field errors.

- **Important** - `product/fleet_audit/fleet_audit/files.py:108`: Output mtime conversion catches only `OSError`. Mocking `os.stat` with `st_mtime=253402300800` raises `ValueError`; `1e20` raises `OverflowError`. Scan loses its report, returning invalid-input exit `3` or an uncaught traceback instead of retaining an observation uncertainty. Suggested fix: catch both conversion exceptions and return a stat-error observation.

Verified field errors now appear in summary counts and text `uncertainty:` lines. Audit still rejects them before collection. Both added tests match their names; no existing tests, fixtures, or `conftest.py` changed in d00b16b.

From `product/fleet_audit`, `.venv/bin/python -B -m fleet_audit.acceptance <stage> --offline` produced:
```text
OK fleet
OK registry
OK observer
OK verdicts
OK drift
```
Pytest unavailable: `ModuleNotFoundError: No module named 'pytest'`. Tests reviewed by reading; nothing installed or changed.

Important findings: 2