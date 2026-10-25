Verdict: **request changes**

Critical: None.

Important:
- `product/nz_election/pipeline/result_import.py:104-114`: The import reports PASS and dispatches Pages without confirming the publisher applied the transition. A reachable pinned SHA can contain an older live capture than the current data head. `publish.py:160-174` then retains the newer live data despite the requested settled state. Read-only probe: pinned `10:35`, current `10:36`, requested settled → `keep_data=True`, retained live. Reject this conflict with a named code before publication, or otherwise ensure the published night family matches the verified transition.

Nit: None.

Read-only provenance probes passed: malformed sources/dates returned `NIGHT_STATE`; committed synthetic captures returned `NIGHT_CAPTURE_NOT_REAL`. No pytest run or files changed.