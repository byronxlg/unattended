<!-- Plan for intent/fleet-audit, written by the read-only Codex plan job plan-fleet-audit (thread 01a13fdf-48e3-7603-a851-6be5f7421375, 2026-10-16 03:09 NZ). -->
<!-- Accepted by the supervisor 2026-10-16 03:20 NZ; the acceptance note is at the end of the file. -->

# Fleet Audit implementation plan

## Scope and delivery

Implement the accepted specification at `/Users/byron/repos/unattended/intent/fleet-audit/spec.md`, including all twelve Supervisor decisions. Those decisions override the body, particularly receipt completion, scan loaded-disabled behavior, environment redaction, and package layout.

Deliver five sequential PRs on `change/fleet-audit-1` through `change/fleet-audit-5`. Each starts from the preceding merged increment, includes its fixtures and verification, and remains buildable independently. Engineers commit only inside their assigned worktree; the supervisor handles publication and merging. Paths below identify repository locations in the planning checkout; implement corresponding repository files inside the assigned worktree.

Product commands write only stdout and stderr, never execute job programs, and never mutate launchd. Application paths are absolute, normalized, literal strings: no tilde, environment expansion, realpath substitution, or shell splitting. Snapshot member references are internal relative names, not application paths.

No implementation, launchctl execution, installation measurement, or product test execution occurred during planning. Cross-version launchctl compatibility and supervisor semantic success are not shown.

## Package and installation

Create these files under the absolute package project directory:

| File | Responsibility |
| --- | --- |
| `/Users/byron/repos/unattended/product/fleet_audit/pyproject.toml` | Build metadata, dependency pin, console entry, pytest configuration. |
| `/Users/byron/repos/unattended/product/fleet_audit/uv.lock` | Committed resolved dependencies, including the build backend. |
| `/Users/byron/repos/unattended/product/fleet_audit/README.md` | Installation, commands, evidence limits, snapshot workflow, verification. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/__init__.py` | Package version; no collection side effects. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/models.py` | Immutable dataclasses and explicit known/unknown values. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/files.py` | Bounded regular-file reads, discovery, stat and tail acquisition interfaces. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/registry.py` | Strict frontmatter/schema validation and declaration-to-plist join. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/plists.py` | XML/binary plist parsing, typed fields, environment keys only. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/collect.py` | Bounded launchctl execution and domain/service collection. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/launchctl_parse.py` | Structural parsing and trusted service/domain normalization. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/overrides.py` | Complete override-map parsing and effective disabled state. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/output.py` | Output stat observations and observation-relative ages. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/receipts.py` | Final-line parsing and ticks_jsonl version 1 outcomes. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/verdicts.py` | Explicit ordered rule table and evidence-linked reasons. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/drift.py` | Three-way comparisons and schedule normalization. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/reports.py` | Stable text/JSON, summary, exit precedence. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/cli.py` | Argument validation and declared/audit/scan orchestration. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/snapshot.py` | Manifest validation, fixture-backed readers, no live fallback. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/capture.py` | Supervisor-only capture module emitting a snapshot archive to stdout. |
| `/Users/byron/repos/unattended/product/fleet_audit/fleet_audit/acceptance.py` | Offline proving stages; healthy line only after assertions pass. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/README.md` | Fixture inventory, source commit, capture times, transformations and provenance. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/conftest.py` | Fixture readers, deterministic clocks, forbidden-live-access guards. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_registry.py` | Schema, discovery, join and declared tests. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_plists.py` | Typed plist and redaction tests. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_observer.py` | Collection, structural parser, override and coverage tests. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_snapshot.py` | Snapshot validation, capture/replay and isolation tests. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_receipts.py` | Tail boundaries, races and producer outcomes. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_verdicts.py` | Ordered verdicts, freshness boundaries and uncertainty. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_drift.py` | Three pairwise comparisons and typed schedules. |
| `/Users/byron/repos/unattended/product/fleet_audit/tests/test_reports.py` | Scan, report schema, escaping, provenance and exit codes. |

The pyproject contents must specify project name `fleet-audit`, version `0.1.0`, Python `==3.12.*`, runtime dependencies exactly `PyYAML==6.0.2`, README metadata, and script `fleet-audit = fleet_audit.cli:main`. Use build backend `setuptools.build_meta` with build-only requirement `setuptools==75.8.0`; explicitly package `fleet_audit`. Pytest configuration: `testpaths = ["tests"]`, `addopts = "--strict-config --strict-markers"`. Pytest is a verification dependency supplied through `uv run --with pytest`, not a runtime dependency.

Run package commands with working directory `/Users/byron/repos/unattended/product/fleet_audit`. The build-system declaration makes uv install the local project and console entry. Thus `uv run fleet-audit` resolves `cli.main`, and `uv run python -m fleet_audit.acceptance` resolves the installed package module. Acceptance locates the checkout's adjacent fixtures explicitly, without depending on the caller's incidental working directory.

## Shared records and boundaries

Use frozen dataclasses. Generic `Value[T]` is a tagged union of `Known[T](value)`, `Absent(reason)`, `Unknown(reason)`, and `Unsupported(raw, reason)`. No variant permits implicit truth testing; operations require explicit variant matching. Boolean negation never turns unknown into false. `Absent` is usable only where a complete observation proves absence, such as an intact service block without pid.

| Record | Fields |
| --- | --- |
| `Error` | `code, message` |
| `ValidationError` | `file, field, code, message` |
| `Observation[T]` | `status, observed_at, source_command, return_code, error, data` |
| `Identity` | `host, domain, label` |
| `Project` | `project, owner, tier, lifecycle, reviewed, runbook_path` |
| `Schedule` | `interval_seconds, calendar, timezone, keep_alive, run_at_load`, each preserving presence and trust |
| `OutputContract` | `path, kind, max_age_seconds, mtime_sufficient` |
| `Declaration` | `identity, project, id, scheduler, plist_path, expected_program, expected_arguments, expected_working_directory, expected_schedule, expected_enabled, output, grace_seconds` |
| `RegistryResult` | `jobs, errors, discovery` |
| `PlistData` | `path, present_keys, label, program, arguments, working_directory, schedule, disabled, stdout_path, stderr_path, environment_keys, field_errors` |
| `CommandData` | `argv, stdout, stderr, timed_out, truncated, duration_seconds` |
| `DomainData` | `domain, labels, complete, warnings` |
| `ServiceData` | `identity, loaded, state, pid, runs, last_exit_code, last_exit_text, program, argv, working_directory, plist_path, schedule, properties, missing_fields, warnings, structural_valid` |
| `OverrideData` | `entries, complete, warnings` |
| `DisabledState` | `value, origin, entry, evidence_refs` |
| `FileMetadata` | `device, inode, size, mtime_ns, ctime_ns, regular` |
| `OutputData` | `path, exists, size, mtime, age_seconds, stat_error` |
| `TailData` | `path, before, after, path_after, offset, bytes_read, starts_at_line_boundary, tail_bytes, changed` |
| `ReceiptData` | `path, tail, last_object, ts, age_seconds, ran, rc, error, result, outcome, parsing_errors` |
| `Comparison` | `field, pair, left, right, status, evidence_refs` |
| `DriftFinding` | `kind, field, pair, reason, evidence_refs` |
| `Verdict` | `name, rule_id, reason, evidence_refs` |
| `JobRecord` | `identity, project, registry, plist_path, observations, loaded, disabled, comparisons, drift, verdict, uncertainties` |
| `Coverage` | `complete, issues, observations` |
| `FleetObservation` | `domain, observed_at, jobs, coverage` |
| `Report` | `schema_version, command, domain, observed_at, jobs, issues, summary, exit_code` |
| `Manifest` | `format_version, capture_clock, domain, macos_label, indexes, provenance` |
| `Snapshot` | `manifest, runbooks, plists, commands, stats, receipts, expected` |

Observation status distinguishes attempted, not_requested and not_applicable. Unattempted time/data/code remain null. File provenance has null return code; subprocess return code is null only when unavailable, including spawn failure or timeout. UTC RFC3339 timestamps and explicit nulls survive serialization. Unknown wrappers serialize as null values plus their uncertainty/presence information.

Public boundaries, with source sections:

- Registry: `discover_runbooks(directory: Path, files: FileSource) -> Observation[tuple[str, ...]]`; `parse_frontmatter(path: str, content: bytes, uid: int) -> RegistryResult`; `load_registry(directory: Path, uid: int, files: FileSource) -> RegistryResult`; `join_plists(registry: RegistryResult, files: FileSource) -> RegistryResult`. Implements **Runbook schema version 1**, **CLI and report contract**.
- Files/plists: `read_regular(path: str, limit: int) -> Observation[bytes]`; `parse_plist(path: str, content: bytes) -> PlistData`; `observe_plist(path: str, files: FileSource) -> Observation[PlistData]`. Implements **Evidence record and collection**, decisions 2 and 11.
- Collector/parser: `run_bounded(argv: tuple[str, ...], timeout_seconds: float = 10, max_bytes: int = 4194304) -> Observation[CommandData]`; `parse_domain(command: Observation[CommandData], domain: str) -> Observation[DomainData]`; `parse_service(command: Observation[CommandData], identity: Identity) -> Observation[ServiceData]`; `collect_jobs(jobs: tuple[JobRecord, ...], domain: str, source: CommandSource) -> FleetObservation`. Implements **Evidence record and collection**.
- Overrides: `parse_overrides(command: Observation[CommandData]) -> Observation[OverrideData]`; `effective_disabled(label: str, plist: Observation[PlistData], overrides: Observation[OverrideData]) -> DisabledState`. Implements **Evidence record and collection**, decisions 6 and 10.
- Output/receipts: `observe_output(path: str, files: FileSource) -> Observation[OutputData]`; `read_tail(path: str, files: FileSource, limit: int = 65536) -> Observation[TailData]`; `parse_receipt(tail: Observation[TailData]) -> Observation[ReceiptData]`; `normalize_tick(value: object) -> ReceiptData`. Implements **Receipt and freshness semantics**, decision 4.
- Verdicts: `coverage_failure(job: JobRecord, coverage: Coverage) -> Verdict | None`; `evaluate(job: JobRecord, coverage: Coverage, mode: str) -> Verdict`. Implements **Verdict decision order**, decisions 1, 3, 4, 5 and 9.
- Drift: `normalize_calendar(value: object) -> Value[tuple[tuple[tuple[str, int], ...], ...]]`; `compare_job(job: JobRecord) -> tuple[tuple[Comparison, ...], tuple[DriftFinding, ...]]`. Implements **Drift comparison**, decision 7.
- Reports: `build_report(command: str, fleet: FleetObservation) -> Report`; `exit_code(report: Report) -> int`; `render_text(report: Report) -> str`; `render_json(report: Report) -> str`. Implements **CLI and report contract**.
- CLI/scan: `main(argv: list[str] | None = None) -> int`; `scan_plists(directory: str, files: FileSource) -> FleetObservation`. Implements **CLI and report contract**, decisions 1, 2, 6 and 9.
- Replay: `load_snapshot(directory: Path) -> Snapshot`; `replay(snapshot: Snapshot, command: str) -> Report`. Capture: `capture_snapshot(directory: str | None, domain: str, mode: str) -> Snapshot`; `emit_archive(snapshot: Snapshot, stream: BinaryIO) -> None`. Implements **Offline replay and verification**, decision 12.

`FileSource` and `CommandSource` are injected interfaces implemented separately by live and snapshot adapters. Replay cannot construct the live adapters. Add observation types only when their increment needs them; increment 1 contains no launchctl implementation or imports.

## Validation and observation policy

Use a restricted PyYAML loader: reject aliases, custom tags, duplicate keys and nulls; restrict scalar recognition to the schema's explicit booleans and integers. Reject YAML coercions such as `yes`, floats in integer fields, and unquoted dates. Preserve scalar style to require a quoted `reviewed` date. Reject booleans as integers.

Implement every schema row, default, container rule, field error and literal message suffix from the spec. Validate every frontmatter-bearing Markdown file; ignore ordinary Markdown. Sort discovery, avoid directory symlinks, cap discovery at 1,000 files, and cap each runbook/plist at 1 MiB. Never check executable or working-directory existence. Label mismatch, missing Label and duplicate identities fail before any live service observation.

Preserve plist key presence separately from normalized values. Program falls back to argv[0] only on disk; missing argv stays missing. EnvironmentVariables retains keys only. Unsupported KeepAlive mappings remain unsupported, including the real Homebrew skhd/yabai mappings.

Collection uses explicit current-user domain and sequential `print domain`, `print domain/label`, and independent `print-disabled domain`. No production `launchctl list`. Drain stdout/stderr concurrently within a combined 4 MiB limit and 10-second deadline; terminate and reap on either limit. Reject partial success.

Only structurally valid, identity-matching responses establish loaded=true. Exact recognized exit-113 absence must match both requested label and GUI uid; other errors leave loaded unknown. Nested coalition state cannot replace root job state. Missing exit history, directory and timer fields remain unknown.

An explicit enabled override wins over disk Disabled=true. A complete map with no label falls back to disk Disabled, default false only for a valid plist. Failed or partial override maps establish unknown, never an empty known map.

## Ordered verdict engine

Represent rules as an immutable ordered table of `Rule(id, predicate, verdict_builder)`. Predicates return `Match(evidence_refs, details)` or `NoMatch`; they inspect trusted `Known` values or specifically permitted `Absent` states. Give every rule a stable numbered ID and test table order. No catch-all truthiness, nullable Boolean shortcuts, or hidden ordering across helper calls.

| Rule | Predicate and result |
| --- | --- |
| 1 | Global collection failure, unusable identity, unknown loaded, or structural invalidity: cannot_determine. |
| 2 | Effective disabled unknown: cannot_determine. |
| 3 | Loaded and disabled: loaded_disabled, including scan. |
| 4 | Absent and disabled: disabled; expected_enabled controls classification. |
| 5 | Absent and enabled: declared_not_loaded for audit; scan cannot_determine, `plist on disk, service absent; not declared`. |
| 6 | Loaded, root state running, positive pid: running; reason ends `useful work not established`. |
| 7 | Loaded, proven no pid, state not running/spawn scheduled, nonzero exit: failing. |
| 8 | Loaded, proven no pid, spawn scheduled, trusted KeepAlive=true: failing. Loaded policy preferred; disk fallback allowed only for this health rule. |
| 9 | Remaining errors, contradictory pid/state, required comparison unknown, or drift: cannot_determine. |
| 10 | No output contract, invalid/unavailable/future timestamp, or unresolved timing ambiguity: cannot_determine. |
| 11 | Loaded and A>M+G: late; retain receipt failure evidence. |
| 12 | Idle, failed receipt, A<=M+G: failing. |
| 13 | Idle, last exit zero, A<=M, completed receipt or explicit sufficient mtime: healthy_idle. |
| 14 | Otherwise cannot_determine, explaining grace, completion, exit history or state. |

Use the spec's reason templates verbatim, with decision overrides above. Rules 6-8 may retain ancillary uncertainties, which still influence report exit status. No collection error permits healthy_idle. Drift remains independent even when a higher rule returns running or failing. Until increment 4, requested but unsupported drift comparisons are explicit incomplete evidence, never silently equal.

## Receipt algorithm and contract

Open only the declared output path, require a regular file, record descriptor metadata, and read at most the final 65,536 bytes. Determine whether the retained region starts at a line boundary conservatively; a final line extending beyond the retained region is an error. Remove exactly one terminal LF and parse the last physical line, never searching backward for an older valid object. A partial first retained line may be discarded only if another final line follows.

Reject blank/oversized final lines, malformed UTF-8/JSON, duplicate JSON keys and non-object JSON. Compare descriptor metadata before/after and the final path identity, including device/inode/size/mtime_ns/ctime_ns; append, truncate, replacement or detected modification yields uncertainty without retries. A same-metadata modification may evade this check; atomic observation is not shown.

Validate timezone-aware RFC3339 `ts`, supervisor mapping and Boolean ran. Required producer fields rc/error/result must have the documented types; missing or invalid fields yield unestablished with validation details. Rc accepts null, integer excluding Boolean, or signed decimal string; no floats. Result is null/string and is never interpreted or required to be nonblank.

- Completed branch 1: ran=false, error=null.
- Completed branch 2: ran=false, error begins `skipped:`.
- Completed branch 3: ran=true, parsed rc=0, error=null.
- Failed branch 1: ran=true, parsed rc nonzero.
- Failed branch 2: ran=true, error non-null, including empty string.
- Failed branch 3: ran=false, error non-null without `skipped:` prefix.
- Otherwise unestablished, including missing supervisor or ran=true/rc=null/error=null.

Use receipt ts, never mtime, for receipt age. Mtime evidence requires explicit mtime_sufficient=true for health. Scan has no invented freshness budget. Keep M=1200 and G=1800 for the lab.

## Snapshot and fixture format

A canonical example snapshot root is `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host`. Its files are:

| Location | Contents |
| --- | --- |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/manifest.json` | Version 1, capture clock, GUI domain, macOS label, logical-path and command indexes, provenance. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/runbooks/` | Indexed Markdown bytes. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/plists/` | Indexed XML/binary plist bytes, environment values removed with redaction recorded. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/commands/` | Command envelopes with argv, times, rc, bounded streams and errors. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/stats.json` | Logical-path stat observations, including explicit failures. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/receipts/` | Tail bytes plus boundaries, before/after metadata and observation times. |
| `/Users/byron/repos/unattended/product/fleet_audit/fixtures/host/expected.json` | Independently reviewed assertions, never generated as self-confirming expected output. |

Each indexed entry records member name, byte length, SHA-256, origin classification and source reference. Command keys include argv and capture identity, so separate observations cannot overwrite each other. Validate all references before collection: reject escaping paths, symlinks, missing entries, invalid versions, malformed envelopes and oversized members. Original absolute application paths are lookup keys only.

Capture is a module entry invoked by the supervisor with `uv run python -m fleet_audit.capture audit /Users/byron/repos/unattended/runbook --domain gui/501`; support a corresponding scan mode. It emits an uncompressed snapshot tar stream to stdout and diagnostics to stderr. The supervisor materializes that stream into a chosen snapshot directory. This preserves the product's stdout/stderr-only write contract. The archive includes expected.json as an explicitly unreviewed placeholder; acceptance refuses it until assertions are reviewed.

Redact environment values before archiving command streams or plist bytes, preserving environment keys and structural boundaries. Retain malformed structure as malformed; do not repair the networkserviceproxy fixture. Record redaction transformations. Capture only allowed plist/runbook/output evidence; never follow paths embedded in receipt contents.

Replay re-runs parsing, normalization, verdicts and reporting using frozen observation times. Missing entries are invalid input, exit 3; recorded ENOENT, denial, timeout or malformed output are valid failure evidence. Snapshot mode must never fall back to live execution, current clocks or original-path reads. Acceptance guards all three.

Freeze source provenance from `/Users/byron/repos/unattended/.worktrees/spike-fleet-audit/spike/`. Keep the five original command fixture records separate from the twelve-row audit capture and original snapshot capture. Do not invent precise observation times absent from the source; mark timestamp limitations. The standalone print-disabled evidence supplies rc=0 and capture date, not a precise command timestamp.

## Increment 1: registry and plist join

Branch `change/fleet-audit-1`.

- Create packaging, lockfile, initial README, `__init__`, models, files, registry, plists, declared-only CLI/reports, registry acceptance, conftest, registry/plist tests and fixture README from the file inventory.
- Freeze real audit plist projections for `com.unattended.tick`, `com.google.GoogleUpdater.wake`, and both no-label records `com.google.keystone.agent.plist` and `com.google.keystone.xpcservice.plist`. Original plist bytes are not shown by those projections; reconstructed XML/binary inputs must be labelled synthetic.
- Freeze labelled synthetic records `registry-valid`, `registry-schema-errors`, `registry-duplicate-project`, `registry-duplicate-job`, `registry-duplicate-identity`, `registry-label-mismatch`, `registry-path-errors`, `plist-xml`, `plist-binary`, `plist-environment-keys`, `file-too-large`, `nonregular-file`, and `discovery-limit`.
- `test_schema_rejection_matrix`: parameterize every spec field/container rejection and exact message prefix/suffix, including unknown uid/receipt/cron fields, nulls, aliases, tags, duplicate keys, implicit coercion, Boolean integers and dates.
- `test_registry_defaults_and_metadata`: defaults match schema and paused/retired metadata never suppresses jobs.
- `test_discovery_order_frontmatter_and_limits`: stable recursive discovery, ignored non-frontmatter files, delimiter errors, no directory-symlink traversal, 1,000-file/1-MiB bounds and empty discovery error.
- `test_duplicate_projects_jobs_and_identities`: each uniqueness scope is enforced.
- `test_literal_paths_and_argv`: reject nonnormalized/relative/control-character paths; preserve spaces, empty argv elements and argv[0]; do not inspect executable/directory existence.
- `test_plist_join_errors`: missing/unreadable/invalid/no-Label/mismatched-Label plists produce the exact declared errors.
- `test_xml_binary_presence_and_environment_keys`: equivalent XML/binary observations preserve presence and redact all environment values.
- `test_declared_entrypoint_and_no_collection`: declared text/JSON and help work; invalid input exits 3; the package imports and runs with no launchctl code present.
- Proving command: `uv run python -m fleet_audit.acceptance registry --offline`; exact healthy line: `OK registry`.
- Done: all listed tests and proving command pass, valid nonempty declared exits 0, errors exit 3, package installs and console/module resolution is verified.

### Increment 1 CI step

Change `/Users/byron/repos/unattended/.github/workflows/ci.yml` as a separate small step within this PR. Existing globs miss the new package and may skip tests. Preserve repository lint and existing tests; add a Python 3.12 package step with explicit working directory, locked dependency synchronization, registry acceptance and `uv run --with pytest pytest -q`. Add the next proving command in each subsequent increment. Do not use absent-file conditions to silently skip implemented package tests.

## Increment 2: observer and replay

Branch `change/fleet-audit-2`.

- Add collect, launchctl_parse, overrides, snapshot, initial capture, observer/snapshot tests, service records, observer acceptance and verdicts containing the rule-1 coverage guard only. Extend file adapters and fixtures. Capture receipt-tail transport may be added now; receipt interpretation waits for increment 3.
- First test: `test_empty_inventory_exit_one_retains_every_job`. Replay the real blank `launchctl list` exit-1 record against a nonempty registry; every job remains present with cannot_determine and `rc=1` in its reason. No empty fleet or healthy result. `test_empty_inventory_without_jobs_reports_coverage_issue` covers absent discoverable rows.
- Freeze all five real original records: `com.unattended.tick.json`, `com.google.GoogleUpdater.wake.json`, `com.pdw.docker-restart.json`, `org.nixos.skhd.json`, `com.koekeishiya.yabai.json`.
- Freeze all twelve real audit rows: GoogleUpdater, both empty Keystone plists, Homebrew `com.koekeishiya.skhd` and `com.koekeishiya.yabai`, `com.management.tick`, `com.pdw.caffeinate`, `com.pdw.docker-restart`, `com.unattended.tick`, `homebrew.mxcl.ollama`, `org.nixos.skhd`, and `org.nixos.yabai`.
- Freeze original snapshot records: blank exit-1 list, domain inventory and disabled map, `com.apple.appleseed.seedusaged.postinstall`, `com.apple.talagent`, and `com.apple.networkserviceproxy`. Apple records are parser fixtures only.
- Freeze the real override text from `/Users/byron/repos/unattended/intent/fleet-audit/evidence/print-disabled-gui501-2026-10-16.txt`. Preserve all entries: it contains five disabled Apple labels, despite decision 10 saying four.
- Label synthetic variants `blank-success`, `wrong-domain`, `wrong-label`, `unrelated-113`, `truncated-service`, `duplicate-state`, `invalid-pid`, `never-exited`, `override-denied`, `override-incomplete`, `override-absent`, `timeout`, `combined-output-limit`, `snapshot-missing-entry`, and `snapshot-path-escape`.
- `test_real_service_fields_and_capture_separation`: preserve argv, calendars, exit 78/EX_CONFIG, exact absence, separate clocks and tick run counts 28 versus 29.
- `test_structural_and_identity_failures_are_unknown`: reject wrong roots, malformed nesting, contradictory duplicate fields and unrelated 113; nested coalition state never supplies root state.
- `test_missing_pid_and_exit_are_not_zero`: proven pid absence differs from parser failure; never-exited remains unknown history.
- `test_real_override_map_and_precedence`: full map, explicit enabled override, absent fallback, unknown failed map and disabled origin.
- `test_subprocess_bounds_and_reaping`: fake processes verify timeout, combined stream limit, spawn failure and cleanup without invoking launchctl.
- `test_snapshot_validation_and_failure_evidence`: missing/escaping members are invalid; recorded collection failures remain replayable evidence.
- `test_replay_forbids_live_commands_paths_and_clock`: injected traps fail any subprocess, original-path read or live-clock access.
- `test_capture_roundtrip_and_environment_redaction`: fake live adapters produce replayable archive bytes without environment values or filesystem writes.
- Proving command: `uv run python -m fleet_audit.acceptance observer --offline`; exact healthy line: `OK observer`.
- Done: registry still passes; every real observation is traceable; capture/replay isolation and the first coverage rule pass. No claim that full audit verdicts ship yet.

## Increment 3: verdicts and freshness

Branch `change/fleet-audit-3`.

- Add output, receipts, receipt/verdict tests; complete verdict table, audit CLI, report exit calculation, receipt capture/replay and verdict acceptance.
- Freeze real receipt lines from `/Users/byron/repos/unattended/state/ticks.jsonl`: first ran=true at `2026-10-15T08:38:30Z` with rc `"0"`; usage-limit skip at `2026-10-15T11:24:08Z`; ran=false/error=null at `2026-10-15T08:34:36Z`. Record source commit and line hashes when landing fixtures. These are real line contents, not evidence that they were the final line at either spike capture.
- Freeze synthetic scenarios `completed-no-result`, `failed-nonzero-rc`, `failed-ran-error`, `failed-not-ran-error`, `unestablished-null-rc`, `missing-supervisor`, `invalid-producer-fields`, `mtime-sufficient`, `mtime-insufficient`, `running-old-exit`, `running-ancillary-error`, `keepalive-no-exit`, `expected-disabled`, `unexpected-disabled`, `enabled-absent`, `loaded-disabled`, `contradictory-state`, `permission-denied`, `future-time`, `grace-window`, `stale-failed-receipt`, `malformed-tail`, `concurrent-tail`, and `age-boundaries`. Any scenario assigning metadata/times around real lines is labelled synthetic with a real-content source.
- `test_tick_completed_not_ran_null_error`, `test_tick_completed_skip`, `test_tick_completed_ran_zero`: one test per completed branch; include all three real lines and no-result synthetic case.
- `test_tick_failed_nonzero_rc`, `test_tick_failed_ran_error`, `test_tick_failed_not_ran_error`: one test per failed branch, including error empty-string behavior.
- `test_tick_unestablished_other_cases`: missing supervisor, null rc and invalid producer types cannot establish completion; Boolean rc rejected, integer/string zero accepted.
- `test_tail_final_physical_line_only`: remove exactly one newline, never fall back after a malformed/blank final line; partial preceding line is ignored.
- `test_tail_encoding_json_and_bounds`: UTF-8, duplicate keys, nonobject JSON, oversized line, exact 64-KiB boundary and nonregular-file errors.
- `test_tail_concurrent_append_truncate_replace`: before/after metadata changes yield uncertainty; no unbounded retries.
- `test_age_minus_one`, `test_age_at_m`, `test_age_at_m_plus_one`, `test_age_at_m_plus_g`, `test_age_at_m_plus_g_plus_one`: completed idle fixture yields cannot_determine, healthy_idle, cannot_determine, cannot_determine, late respectively for M=1200/G=1800.
- `test_fourteen_rule_order_and_first_match`: every rule wins in its intended case; historical failure does not override running, disabled precedes running, stale failed receipt is late, fresh failed receipt is failing.
- `test_unknown_never_matches_predicate`: every unknown/unsupported field and implicit-truth operation cannot satisfy a health predicate.
- `test_collection_error_never_healthy_idle`: parameterize global, service, override, parse and file errors.
- `test_receipt_timestamp_not_log_or_mtime`: fresh logs cannot hide a stale/missing receipt; old stdout cannot invalidate a fresh completed receipt.
- `test_audit_exit_precedence`: invalid input 3, definite finding 1, uncertainty 2, nonempty complete healthy fleet 0; expected/unexpected disabled and running ancillary uncertainty covered.
- Proving command: `uv run python -m fleet_audit.acceptance verdicts --offline`; exact healthy line: `OK verdicts`.
- Done: audit works live through bounded adapters and offline through fixtures; all 14 rules and producer branches pass; stat-only original tick records remain completion-unknown.

## Increment 4: three-way drift

Branch `change/fleet-audit-4`.

- Add drift and drift tests; extend loaded schedule parsing, comparison records, reports and drift acceptance.
- Reuse real tick `runatload`, nix skhd `keepalive`, PDW calendar and Apple talagent multi-calendar records. Freeze synthetic `drift-registry-disk`, `drift-registry-loaded`, `drift-disk-loaded`, `drift-missing-side`, `drift-absent-service`, `argv-boundaries`, `calendar-equivalent`, `calendar-wildcards`, `interval-and-calendar`, `policy-positive-tokens`, `policy-missing`, and `policy-unsupported`.
- `test_three_pairs_per_declared_field`: parameterize program, complete argv, working directory and each requested schedule component over all three comparison pairs; known unequal values emit correct findings.
- `test_unknown_is_incomplete_not_drift`: missing loaded evidence is unknown, absent service makes loaded pairs not_applicable, omitted expectations produce no comparisons.
- `test_program_fallback_and_exact_argv`: disk Program fallback, argv[0], empty/space-containing arguments and order remain exact; no shell splitting.
- `test_calendar_canonicalization`: map/alternative order and duplicates do not matter; Sunday 7 equals 0, omitted keys remain wildcards, interval/calendar coexist.
- `test_policy_presence_and_disk_defaults`: disk absent KeepAlive/RunAtLoad normalize false; missing loaded tokens remain unknown; supported positive property tokens prove true; unsupported dictionaries remain unsupported.
- `test_loaded_policy_never_inferred_from_disk`: drift never uses the rule-8 disk fallback.
- `test_drift_retained_with_running_and_exit_one`: higher-priority verdict remains running while independent drift forces exit 1.
- Proving command: `uv run python -m fleet_audit.acceptance drift --offline`; exact healthy line: `OK drift`.
- Done: all requested pairwise comparisons are explicit; incomplete comparisons block healthy_idle; unproven loaded policy stays unknown.

## Increment 5: scan, reports and lab adoption

Branch `change/fleet-audit-5`.

- Complete scan and text/JSON reports, report tests, fleet acceptance, capture scan mode and package README. Add `/Users/byron/repos/unattended/runbook/fleet/fleet.md` with the accepted lab declaration only (its own directory: supervisor decision 13; written by the supervisor before this increment).
- Lab paths: plist `/Users/byron/Library/LaunchAgents/com.unattended.tick.plist`; program `/bin/bash`; full argv `/bin/bash` then `/Users/byron/repos/unattended/bin/tick`; working directory `/Users/byron/repos/unattended`; receipt `/Users/byron/repos/unattended/state/ticks.jsonl`; domain `gui/501`, interval 600, max age 1200, grace 1800. Observe RunAtLoad without declaring it as an expectation.
- Reuse all twelve real audit rows and three real receipt contents. Freeze synthetic `scan-apple-filter`, `scan-no-label`, `scan-disabled`, `scan-loaded-disabled`, `scan-service-absent`, `scan-empty-coverage`, `report-escaping`, `report-mixed-exits`, `report-unattempted`, and `report-environment-redaction`.
- `test_scan_twelve_rows_and_both_nix_failures`: retain every non-Apple row, both exit-78 failures and both no-label rows; never infer filename labels.
- `test_scan_label_filter_and_unreadable_filename_fallback`: valid com.apple. labels excluded; unreadable/no-label files excluded only by exact com.apple. filename prefix.
- `test_scan_no_freshness_and_deduplicated_stats`: idle interval jobs say `no freshness contract declared`; stat only declared stdout/stderr once per path and never read their contents.
- `test_scan_running_old_ollama_log`: running with positive pid wins; reason ends `useful work not established`.
- `test_scan_disabled_loaded_disabled_and_absent`: disabled with unknown intent exits 2; loaded_disabled exits 1; enabled absent emits the decision-9 reason.
- `test_reports_schema_stability_and_provenance`: complete JSON envelope, explicit nulls, unattempted status, stable job ordering, preserved argv order, UTC timestamps, observation refs, summary counts and escaping.
- `test_reports_never_emit_environment_values`: keys survive; values are absent from text, JSON and snapshots.
- `test_cli_help_domains_and_validation_before_collection`: help exits 0, unknown flags/domain mismatch exit 3, invalid declarations/snapshots prevent collection.
- `test_empty_or_mixed_fleet_exit_precedence`: incomplete/empty coverage never exits 0; exercise precedence 3 > 1 > 2 > 0 across jobs and report issues.
- Proving command: `uv run python -m fleet_audit.acceptance fleet --offline`; exact healthy line: `OK fleet`.
- Done: all five proving commands, package pytest and repository lint pass. Supervisor captures actual live declared/audit/scan output and exit codes without a predetermined healthy count, reviews redaction, and publishes the first live report through the existing blog workflow. The implementation job does not edit `/Users/byron/repos/unattended/posts/`; the supervisor chooses the publication file.

## Verification, size and review

From `/Users/byron/repos/unattended/product/fleet_audit`, final CI must run each command separately: `uv run python -m fleet_audit.acceptance registry --offline`, `uv run python -m fleet_audit.acceptance observer --offline`, `uv run python -m fleet_audit.acceptance verdicts --offline`, `uv run python -m fleet_audit.acceptance drift --offline`, `uv run python -m fleet_audit.acceptance fleet --offline`, and `uv run --with pytest pytest -q`. Run `/Users/byron/repos/unattended/bin/lint` from the repository checkout. Healthy acceptance lines are exactly `OK registry`, `OK observer`, `OK verdicts`, `OK drift`, and `OK fleet`.

Acceptance assertions call production code without requiring pytest and fail nonzero on any mismatch or attempted live observation. CI may resolve/install dependencies; offline refers to the acceptance workload and evidence access. Each PR records actual verification stdout, not the expected output as if executed. Preserve repository tests and lint checks.

Estimated added hand-written lines, including tests: increment 1 900-1,200; increment 2 1,100-1,500; increment 3 900-1,300; increment 4 500-750; increment 5 600-900. Raw fixture bytes are additional and should not duplicate entire unrelated spike captures. PyYAML install footprint under uv: not measured. Increment 1 records installed PyYAML bytes and environment/cache disk deltas; stop build work below 1 GiB free.

Review follows `/Users/byron/repos/unattended/REVIEW.md`: bugs first, security second, spec/plan compliance third. A fresh-context reviewer supplies findings; the author cannot approve. Update this plan in the same commit if implementation departs.

## Risks and rejected alternatives

The riskiest step is structural launchctl parsing: diagnostic text is not a stable machine interface, and the spike's networkserviceproxy record already contains unsupported structure. Another macOS version may change root identities, absence diagnostics, property tokens, arguments or timers. Such changes must produce unknown fields, incomplete comparisons or cannot_determine with retained provenance, never false absence or healthy defaults. Cross-version support is not shown.

Rejected alternatives: copying the spike verdict function unchanged would retain superseded receipt and ordering behavior; inferring freshness from scan log ages would invent deadlines and misclassify idle/running jobs; using disk policy to fill missing loaded policy would hide drift rather than observe it.

- [ ] Increment 1: registry, plist join, package resolution and CI step verified.
- [ ] Increment 2: empty-inventory rule first, observer and isolated replay verified.
- [ ] Increment 3: ordered verdicts, receipt branches and age boundaries verified.
- [ ] Increment 4: three-way drift and unknown policy behavior verified.
- [ ] Increment 5: scan, complete reports, lab runbook and supervisor live report completed.
- [ ] Final five proving outputs, pytest output, lint output and measured footprint recorded.
## Supervisor acceptance

Interrogated 2026-10-16 against the questions set when the job was dispatched. Accepted without
changes; the answers are in the text above.

- Riskiest step: structural launchctl parsing (Risks section). Another macOS must degrade to
  unknown fields and cannot_determine, never false absence or a healthy default.
- Rejected alternatives: three are named (copying the spike verdict, scan freshness from log
  ages, disk policy filling missing loaded policy).
- Increment 1 contains no launchctl implementation or imports; it is buildable and testable on
  CI without launchd.
- Increment 2 opens with the empty-inventory test (blank exit-1 list against a nonempty
  registry keeps every job as cannot_determine).
- The five proving commands and healthy lines match the spec table verbatim.
- The receipt branches match decision 4 exactly (three completed, three failed, otherwise
  unestablished); the plan uses receipt ts, never mtime, for age.

Two lab notes on top of the plan. The spike worktree `.worktrees/spike-fleet-audit` is the
fixture source until day 3; the product's `fixtures/README.md` records the source commit
(18c8e8c) so the fixtures stand alone once the spike branch is gone. The CI edit in increment 1
is named in the build prompt because `AGENTS.md` forbids `.github/` edits otherwise.
