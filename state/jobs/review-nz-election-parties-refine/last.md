**Verdict: accept.**

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Read-only, in-memory verification of the test functions:
- `tests/test_parties_refine.py:13`: all 13 cases pass on HEAD. On `729f9e7`, four licence and five caption cases fail.
- `tests/test_parties_refine.py:25`: missing-source tests pass on both revisions. Rejection already existed; requiring base failures is inconsistent with the baseline.
- `pipeline/snapshots.py:457`: exact source-specific licences strengthen the removed global membership check. Both committed snapshots load, seven records each; 52 malformed-field probes reject.
- `pipeline/parties_page.py:102`: rendered caption checks pass. Complete HTML matches main byte-for-byte with committed facts and both empty and populated averages, preserving content and order.

Seven existing page checks also pass. Full pytest and screenshot question tests were not rerun; screenshots remain supervisor-owned under the brief.