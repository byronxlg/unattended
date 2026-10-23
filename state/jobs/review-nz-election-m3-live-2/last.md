Verdict: **accept**.

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Both prior findings are fixed. Regression tests at `product/nz_election/tests/test_night_operation.py:294` and `:335` target the old failures; inspection confirms both would fail on `727561e`.

The harness change preserves all assertions: no hidden fetches, exactly one synchronous resume fetch, and existing error backoff. Freeze guards cover recovery, publication, and deployment. Replay/demo labels remain enforced. Merge-base tests retain their checks. No secrets found; permissions match required operations; recovery consumes a five-minute cycle slot.

Verification: read-only pytest subset returned `11 passed, 7 deselected in 0.31s`. In-memory comparison confirmed unchanged acquisitions publish one retrieval time on `727561e`, four on `b7ac47e`; freeze and mode probes passed.

Limitations: filesystem-writing integration tests were inspected, not rerun. Browser verification relies on supplied host evidence: PASS, 60 images. No files changed.