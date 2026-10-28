Verdict: **request changes**.

- **Important**: [settlement_capture.py:84](product/nz_election/pipeline/settlement_capture.py#L84) does not guarantee named, sanitized errors for malformed bundles. Read-only probes through the actual validator produced uncaught `TypeError` for null/numeric JSON and an unnamed `JSONDecodeError` for empty input. An input-controlled key also leaked through:
  ```text
  ValueError INVALID_TIMESTAMP: envelope.data.RAW_UPSTREAM_SENTINEL.generated_at
  ```
  Normalize validation failures to safe named codes at this boundary. Add tests asserting exact codes and absence of upstream text.

- **Nit**: [runbook/night.md:524](product/nz_election/runbook/night.md#L524) passes literal `PRE_IMPORT_DATA_SHA` despite now defining a shell variable above. Use `data_sha="$PRE_IMPORT_DATA_SHA"` and clarify assignment/substitution for `SETTLED_DATA_SHA`; copied commands currently fail `NIGHT_DATA_SHA`.

Fix-1 correctly excludes election content from the label scan. The DemocracyNZ regression test checks preserved capture content and provenance. Deterministic serialization and settlement row comparison look sound.

Verification: in-memory probes via `.venv/bin/python -B -c` completed. `uv run --offline --no-sync` failed because the read-only sandbox denied cache access. Full tests were not rerun; the supplied 92-pass and round-trip evidence remains supervisor-provided. No files changed.