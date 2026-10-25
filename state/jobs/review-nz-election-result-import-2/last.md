Verdict: **accept**

- Critical: None.
- Important: None.
- Nit: None.

Confirmed at `publish.py:196-201`: complete night-file bytes must match before any return or publication, on every lease attempt. Mismatches raise `NIGHT_IMPORT_CONFLICT`, preventing the import summary and Pages dispatch.

Existing callers retain main’s publisher logic with the new options disabled. `runbook/night.md:418-423` matches the behavior. No tests on main were modified.

Read-only probes passed: six byte-comparison cases, default-behavior AST comparison, and retry-loop guard placement. No pytest run; no files changed.