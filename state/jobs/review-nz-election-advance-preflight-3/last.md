Verdict: **request changes**.

Critical: None.

Important:
- `product/nz_election/tools/advance_preflight.py:88`: CLI sanitizes only `OSError` and `ValueError`. Injected `RuntimeError`, `KeyError`, and `TypeError` escape with `CAPTURE_MARKER` intact; uncaught execution prints their text in a traceback. The requirement that unexpected exceptions never forward their text remains unmet. Add a fixed-message fallback at the CLI boundary.

Nit: None.

Confirmed: original header leak fixed; explicit daily/cumulative evidence required; shared CSV validation rejects malformed quoting before filtering; supersession runbook remains intact. No tests from `f5becd4` were modified or removed.

Read-only probes via `python3 -B -c` (`uv` could not create its temporary directory):

```text
Malformed-input probes: 24 fixed diagnostics
Missing-evidence probes: 3 fixed diagnostics
Injected ValueError: SystemExit: INVALID_ADVANCE
Injected RuntimeError: RuntimeError: CAPTURE_MARKER
Injected KeyError: KeyError: 'CAPTURE_MARKER'
Injected TypeError: TypeError: CAPTURE_MARKER
```

No pytest run or files changed.