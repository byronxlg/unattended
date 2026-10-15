<!-- Spec job: spec-fleet-audit (read-only, thread 01a13fd3-22f7-73d2-b1de-9d20dfbd2120), copied verbatim from state/jobs/spec-fleet-audit/last.md -->
<!-- Reviewed and accepted by the supervisor on 2026-10-16 (day 1); decisions at the end override the body where they differ -->

# Fleet Audit specification

## Status and scope

Design for supervisor review, governed by `intent/fleet-audit/intent.md`. Resolve the numbered concerns before build. The candidate draft supplies structure, not additional scope.

Build a read-only Python 3.12 CLI in `product/fleet_audit/`, using stdlib plus PyYAML. Audit one local host and its current user's `gui/<uid>` domain. Never execute job commands, mutate jobs, inspect cron, or read undeclared application files. Writes are stdout and stderr only.

The lab is the only initial runbook declaration. Other jobs remain scan observations until their owners supply runbooks. Process presence establishes running, not useful work. Cross-version launchctl compatibility, continuous failure, and exact missed executions across sleep or reboot are not shown.

## Runbook schema version 1

Discover `*.md` recursively in the supplied directory, sorted by relative path, without following directory symlinks. Ignore Markdown without frontmatter; validate every frontmatter-bearing file. Require opening and closing `---` delimiters and a mapping.

Reject duplicate YAML keys, aliases, custom tags, unknown fields, explicit nulls, and implicit type coercion. Booleans do not count as integers. Dates must be quoted strings. Errors have `{file, field, code, message}`; messages begin `<file>:<field>: `. Table messages below are literal suffixes with placeholders substituted.

Required fields have no default. Optional omission means the stated default, not an observed value.

| Field | Type; required/default | Validation error |
| --- | --- | --- |
| `schema_version` | Integer; required; exactly 1 | `expected schema_version 1` |
| `project` | String; required; `[a-z0-9][a-z0-9_-]*` | `expected project slug`; `duplicate project {value}` |
| `owner` | Nonblank string; required | `expected nonblank owner` |
| `tier` | String; optional, `standard`; `critical`, `standard`, `experimental` | `expected critical, standard, or experimental` |
| `lifecycle` | String; optional, `active`; `active`, `paused`, `retired` | `expected active, paused, or retired` |
| `reviewed` | Quoted ISO `YYYY-MM-DD` calendar date; required | `expected valid YYYY-MM-DD string` |
| `jobs` | Nonempty list of mappings; required | `expected nonempty job list` |
| `jobs[].id` | Slug as for project; required; unique within project | `expected job slug`; `duplicate job id {value}` |
| `jobs[].scheduler` | String; optional, `launchd`; only `launchd` | `only launchd is supported` |
| `jobs[].host` | String; optional, `local`; only `local` | `only local host is supported` |
| `jobs[].domain` | String; optional, current `gui/<uid>` | `expected current-user gui/{uid}` |
| `jobs[].label` | Nonempty string without whitespace, slash, or control characters; required | `expected launchd label`; `duplicate identity {host}/{domain}/{label}` |
| `jobs[].plist_path` | Absolute normalized path; required | `expected absolute normalized path`; `plist missing`; `plist unreadable: {error}`; `invalid plist: {error}`; `plist Label missing`; `plist Label {actual} differs from {expected}` |
| `jobs[].expected_program` | Absolute normalized executable path; required | `expected absolute normalized path` |
| `jobs[].expected_arguments` | Nonempty string array, complete argv including argv[0]; required | `expected nonempty argv array`; `argv contains control character` |
| `jobs[].expected_working_directory` | Absolute normalized path; optional, no expectation | `expected absolute normalized path` |
| `jobs[].expected_schedule` | Mapping described below; optional, no expectation | `expected schedule mapping` |
| `jobs[].expected_enabled` | Boolean; optional, true | `expected boolean` |
| `jobs[].output` | Evidence mapping below; optional, no freshness contract | `expected evidence mapping` |
| `jobs[].grace_seconds` | Integer >= 0; optional, 0; requires output when supplied | `expected nonnegative integer`; `grace_seconds requires output` |
| `output.path` | Absolute normalized path; required within output | `expected absolute normalized path` |
| `output.kind` | String `mtime` or `ticks_jsonl`; required within output | `expected mtime or ticks_jsonl` |
| `output.max_age_seconds` | Integer > 0; required within output | `expected positive integer` |
| `output.mtime_sufficient` | Boolean; optional, false; true permitted only for mtime | `expected boolean`; `mtime_sufficient requires kind mtime` |
| `expected_schedule.interval_seconds` | Integer > 0; optional, no interval expectation | `expected positive integer` |
| `expected_schedule.calendar` | Nonempty calendar mapping or nonempty list thereof; optional | `expected calendar mapping or nonempty list` |
| `expected_schedule.timezone` | String; required with calendar; only `local` | `calendar requires timezone local`; `timezone requires calendar` |
| `expected_schedule.keep_alive` | Boolean; optional, no expectation | `expected boolean` |
| `expected_schedule.run_at_load` | Boolean; optional, no expectation | `expected boolean` |

A schedule must contain at least one of interval, calendar, keep_alive, or run_at_load: otherwise `expected at least one schedule expectation`. Interval and calendar may coexist. Calendar keys are exactly `Minute` 0..59, `Hour` 0..23, `Day` 1..31, `Weekday` 0..7, `Month` 1..12, all integers; omitted keys are wildcards. Errors: `unknown calendar field {key}`, `expected {key} integer in {min}..{max}`, or `calendar mapping must not be empty`.

At any level: missing required field gives `required field missing`; unknown field gives `unknown field`; wrong container type gives `expected mapping` or `expected list`. Malformed YAML, duplicate keys, aliases, tags, and missing delimiter give `invalid frontmatter: {detail}`. Empty discovery gives `no declared jobs`. Reject `uid`, `receipt`, and cron fields as unknown: domain has one representation and output names either evidence kind.

Paths are literal, with no tilde or environment expansion, NUL, control characters, `.` or `..` components. Do not check executable or working-directory existence by opening them. Metadata such as tier, lifecycle, and review date does not suppress auditing. Identity is `(local, domain, label)`, never a filename. Duplicate identities are errors even within one project.

Worked `runbook/fleet.md` frontmatter, followed by ordinary Markdown prose:

```yaml
---
schema_version: 1
project: unattended
owner: Byron
tier: standard
lifecycle: active
reviewed: "2026-10-16"
jobs:
  - id: tick
    scheduler: launchd
    host: local
    domain: gui/501
    label: com.unattended.tick
    plist_path: /Users/byron/Library/LaunchAgents/com.unattended.tick.plist
    expected_program: /bin/bash
    expected_arguments: [/bin/bash, /Users/byron/repos/unattended/bin/tick]
    expected_working_directory: /Users/byron/repos/unattended
    expected_schedule:
      interval_seconds: 600
    expected_enabled: true
    output:
      path: /Users/byron/repos/unattended/state/ticks.jsonl
      kind: ticks_jsonl
      max_age_seconds: 1200
    grace_seconds: 1800
---
```

## Evidence record and collection

Each job record contains identity, project metadata or null for scan, registry expectations or null, plist observation, service observation, override observation, output observations, receipt observation, derived loaded/disabled values, comparison results, verdict, reason, and uncertainties.

Every observation has `observed_at` as UTC RFC3339, `source_command` as an argv array, `return_code`, `error` as null or `{code,message}`, and `data`. File operations use descriptive arrays such as `["stat", path]`, `["plistlib.load", path]`, and `["read_tail", path, "65536"]`; these are provenance, not shell commands. Their return code is null because no process ran. Subprocess codes are integers, or null if spawning failed or timed out. Unattempted observations retain null data/time/code and an explicit `not_requested` or `not_applicable` status.

| Observation | Data and absence semantics |
| --- | --- |
| Registry | Runbook path and normalized schema fields. Omitted optional expectations mean no comparison, never equality. |
| Plist | Preserve presence and typed values of Label, Program, ProgramArguments, WorkingDirectory, StartInterval, StartCalendarInterval, KeepAlive, RunAtLoad, Disabled, StandardOutPath, StandardErrorPath. Missing keys remain absent; invalid values carry field errors. |
| Service | Explicit domain/label; loaded; state; positive pid; nonnegative runs; signed last_exit_code; last_exit_text; program; argv; working_directory; plist_path; typed schedule components; properties; parse warnings. Missing fields are null with a missing-field list. |
| Override | Entire parsed override map provenance plus this label's `enabled`, `disabled`, `absent`, or `unknown` entry. Successful complete map with no entry means absent, not collection failure. |
| Output | Path, existence, size, mtime, observation-relative age, stat error. Audit observes only `output.path`; scan may stat plist-declared stdout/stderr paths, deduplicated, without reading contents. |
| Receipt | Path, bounded-read metadata, size/mtime before and after, parsed last object, receipt timestamp, age, normalized outcome, and parsing/read errors. No receipt contract means unattempted, not failed. |

Use `launchctl print gui/<uid>`, per-service `launchctl print gui/<uid>/<label>`, and `launchctl print-disabled gui/<uid>`. Domain enumeration corroborates coverage; it does not replace service lookups. Production does not need `launchctl list`.

A successful structurally valid service response establishes loaded=true. Only exit 113 with the exact requested label and domain in the recognized service-not-found diagnostic establishes loaded=false; this is an expected absence observation, not a collection error. Other nonzero exits, blank successful responses, truncation, malformed nesting, or identity mismatch establish unknown.

A missing pid in an intact service block means no reported pid, not pid zero. Missing last exit means history unknown, including “never exited”; it is not exit zero. A missing loaded directory or schedule component is unknown, not a launchd default. Nested coalition state never supplies job state.

Effective disabled is the explicit override when present; otherwise the disk Disabled boolean, default false for a valid plist. A failed override collection makes effective disabled unknown. Preserve its origin.

Bound each subprocess to 10 seconds and 4 MiB combined stdout/stderr; terminate on either limit and retain an error. Bound each runbook/plist read to 1 MiB, discovery to 1,000 files, and receipt reads to the final 64 KiB. Limit violations are explicit errors, never truncated success. Reject nonregular evidence files. Do not follow application paths found inside receipt contents.

Collection is sequential, not atomic. Global command errors are attached to every affected job. An empty or failed launchctl inventory never yields an empty fleet: retain discovered declarations/plists and their uncertainty; if none can be enumerated, emit a report-level cannot_determine coverage issue. Replayed `launchctl list` exit 1 with empty streams makes every affected job cannot_determine and includes `rc=1`.

## Receipt and freshness semantics

For `ticks_jsonl`, read only the final bounded region. Remove one terminal newline, then parse the final physical line; do not search backward for an older valid result. A partial first line in the region is ignored only when it is not the final line. An oversized final line, blank final line, malformed UTF-8/JSON, duplicate JSON keys, or non-object value is a receipt error. Detect concurrent modification from before/after metadata and return uncertainty without retrying indefinitely.

The lab producer stores `ts` and `supervisor.{ran,rc,error,result}`. Its `result` is nested free text, not a documented success enum. Require timezone-aware `ts`, boolean ran, null or integer/decimal-string rc, null/string error, and null/string result. Other receipt fields are ignored. No real receipt content was captured by the spike.

Normalize outcomes conservatively: `completed` requires ran=true, rc=0, empty/null error, and nonblank result; `failed` requires ran=true and nonzero rc; everything else is `unestablished`. Free-text result alone cannot establish success. A no-work or usage-limit skip does not establish completed supervisor work. This interpretation needs concern 4 resolved before build.

Receipt age uses `ts`; mtime evidence age uses mtime, both against the respective observation time. Never substitute log freshness for a receipt. A future timestamp is cannot_determine, without clock-skew tolerance.

Let A be age, M=max_age_seconds, G=grace_seconds. A<=M is fresh; M<A<=M+G is within grace; A>M+G is late. Equality at either boundary is not late. Within grace is not healthy_idle: report cannot_determine unless another higher-priority verdict applies. This preserves suspicion at M and the execution allowance G as distinct concepts.

## Verdict decision order

Evaluate the first matching rule below. Predicates use only trusted fields; unknown values never satisfy a predicate. Drift is computed independently and retained alongside the single verdict. `idle` means loaded=true, state=`not running`, and no reported pid.

| Order | Exact predicate and verdict | Reason template |
| --- | --- | --- |
| 1 | Global collection failure, unusable identity, unknown loaded state, or structurally invalid service response: cannot_determine | `cannot establish {field}: {source} rc={rc}: {error}` |
| 2 | Effective disabled unknown: cannot_determine | `disabled state unknown: {source} rc={rc}: {error}` |
| 3 | loaded=true and disabled=true: loaded_disabled | `service loaded but disabled by {origin}; lookup rc=0` |
| 4 | loaded=false and disabled=true: disabled | `service absent, disabled by {origin}; expected_enabled={value}; lookup rc=113` |
| 5 | loaded=false and disabled=false: declared_not_loaded for audit; cannot_determine for scan | `service absent; lookup rc=113; load history unknown` |
| 6 | loaded=true, state=running, positive pid: running | `state running, pid={pid}; useful work not established` |
| 7 | loaded=true, no reported pid, state not running or spawn scheduled, nonzero last exit: failing | `state={state}, no pid; last exit={code} {text}` |
| 8 | loaded=true, no reported pid, state=spawn scheduled, KeepAlive=true from loaded properties or disk when loaded policy unavailable: failing | `KeepAlive=true ({origin}), spawn scheduled, no pid; last exit={code_or_unknown}` |
| 9 | Any remaining collection/parse/file error, contradictory pid/state, missing required comparison evidence, or drift: cannot_determine | `health unestablished: {ordered_details}` |
| 10 | No output contract, unavailable/invalid/future evidence timestamp, or unresolved timing ambiguity: cannot_determine | `freshness unestablished: {detail}` |
| 11 | loaded=true and A>M+G: late | `{kind} {path} age={A}s exceeds max_age={M}s + grace={G}s; missed execution not established` |
| 12 | idle, ticks_jsonl outcome=failed, A<=M+G: failing | `receipt {path} ts={ts} supervisor rc={rc}; result={result_state}` |
| 13 | idle, last exit=0, A<=M, and either ticks_jsonl outcome=completed or mtime_sufficient=true: healthy_idle | `not running, last exit=0; {path} age={A}s <= max_age={M}s; evidence={completed_result_or_explicit_mtime}` |
| 14 | Otherwise: cannot_determine | `health unestablished: {within_grace_or_missing_completion_or_missing_exit_or_state}` |

Rules 6 through 8 can retain ancillary observation errors as uncertainties; no collection error anywhere in a job permits healthy_idle. Historical failure does not override a currently running pid. Running never promises completion, even with a contract. A stale failed receipt yields late, retaining its failure in evidence. Disabled-as-expected is a classification of disabled, not a ninth verdict.

## Drift comparison

For audit, compare each declared expectation across registry-to-disk, registry-to-loaded, and disk-to-loaded. Emit findings only for known unequal values; unknown sides produce incomplete comparison records and uncertainties. An absent service makes loaded comparisons not applicable.

Each comparison contains field, pair, left/right values, status `equal|different|unknown|not_applicable`, and observation references. Findings use `wrong_program`, `wrong_arguments`, `wrong_working_directory`, or `wrong_schedule`; reason: `{field}: {left_source}={left_value} differs from {right_source}={right_value}`.

Program on disk is Program when present, otherwise ProgramArguments[0]. Do not invent missing argv from Program. Compare argv element-for-element, preserving spaces, empty arguments, order, and argv[0]; never shell-split or expand. Paths compare literal normalized strings without realpath resolution.

Schedule comparison is typed and component-wise: integer interval, calendar alternatives, boolean KeepAlive and RunAtLoad. Calendar map key order and alternative order are immaterial; deduplicate identical alternatives and normalize Sunday 7 to 0. Omitted calendar keys remain wildcards. Compare only requested components, retaining all observed components in evidence. `timezone: local` describes host wall-clock interpretation, not a loaded timezone field.

Disk omissions of KeepAlive and RunAtLoad normalize to false; disk omitted interval/calendar means absent. Missing loaded timer/policy fields remain unknown unless a complete supported representation proves the value. Unsupported KeepAlive dictionaries and event triggers are retained as unsupported evidence, never coerced to booleans. The spike did not independently normalize loaded KeepAlive/RunAtLoad drift; fixtures must prove that extension.

## CLI and report contract

Commands are `uv run fleet-audit declared <dir> [--json]`, `uv run fleet-audit audit <dir> [--domain gui/<uid>] [--fixture <snapshot>] [--json]`, and `uv run fleet-audit scan [--domain gui/<uid>] [--fixture <snapshot>] [--json]`. Standard `--help` exits 0. Unknown flags or mismatched domains exit 3; CLI domain validates declarations, never silently retargets them.

Scan enumerates non-Apple user LaunchAgent plists only. Exclude valid labels beginning `com.apple.`; for unreadable/no-label plists exclude only filenames beginning `com.apple.`. Preserve no-label rows by plist path without inventing labels or service lookups. Scan invents no freshness budget and emits running, failing, disabled, or cannot_determine. A loaded-disabled scan record uses cannot_determine with an explicit contradiction reason and a definite-finding classification.

Text emits one stable, escaped line per job: `{project_or_scan}/{id_or_plist} {domain}/{label_or_no_label} {verdict}: {reason}`, followed by drift/uncertainty details and a summary. Declared text uses `declared` in place of verdict and describes the joined plist. Unknown values print `unknown`, never zero.

JSON emits one document: `{schema_version, command, domain, observed_at, jobs, issues, summary, exit_code}`. Jobs contain the complete evidence model above; timestamps are UTC strings, absent values are explicit nulls, arrays are stable-sorted, and summary counts verdicts, drift findings, uncertainties, and invalid-input errors. Each verdict also contains `evidence_refs` linking to its observation provenance. No raw environment values are included.

Illustrative one-job JSON for an invalid scan plist, with unattempted observations omitted from this example only:

```json
{
  "schema_version": 1,
  "command": "scan",
  "domain": "gui/501",
  "observed_at": "2026-10-15T13:37:56Z",
  "jobs": [{
    "identity": {"host": "local", "domain": "gui/501", "label": null},
    "project": null,
    "registry": null,
    "plist_path": "/Users/byron/Library/LaunchAgents/com.google.keystone.agent.plist",
    "observations": {
      "plist": {
        "observed_at": "2026-10-15T13:37:56Z",
        "source_command": ["plistlib.load", "/Users/byron/Library/LaunchAgents/com.google.keystone.agent.plist"],
        "return_code": null, "error": null, "data": {}
      }
    },
    "loaded": null, "disabled": null, "comparisons": [], "drift": [],
    "verdict": "cannot_determine",
    "reason": "cannot establish identity: plist Label missing; filename is not identity",
    "evidence_refs": ["plist"],
    "uncertainties": ["plist Label missing"]
  }],
  "issues": [],
  "summary": {"jobs": 1, "verdicts": {"cannot_determine": 1}, "drift_findings": 0, "uncertainties": 1, "invalid_input_errors": 0},
  "exit_code": 2
}
```

Exit precedence is 3, then 1, then 2, then 0. Exit 3 means invalid CLI/runbook/plist join or invalid snapshot input; collect no live service evidence after validation fails. Exit 1 means any failing, late, declared_not_loaded, loaded_disabled, drift, or unexpected disabled finding. Exit 2 means unresolved uncertainty exists and no definite finding exists, including incomplete coverage or ancillary errors on running jobs. Exit 0 requires nonempty complete coverage and only running, healthy_idle, or expected-disabled jobs, with no drift or uncertainty. Scan disabled has expectation unknown and therefore exits 2 unless another definite finding forces 1. Declared exits 0 for a valid nonempty registry, otherwise 3.

## Offline replay and verification

A snapshot directory contains `manifest.json` with format version 1, capture clock, domain, macOS label, and indexed logical paths; `runbooks/`; XML/binary `plists/`; `commands/` with argv, observation times, return codes, bounded stdout/stderr and errors; `stats.json`; `receipts/` containing bounded tail bytes and boundary/metadata information; and `expected.json` for acceptance assertions. All manifest references remain inside the snapshot. Original absolute paths are lookup keys, never opened during replay.

Replay uses frozen observation times, re-runs parsing and verdict logic, and performs no live commands or original-path reads. Missing manifest entries are invalid input; explicitly recorded ENOENT, denied reads, timeouts, and malformed command output are valid evidence of failure. Original spike stat-only tick records remain completion-unknown; synthetic receipt contents must be labelled synthetic.

Freeze the five original fixtures: `com.unattended.tick.json`, `com.google.GoogleUpdater.wake.json`, `com.pdw.docker-restart.json`, `org.nixos.skhd.json`, and `com.koekeishiya.yabai.json`. Also preserve all twelve rows from `audit.json`, including management, caffeinate, Homebrew skhd, Ollama, nix yabai, and both empty Keystone plists. Preserve separate timestamps/run counts rather than merging captures.

From `snapshot.json`, retain the blank exit-1 list record, domain disabled map, `com.apple.appleseed.seedusaged.postinstall` loaded-disabled record, `com.apple.talagent` multi-calendar record, and `com.apple.networkserviceproxy` structural failure. Apple records are parser fixtures, not scan targets. A real `print-disabled` command fixture and real receipt-content fixture are not shown; use labelled synthetic fixtures until supervisor collection supplies them.

Synthetic tests cover every verdict: running with historical nonzero exit and ancillary errors; completed receipt and explicit mtime healthy_idle; late at M+G+1; nonzero exit, KeepAlive spawn loop, and failed receipt failing; expected/unexpected disabled; enabled exact-113 absence; loaded-disabled; and missing-policy, permission, future-time, malformed-receipt, missing-result, skip, grace-window, and contradictory-state uncertainty.

Also test A=-1, M, M+1, M+G, M+G+1; collection errors blocking healthy_idle; empty inventory never becoming empty success; exact argv boundaries; three pairwise drift combinations per field; missing versus unequal fields; duplicate identities; every schema rejection; XML/binary plists; bounded/truncated reads; concurrent receipt changes; and mixed exit-code precedence. Fixture replay must fail if it attempts live collection.

Acceptance commands below are proposed, not executed results. Run from `product/fleet_audit/`; each uses a package acceptance module, exits nonzero on mismatch, and prints the healthy line only after all assertions pass.

| Increment | Proving command | Expected healthy line |
| --- | --- | --- |
| 1: Registry and plist join | `uv run python -m fleet_audit.acceptance registry --offline` | `OK registry` |
| 2: Observer and replay | `uv run python -m fleet_audit.acceptance observer --offline` | `OK observer` |
| 3: Verdicts and freshness | `uv run python -m fleet_audit.acceptance verdicts --offline` | `OK verdicts` |
| 4: Three-way drift | `uv run python -m fleet_audit.acceptance drift --offline` | `OK drift` |
| 5: Scan and reports | `uv run python -m fleet_audit.acceptance fleet --offline` | `OK fleet` |

Final verification also runs `uv run --with pytest pytest -q` and repository `bin/lint`. Measure installation footprint; stop build work below 1 GiB free. Supervisor live verification records actual results without a predetermined healthy count. No implementation, live launchctl execution, or product-test execution occurred during this design.

## Concerns requiring supervisor answers

1. **Should scan invent freshness for interval jobs with StandardOutPath?** Recommend no. A path and timer establish neither successful completion nor a deadline; retain cannot_determine for idle jobs without contracts.
2. **How should a plist without Label be treated?** Recommend declared validation error, but a retained cannot_determine scan row identified by path. Never infer a service label from its filename.
3. **Should Ollama's week-old log override its running pid?** Recommend running with “useful work not established.” Without a freshness contract, old logs do not establish failure; the spike shows process presence only.
4. **What exactly makes the lab receipt successful?** The producer's nested `supervisor.result` is arbitrary text, not a success flag. Recommend the conservative completed predicate specified above, requiring result presence plus rc=0, and treating skips as unestablished. Semantic supervisor success beyond those fields is not shown.
5. **Are the 1200-second maximum age and 1800-second grace acceptable despite 2700-second supervisor runs?** Keep the accepted values and report the grace window as uncertainty; running takes precedence. Revisit the contract if live examples expose false late findings. Do not silently enlarge either field.
6. **Are expected-disabled and scan-disabled exit semantics acceptable?** Recommend only explicit expected_enabled=false qualifies for exit 0; unknown scan intent produces exit 2, unexpected disablement exit 1.
7. **May loaded policy drift remain unknown where launchctl does not expose a proven representation?** Recommend yes. Freeze supported property forms and report unknown otherwise, rather than inferring loaded KeepAlive/RunAtLoad from disk.
8. **Are the proposed metadata enums and strict absolute-path schema acceptable?** Recommend adopt them for version 1; future schema changes require a version change rather than silent coercion.
## Supervisor decisions

Reviewed 2026-10-16 against intent/fleet-audit/intent.md. The spec is accepted with the
decisions below; where a decision differs from the body above, the decision wins and the plan
(phase 3) and the build follow the decision.

1. **Scan freshness for interval jobs with StandardOutPath: no.** As recommended and as the
   intent leans. Scan emits no freshness verdicts; an idle interval job without a runbook is
   cannot_determine with reason `no freshness contract declared`.
2. **Plist without Label.** As recommended: a validation error in `declared` and `audit` (exit
   3, `plist Label missing`); in `scan` a retained cannot_determine row identified by plist
   path. The filename is never a label. The two Keystone plists on the host are the fixtures.
3. **Running pid with an old log (Ollama): running.** As recommended. Reason ends `useful work
   not established`. Without a contract, log age is not evidence of failure.
4. **What makes the lab receipt completed. Decision differs from the recommendation.** The
   launchd job declared in runbook/fleet.md is `bin/tick`, not the supervisor. Every tick run
   appends one line to state/ticks.jsonl, whether or not it started a supervisor; a line with
   `supervisor.ran: false` is a tick that ran to completion and decided not to start one. On
   2026-10-16 the file had 31 lines: 6 with `ran: true`, 25 with `ran: false` (reasons empty,
   usage-limit marker, or next-run-after). Under the body's predicate the lab's own job would be
   cannot_determine almost always, which is the false-alarm shape spike 2 warned about.
   The producer contract for `kind: ticks_jsonl`, version 1, is therefore:
   - the final line is a JSON object with a timezone-aware RFC3339 `ts` and a `supervisor`
     mapping with boolean `ran`; `rc` is null, an integer, or a decimal string (the real
     producer writes `"0"`); `error` and `result` are null or strings; other keys are ignored;
   - `completed`: `ran: false` and `error` null or beginning `skipped:`; or `ran: true`,
     `rc` equal to 0 after decimal parsing, and `error` null. `result` free text is not
     required and is never interpreted;
   - `failed`: `ran: true` and (`rc` nonzero or `error` non-null); or `ran: false` and `error`
     non-null not beginning `skipped:`;
   - anything else, including a missing `supervisor` mapping, is `unestablished`.
   Rule 12 and rule 13 use these outcomes unchanged. Real fixtures: take the first `ran: true`
   line, one `skipped: usage limit` line and one `ran: false, error: null` line from
   state/ticks.jsonl at the commit that lands the fixtures; label them real, not synthetic.
   Supervisor success beyond the tick's own exit is out of scope for this verdict; a later
   receipt kind can add it.
5. **1200 s max age and 1800 s grace: keep.** As recommended, with the mechanism stated: the
   tick is the launchd process and the supervisor is its child, so during a 45 minute run
   launchd reports com.unattended.tick running with a pid, and rule 6 fires before rule 11. The
   receipt line is appended after the supervisor exits, so the age resets at the end of the run.
   Within grace (1200 < A <= 3000) idle is cannot_determine, which is the intended suspicion.
   Revisit only on a live false late finding, recorded in an eval under evals/.
6. **Disabled exit semantics: accepted.** Only explicit `expected_enabled: false` qualifies
   for exit 0; scan disabled exits 2; unexpected disablement exits 1.
7. **Loaded policy drift may stay unknown: accepted.** Supported property forms are frozen in
   the parser; anything else is unknown with the raw form retained. Never infer loaded
   KeepAlive or RunAtLoad from disk.
8. **Metadata enums and strict absolute paths: accepted** for schema version 1.
9. **Scan and loaded_disabled (not a listed concern; the body's rule is replaced).** Scan emits
   `loaded_disabled` directly rather than a cannot_determine carrying a definite-finding flag.
   It is a launchd-only verdict, needs no runbook, and exits 1. Scan's vocabulary is therefore
   running, failing, disabled, loaded_disabled, cannot_determine. Rule 5 for scan stays
   cannot_determine with reason `plist on disk, service absent; not declared`.
10. **Real print-disabled fixture: supplied.** intent/fleet-audit/evidence/
    print-disabled-gui501-2026-10-16.txt is the live output of `launchctl print-disabled
    gui/501` on the host (rc 0), captured by the supervisor; use it as the real override
    fixture (com.koekeishiya.yabai disabled, org.nixos.* enabled, four Apple labels disabled).
11. **Plist keys preserved.** Add `EnvironmentVariables` presence (keys only, never values) to
    the plist observation; the lab's tick plist carries one and the report must not leak it.
    `RunAtLoad: true` on that plist is observed, not an expectation, until the runbook says so.
12. **Package layout.** `product/fleet_audit/` holds `pyproject.toml` with a `fleet-audit`
    script entry, the package `fleet_audit/`, `fixtures/`, and `tests/`. The acceptance module
    runs offline only; any attempt at live collection under `--offline` is a test failure.
13. **Declaration directory.** The lab's declaration is `runbook/fleet/fleet.md`, and the
    tool is pointed at `runbook/fleet`, not `runbook/`. Discovery validates every
    frontmatter-bearing Markdown file (above), and `runbook/README.md` and
    `runbook/updates.md` carry the management operator's registry frontmatter, which is a
    different schema; `declared runbook` exits 3 on them, by design. Nothing in the tool
    changes: a declaration directory holds declarations only. The supervisor found this when
    writing the declaration on 2026-10-16 (NZ) and moved the file; the plan's path is amended.
