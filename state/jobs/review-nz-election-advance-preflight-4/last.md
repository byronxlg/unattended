Verdict: **accept**

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Confirmed at `advance_preflight.py:85-91`: unexpected exceptions and serialization failures produce fixed diagnostics without exception text or capture content. `MISSING_EVIDENCE`, `KeyboardInterrupt`, and `SystemExit` retain their behavior. Successful JSON intentionally includes headers.

Earlier requirements hold: explicit semantic evidence, shared CSV validation before filtering, documented supersession, and no raw headers in failure diagnostics. Tests from main `f5becd4` are unchanged; additions only.

Verification: `python3 -B -c '<read-only probes>'`
```text
PASS: 60 read-only probes; no pytest
```
Used Python directly because uv required temporary writes denied by the sandbox. No files changed.