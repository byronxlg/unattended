# Registry fixtures

Source: read-only `spike/audit.json` in `.worktrees/spike-fleet-audit` at
commit `18c8e8c`, macOS 26.5. Capture-level `collected_at` is
`2026-10-15T13:37:56.188884+00:00`; it is not a per-plist read timestamp.

Real projections (JSON): `com.unattended.tick`, `com.google.GoogleUpdater.wake`,
`com.google.keystone.agent`, `com.google.keystone.xpcservice`. Each contains only
the original path, capture-level time, source and declared plist projection.
No command, environment value, service observation, or receipt is copied.
Both Keystone projections are empty; no labels are inferred from filenames.
The tick projection contains RunAtLoad true but does not include
EnvironmentVariables: the spike projection excluded that field. Its real keys
cannot be recovered from this source. No environment keys have been invented
in the real projection or reconstructed tick plist.

Synthetic inputs:

- The four corresponding `.plist` files are reconstructed XML, not captured bytes.
- `registry-valid`, `registry-schema-errors`, `registry-duplicate-project`,
  `registry-duplicate-job`, `registry-duplicate-identity`, `registry-label-mismatch`,
  `registry-path-errors`: Markdown declarations with logical `/fleet-fixtures/`
  paths. The valid declaration deliberately has no RunAtLoad expectation.
- `plist-xml.plist`, `plist-binary.plist`: equivalent synthetic dictionaries,
  including exact argv boundaries and an unsupported KeepAlive mapping.
- `plist-environment-keys.plist`: synthetic key and synthetic marker value only.
  The parser retains the key and discards the value before producing any record.
- `file-too-large.json`, `nonregular-file.json`, `discovery-limit.json`: compact
  generation recipes used by tests for 1 MiB + 1 byte, a FIFO, and 1,001 Markdown
  files. Generated files live only in pytest temporary directories.

Acceptance uses an indexed file adapter; it fails on any unindexed path. Its
synthetic observation time is fixed at 2026-10-16T00:00:00Z and is not real evidence.
Console tests copy synthetic runbooks and replace logical fixture plist paths
with temporary absolute paths before invoking the declared entry point.
