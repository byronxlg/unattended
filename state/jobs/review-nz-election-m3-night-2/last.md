Verdict: **request changes**.

- **Important**: `product/nz_election/pipeline/night.py:86` infers “Final snapshot” from the absence of derivation metadata. Keep only illustrative step 0, remove `derivation` and `elapsed_seconds`, copy the archive timestamp, and relabel its row and sequence “Final snapshot”. Full `night.prepare()` and `night.validate()` accept **285,114 synthetic votes as final results**, with matching hashes and CSVs. Reproduced using an in-memory filesystem. Validate archive-labelled rows against their source capture, independently of removable metadata.

- **Important**: `product/nz_election/pipeline/xml_parser.py:109` does not bound electorate seats against the reference registry. Changing one 2023 party’s `candidate_seats` to `999` and adjusting its `total_seats` passes validation and returns **House 1119**, despite only 72 electorates. Reject impossible electorate-seat totals with `XML_TOTAL`.

- **Nit**: `product/nz_election/pipeline/verify.py:355` validates the outer bundle before checking for the night family. An empty `--data` directory therefore produces the reported `INVALID_INVENTORY` traceback instead of the documented missing-family diagnostic. This fails closed and prints no false PASS, so it is not a blocking correctness issue. Normalize CLI failure reporting or qualify the runbook.

The four prior fixes: demo label-only mutation is blocked; zero-vote contradictions return `XML_TOTAL`; supplied `--data` is inspected; empty/whitespace counts return `XML_COUNT`. The broader illustrative-relabel guarantee remains incomplete above.

Read-only Python probes produced:
```text
2017 2591896 120
2020 2886420 120
2023 2851211 122
replay smoke 2851211 122
```

No page code or weakened existing tests found; the existing manifest-count assertion increases from 117 to 130. No half-publication path found in the staging/exchange logic.

Verification attempt: `PYTHONDONTWRITEBYTECODE=1 uv run --offline --with pytest pytest -q product`
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: ... Operation not permitted (os error 1)
```
Full tests and filesystem publication checks remain unverified here. No files edited. The prior review report was absent; its four findings were assessed from your summary and `272eb6e..6e1547b`.