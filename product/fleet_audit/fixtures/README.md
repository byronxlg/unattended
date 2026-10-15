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

## Observer increment

`observer/` retains three separate real capture groups, all from spike commit
`18c8e8c`. Each JSON envelope labels its source, capture clock and timestamp
limitations. The five original named command records are separate from all
12 `audit-*` rows and the `snapshot-*` records. The original snapshot clock is
`2026-10-15T13:24:32.844438+00:00`; audit clock is
`2026-10-15T13:37:56.188884+00:00`. Per-command timestamps were not recorded.
Audit row `observed_at` numbers are preserved, not merged with either clock.
Tick run counts remain 28 in the original and 29 in the audit.

Snapshot projections retain inventory, disabled map, blank exit-1 list and three
Apple parser records. Their normalized projections come from `records.json` at
the same commit. Apple records are parser inputs only. All environment values
in command streams have been replaced with `[redacted]`; only keys survive.
This also applies to default and inherited environments. Plist projections
retain the original spike's limited fields, not invented original plist bytes.

`print-disabled.json` is real supervisor evidence from
`intent/fleet-audit/evidence/print-disabled-gui501-2026-10-16.txt`, rc 0.
Only its capture date, 2026-10-16, is known. It preserves all 15 entries,
including five disabled Apple labels and disabled com.koekeishiya.yabai.

Synthetic recipe envelopes name blank-success, wrong-domain, wrong-label,
unrelated-113, truncated-service, duplicate-state, invalid-pid, never-exited,
override-denied, override-incomplete, override-absent, timeout,
combined-output-limit, snapshot-missing-entry and snapshot-path-escape.
Tests apply these recipes to the named real commands or fake process adapters.

`host/` is a synthetic composition, not a new real host capture: registry-valid
and its reconstructed plist, real blank exit-1 inventory, original tick service,
and supervisor override map. The manifest indexes members with byte lengths,
SHA-256, origin and source. Command keys include the synthetic capture identity.
Legacy list failure is indexed as inventory evidence while its original argv
is preserved. Synthetic envelope times use source capture clocks, with null
for the standalone override whose time is unavailable; they are not real command times.
The reviewed expected assertions are explicit: one retained job, rule 1,
cannot_determine and rc=1. Capture-generated expected placeholders remain
unreviewed and cannot be used for acceptance without review.

## Increment 3: verdicts and freshness

`verdicts/real/` preserves three real receipt lines from `state/ticks.jsonl` at
commit `d0dd7de`: `ran-zero` (2026-10-15T08:38:30Z), `usage-limit`
(2026-10-15T11:24:08Z), and `not-ran` (2026-10-15T08:34:36Z).
`provenance.json` records each SHA-256 over the exact line excluding its LF.
Only producer timestamps are known; these contents do not establish what was
the final line during a spike observation. No original file is opened in replay.

Every other directory under `verdicts/` is a synthetic snapshot with frozen
clock 2026-10-16T00:00:00Z, except real-content scenarios whose synthetic receipt
observation time equals the producer timestamp. `real-content-*` metadata and
clocks are synthetic with the real-content source/hash recorded in the manifest.
Synthetic service observations derive from increment 2's real tick command and
print-disabled captures; the inventory is reduced to one synthetic tick row.
No environment values are retained. Each member has a byte length and SHA-256.
The declaration is synthetic, using the spec's example runbook contract
(M=1200, G=1800); this checkout does not yet contain `runbook/fleet.md`.

Frozen scenarios: `completed-no-result`, `failed-nonzero-rc`, `failed-ran-error`,
`failed-not-ran-error`, `unestablished-null-rc`, `missing-supervisor`,
`invalid-producer-fields`, `mtime-sufficient`, `mtime-insufficient`,
`running-old-exit`, `running-ancillary-error`, `keepalive-no-exit`,
`expected-disabled`, `unexpected-disabled`, `enabled-absent`, `loaded-disabled`,
`contradictory-state`, `permission-denied`, `future-time`, `grace-window`,
`stale-failed-receipt`, `malformed-tail`, `concurrent-tail`, and `age-boundaries`
(the latter indexes five snapshots at -1, 1200, 1201, 3000 and 3001 seconds).
Expected verdict/rule/exit assertions were selected from the spec decision table,
then checked against replay; they were not copied from evaluator output.
The no-result fixture follows supervisor decision 4, overriding the receipt
algorithm's statement that all producer fields must be present.
