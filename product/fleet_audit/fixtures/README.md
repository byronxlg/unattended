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


## Increment 4: three-way drift

The existing real `observer/com.unattended.tick.json` runatload,
`observer/org.nixos.skhd.json` keepalive,
`observer/com.pdw.docker-restart.json` calendar, and
`observer/snapshot-com.apple.talagent.json` multi-calendar records are reused
without recapture or additional loaded fields. Their original provenance,
source commit 18c8e8c, capture times and timestamp limitations remain in those
records. Tests and drift acceptance parse these exact files.

`drift/` contains small synthetic snapshots: `drift-registry-disk`,
`drift-registry-loaded`, `drift-disk-loaded`, `drift-missing-side`,
`drift-absent-service`, `argv-boundaries`, `calendar-equivalent`,
`calendar-wildcards`, `interval-and-calendar`, `policy-positive-tokens`,
`policy-missing`, `policy-unsupported`, and `running-drift`.
They derive the declaration, plist, output metadata, completed synthetic receipt,
inventory and overrides from `verdicts/completed-no-result` at b786941.
The minimal service blocks are hand-authored synthetic inputs, with no environment
blocks. No environment values are included anywhere in these snapshots.
The synthetic clock is 2026-10-16T00:00:00Z; copied envelopes retain their frozen
synthetic observation times. None is a new host capture.

Each manifest identifies synthetic provenance and the timestamp limitation;
member references include byte counts and SHA-256. Expected pair statuses and
verdict/rule/exit values were selected directly from the specification before
running the implementation, then checked against replay. The three pair entries
are ordered registry-to-disk, registry-to-loaded, disk-to-loaded. Acceptance
requires reviewed=true, validates all expected comparison statuses and findings,
and runs under the existing offline guard with live-clock traps. Unknown cases
produce uncertainty without findings. `running-drift` proves rule 6 remains
running while independent findings force exit 1.

Increment 1 to 3 fixtures and tests are unchanged.

## Increment 5: scan and complete reports

`fleet/` adds ten small synthetic snapshots: `scan-apple-filter`, `scan-no-label`,
`scan-disabled`, `scan-loaded-disabled`, `scan-service-absent`,
`scan-empty-coverage`, `report-escaping`, `report-mixed-exits`,
`report-unattempted`, and `report-environment-redaction`. They are hand-authored
cases with synthetic clock 2026-10-16T00:00:00Z. Expected verdicts and exits come
from decisions 1, 2, 6 and 9, independently of evaluator output. Their manifests
label sources, timestamp limitations and every member's hash and byte count.
The redaction snapshot contains a key with an empty placeholder; the test injects
an ephemeral sentinel to verify that text, JSON and capture remove values.

`fleet/real-twelve` reuses all twelve `observer/audit-*` rows. The composition
and reconstructed plist bytes are synthetic, not a new host capture. Real
command members preserve service stdout/stderr and rc from those rows, with
argv executable canonicalized from `launchctl` to `/bin/launchctl` for indexed
replay. The separate real snapshot inventory and supervisor print-disabled
capture corroborate coverage; they are not represented as simultaneous evidence.
Source is spike commit 18c8e8c and the existing print-disabled fixture. No
original host paths are opened, and no additional fields are invented.

The composition identity is 2026-10-15T13:37:56.188884Z; discovery is synthetic.
Per-command and original plist read times remain null. Log mtimes are converted
from the recorded epoch numbers to UTC; their observation clock is the recorded
row time, not a newly asserted stat time. Sizes were not captured and remain
null. Log existence is established by the captured mtime; no contents are read.
Homebrew skhd, caffeinate and Ollama have running pids; both nix jobs retain
exit 78/EX_CONFIG. Keystone rows retain null labels and unattempted lookups.
The tick's RunAtLoad remains observed, and its unavailable environment keys
are not fabricated from later evidence.

Fleet acceptance also reuses the three `verdicts/real-content-*` compositions
and their exact real receipt contents; synthetic timing does not assert they
were final lines during the spike capture. Earlier fixtures and tests remain
unchanged. The supervisor's declaration now exists at `runbook/fleet/fleet.md`;
the increment 3 note about its absence describes that earlier increment.

The fleet stage runs under the same fixture-only filesystem/process guard and
live-clock traps as other stages, and rejects any unreviewed expected placeholder.
