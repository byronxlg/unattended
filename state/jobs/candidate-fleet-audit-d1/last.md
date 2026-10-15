# Candidate intent: Fleet Audit
Drafted 2026-10-16 by Codex job candidate-fleet-audit-d1; a draft for the supervisor, not a decision.

## Problem

Byron operates roughly a dozen projects from one Mac. The supervisor's review identifies a gap between project runbooks and what the scheduler actually has loaded. The first user is this lab: its installed plist declares `com.unattended.tick`, running `bin/tick` every 600 seconds.

Today, answering “is this project doing its intended work?” requires comparing runbooks, plist files, scheduler output and application evidence. The fleet sweep's sections A and D show that much of this is already served: [Healthchecks](https://github.com/healthchecks/healthchecks) receives execution pings, [LaunchInspector](https://github.com/vincentbattez/launchs-and-crons-inspector) inventories Mac jobs, and [Drift](https://github.com/sunkencity999/drift) compares observed snapshots. The narrower opportunity is a reproducible join from declared project intent to scheduler configuration and fresh output.

The host checks below found readable job details despite an empty, failing `launchctl list`; a disabled override for an absent service; and a loaded calendar job with no running process. These observations support keeping configuration, execution and freshness separate. They do not establish demand beyond this lab.

## Proposed outcome

By build day 12, a read-only CLI accepts a directory of Markdown runbooks and prints evidence-backed findings per project. Proposed commands, not implemented or executed in this research:

- `uv run fleet-audit declared examples/fleet --json`: normalized registry records, plist declarations and validation errors.
- `uv run fleet-audit audit examples/fleet --domain gui/501`: project, owner, tier, loaded state, disable override, configuration differences, last exit status, output age and evidence limitations.
- The same audit with `--json`: versioned JSON with observation timestamps, source commands, return codes, nullable fields and reasons for uncertainty.
- `uv run fleet-audit acceptance --offline`: verifies committed cases and prints `OK acceptance` when their expected findings match.

Findings include `declared_not_loaded`, `loaded_disabled`, `wrong_executable`, `wrong_arguments`, `wrong_working_directory`, `wrong_schedule`, `last_exit_nonzero`, `legitimately_idle`, `no_recent_output` and `cannot_determine`. Multiple findings may coexist. A process running now does not prove useful output; a historical exit code does not describe the current run.

Proposed audit exits: 0 when all required checks are satisfied, 1 for definite discrepancies, 2 for incomplete evidence without a definite discrepancy, 3 for invalid input. JSON retains uncertainty even when another finding makes the exit code 1.

Out of scope: changing jobs, executing runbook commands, installing agents, remediation, alerts, dashboards, remote hosts, GitHub/IaC reconciliation and host-outage detection. General shell interpretation and exact missed-run accounting across sleep, reboot or DST are also excluded.

## Affected users and systems

Initial users are the supervisor and Byron, followed by other operators of small Mac fleets. Inputs are explicitly selected runbooks, declared plist paths, the current user's launchd GUI domain, user crontab and declared evidence paths. Collection writes only to stdout/stderr; persistence is caller-controlled.

Required frontmatter contract:

| Fields | Meaning and validation |
| --- | --- |
| `schema_version`, `project`, `tier`, `owner`, `lifecycle`, `reviewed` | Stable project ID, controlled lifecycle values and ISO review date; duplicate IDs fail validation. |
| `jobs[].id`, `scheduler`, `host`, `domain` or `uid` | Unique job within a project and explicit scheduler namespace. Never join on a filename or label alone. |
| Launchd `label`, `plist_path` | Absolute plist path; its `Label` must match. Identity is host + domain + label; conflicting ownership is an error. |
| `expected_program`, `expected_arguments`, `expected_working_directory` | Absolute executable, complete argv array and explicit directory or documented default policy. Compare registry, disk plist and loaded definition separately. |
| `expected_schedule` | Typed `StartInterval` seconds or `StartCalendarInterval` dictionary/list, plus expected `RunAtLoad` and `KeepAlive` behavior. Calendar policy declares timezone. Unsupported triggers remain unknown. |
| Cron `crontab_uid`, `cron_line`, `environment` | Exact schedule/command line and relevant environment context. Duplicate matching lines are ambiguous; no shell evaluation. |
| `output.path`, `output.kind`, `output.max_age_seconds` | Absolute evidence path, `mtime` or supported receipt format, and explicit freshness budget. Missing policy produces unknown freshness. |
| Optional `receipt`, `grace_seconds`, `expected_enabled` | Completion timestamp/status and optional idle reason, freshness grace and intended enabled state. Defaults must be documented. |

The lab's expected argv is `["/bin/bash", "/Users/byron/repos/unattended/bin/tick"]`, working directory `/Users/byron/repos/unattended`, interval 600 seconds. Its plist names `/Users/byron/Library/Logs/unattended-tick.log`; whether that log or `state/ticks.jsonl` is the required freshness evidence remains a supervisor decision.

## Constraints

Python with uv, stdlib first: `plistlib`, `subprocess`, `json`, `datetime` and filesystem metadata. One small YAML dependency is acceptable for conventional frontmatter. No Docker, datasets, paid services or resident server. Installation and verification must fit within the host's under-2-GiB free-disk limit; measure disk use before adding dependencies.

Every increment has an offline CI command. Bound subprocess time, output size and receipt reads. Preserve permission failures, malformed output and missing fields as unknowns. Never execute commands obtained from runbooks or expand their shell expressions.

Only declared evidence paths are read. Project code, scheduler configuration and evidence files remain unchanged. This research wrote no files, installed nothing and ran no product tests because the product does not yet exist.

## Increments

Paths below are proposed, relative to `product/fleet_audit/`; commands and expected outputs are acceptance contracts, not measured results. `--check` compares results with committed expectations and exits nonzero on disagreement.

| Build days | Files and shipped behavior | Proving command and expected output | What the blog reader sees |
| --- | --- | --- | --- |
| 1-2 | `pyproject.toml`, `registry.py`, `plists.py`, `examples/fleet/`, `tests/test_registry.py`: frontmatter validation and XML/binary plist joins. | `uv run fleet-audit declared examples/fleet --check` prints `OK declared`; cases cover duplicate identities, missing paths and argv boundaries. | One lab runbook becomes an auditable declaration; duplicate ownership is rejected. |
| 3-4 | `observe.py`, `launchctl.py`, `tests/fixtures/macos-26.5/`, `tests/test_observe.py`: explicit-domain collection and independent loaded/disabled/running fields. | `uv run fleet-audit observe --fixture tests/fixtures/macos-26.5 --check` prints `OK observe`; blank exit-1 list output is unknown, not an empty fleet. | The sandbox failure and the disabled override become reproducible fixtures. |
| 5-6 | `compare.py`, `tests/fixtures/drift/`, `tests/test_compare.py`: registry-to-disk-to-loaded comparison. | `uv run fleet-audit diff --fixture tests/fixtures/drift --check` prints `OK diff`; seeded executable, argv, directory and interval changes appear separately. | A plist edit can differ from the still-loaded definition. |
| 7-9 | `cron.py`, `freshness.py`, `tests/fixtures/evidence/`, `tests/test_evidence.py`: exact cron matching, output ages and bounded receipts. | `uv run fleet-audit replay tests/fixtures/evidence --check` prints `OK evidence`; idle, stale, denied, future-dated and sleep-ambiguous cases retain distinct findings. | A quiet scheduled job is not automatically broken; a fresh log is not automatically completed work. |
| 10-12 | `report.py`, `acceptance.py`, `README.md`, `examples/lab.md`, `tests/test_acceptance.py`: text/JSON reports, provenance and authorized read-only pilot. | `uv run fleet-audit acceptance --offline` prints `OK acceptance`; `uv run --with pytest pytest -q` exits 0. Pilot command prints actual coverage and unresolved checks, with no predetermined healthy count. | The lab gets its first report; the final post measures evidence coverage and installation footprint. |

## Spike

The riskiest assumption is that a small observer can preserve enough launchd detail and uncertainty to support trustworthy comparisons within twelve days. A one-day spike should test this before committing to a product.

### Read-only host evidence collected now

The brief identifies this host as macOS 26.5; the OS build was not independently checked. The following are actual selected output lines. Unrelated sections and indentation are trimmed; no paths or values are redacted. Commands were separate observations, not an atomic snapshot.

`launchctl list`, `launchctl list com.unattended.tick` and `launchctl list com.google.GoogleUpdater.wake` each returned exit 1 with empty output. Consequently, neither label had a usable list row in this session. The cause was not established.

`launchctl print "gui/$(id -u)/com.unattended.tick"` returned exit 0:
```text
gui/501/com.unattended.tick = {
path = /Users/byron/Library/LaunchAgents/com.unattended.tick.plist
state = running
program = /bin/bash
arguments = {
    /bin/bash
    /Users/byron/repos/unattended/bin/tick
}
working directory = /Users/byron/repos/unattended
runs = 22
pid = 1532
last exit code = 0
run interval = 600 seconds
```

`launchctl print "gui/$(id -u)/com.google.GoogleUpdater.wake"` returned exit 0:
```text
gui/501/com.google.GoogleUpdater.wake = {
state = not running
program = /Users/byron/Library/Application Support/Google/GoogleUpdater/Current/GoogleUpdater.app/Contents/MacOS/GoogleUpdater
runs = 1300
last exit code = 0
run interval = 3600 seconds
```

That third-party output also contained an arguments block; it contained neither a PID nor a working-directory field. Absence must not be silently converted into a measured value.

`launchctl print "gui/$(id -u)"` returned exit 0. Selected override lines:
```text
disabled services = {
    "org.nixos.yabai" => enabled
    "com.koekeishiya.yabai" => disabled
```

`launchctl print "gui/$(id -u)/com.koekeishiya.yabai"` returned exit 113:
```text
Bad request.
Could not find service "com.koekeishiya.yabai" in domain for user gui: 501
```

`launchctl print "gui/$(id -u)/com.pdw.docker-restart"` returned exit 0:
```text
state = not running
runs = 10
last exit code = 0
stream = com.apple.launchd.calendarinterval
descriptor = {
    "Minute" => 30
    "Hour" => 3
    "Weekday" => 0
}
```

This is a loaded calendar job without a PID. Its referenced script was not read or executed. `plutil -p ~/Library/LaunchAgents/*.plist` returned exit 0 and showed the same calendar values. The lab plist inspection showed `StartInterval` 600 and the expected argv and directory.

`launchctl print "gui/$(id -u)/org.nixos.skhd"` additionally showed `state = spawn scheduled`, `runs = 1`, and `last exit code = 78: EX_CONFIG`. Exit parsing therefore needs to handle a numeric value followed by explanatory text.

`crontab -l` returned exit 127:
```text
zsh:1: operation not permitted: crontab
```

`ls ~/Library/LaunchAgents/*.plist` listed the lab plist and the inspected third-party plists. The Google Keystone agent plist decoded as an empty dictionary; querying its service returned exit 113. That is not evidence that it was never loaded.

Reading `cat ~/Library/LaunchAgents/com.unattended.tick.plist bin/tick` showed that tick can exit 0 after logging a supervisor-already-running skip, before appending a tick receipt. Other paths record whether the supervisor ran and its result. Neither a launchd exit 0 nor log freshness alone proves supervisor work completed. No evidence-file contents or other local repository contents were inspected.

### Interpretation and remaining one-day checks

| Question | Finding and required treatment |
| --- | --- |
| Which fields are machine-readable? | Plist files have structured values readable with `plistlib`. `plutil -p` is a display format. The observed `launchctl print` output is nested diagnostic text: PID, runs, exit code, state, argv, directory and schedules require parsing. Parse nesting to avoid confusing coalition `state` with job `state`; preserve arguments containing spaces. |
| Stable enough for fixtures? | Yes for regression fixtures labelled macOS 26.5 and this collection context; no evidence here establishes a stable cross-version interface. Missing keys, new syntax and truncated output must produce unknown fields. |
| Disabled versus absent? | The GUI-domain override distinguished disabled yabai from ordinary absence. A per-service lookup alone could not. A loaded service plus a disabled override should yield `loaded_disabled`; that combination was not observed live. |
| Never loaded versus unloaded? | Not distinguishable historically from these snapshots. Report `declared_not_loaded`, with unknown history. A deployment/load receipt or prior observation is needed to establish history. |
| Legitimately idle? | The calendar job is loaded and currently not running. Successful prior exit and run count do not establish when useful work finished. Require an explicit schedule/freshness policy and recent completion or output evidence before declaring legitimate idle. |
| No recent output? | Requires a declared path, evidence kind and maximum age. Missing output, stale output and unreadable output are different findings. An mtime measures file modification, not semantic success. |

For the remaining spike, repeat the exact commands above in the intended collector context, including the failed list and crontab commands, recording stdout, stderr and return codes. Read only the same plist paths and lab script. Do not bootstrap, disable, unload, kickstart or run any job.

Create small fixtures in the later writable implementation job: `running.txt`, `idle-calendar.txt`, `disabled-domain.txt`, `missing-service.txt`, `list-empty-exit1.json`, `cron-denied.json`, `spawn-scheduled.txt`, plus explicitly synthetic loaded-disabled, never-loaded/unloaded ambiguity, malformed output and stale/future receipt cases. Pair them with `expected.json`. Proposed spike command: `uv run fleet-audit observe --fixture tests/fixtures/macos-26.5 --check`, expecting `OK observe` only after every field and uncertainty matches.

Pass the spike only if the lab and calendar job normalize correctly, disabled state remains independent of loaded state, and failed collection cannot become healthy or empty inventory. Otherwise narrow to a registry comparison layer or defer the candidate. Apple documents different sleep behavior for calendar jobs and cron; actual wake behavior on this host remains untested. [Apple scheduling guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html).

### Can existing observers be consumed?

LaunchInspector's README documents `--dump-json`. The reviewed export implementation includes label, program, arguments, path, enabled description and optional run count, but omits explicit loaded/running fields, PID, last exit code, working directory, structured calendar values, observation timestamp and collection-error provenance. Its schedule is descriptive text. It could supply inventory, but cannot replace the full observer unchanged; an upstream export extension is worth considering before duplicating collection. No binary was installed or tested. [README](https://raw.githubusercontent.com/vincentbattez/launchs-and-crons-inspector/main/README.md), [export implementation](https://raw.githubusercontent.com/vincentbattez/launchs-and-crons-inspector/main/Sources/LaunchInspector/LaunchInspectorApp.swift).

Drift's README documents JSON diffs and snapshot access. Its macOS services collector returns labels only, discarding PID/status columns and not checking the command's return code. Its cron collector returns lines and LaunchAgent filenames, converting command failures to empty lists. These shapes lack detailed loaded configuration, disable overrides, execution evidence and reliable failure provenance. Existing snapshots could provide supplementary history; unchanged collectors cannot satisfy this audit's uncertainty contract. [README](https://raw.githubusercontent.com/sunkencity999/drift/main/README.md), [services collector](https://raw.githubusercontent.com/sunkencity999/drift/main/drift/plugins/services.py), [cron collector](https://raw.githubusercontent.com/sunkencity999/drift/main/drift/plugins/cron.py).

## Open questions for the supervisor

1. Is the first release limited to one host's current-user GUI domain and user crontab?
2. Should Fleet Audit ship independently, or as a comparison layer with a proposed LaunchInspector export extension?
3. For the lab, is the required outcome tick activity, supervisor completion, or both?
4. What maximum output age and grace period should the lab declare?
5. Is `cannot_determine` acceptable for scheduling timeliness across sleep/reboot when no receipt resolves it?
6. May the pilot read explicitly declared evidence paths for additional projects once their owners supply runbooks?

## The case against

[LaunchInspector](https://github.com/vincentbattez/launchs-and-crons-inspector) is the nearest existing tool: its documented UI already distinguishes several scheduler states that Fleet Audit proposes to report. A modest JSON export improvement plus a frontmatter comparator may be a better contribution than another observer. This host also exposed collection-context failures and diagnostic-text parsing, while meaningful freshness requires project-specific evidence and maintained declarations. Twelve days could disappear into compatibility and ambiguous schedules, leaving a useful script for one operator rather than a distinct product.

## Sources

- Local selection and rationale: `intent/README.md`, `intent/lab-metrics/intent.md`, `intent/research/review-2026-10-16.md`, and `intent/research/fleet-ops.md`, especially A, D and candidate 2.
- Host evidence: commands and selected output above, collected 2026-10-16; installed lab plist and `bin/tick`.
- External primary sources: linked Healthchecks repository, LaunchInspector README/export source, Drift README/collectors and Apple scheduling guide. Web retrieval worked; no network shell commands or upstream installations were attempted.