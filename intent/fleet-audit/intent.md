# Intent: Fleet Audit

Originator: the supervisor (Claude), 2026-10-16 (day 1). Change kind: the product. Decided after
four landscape sweeps (intent/research/), three candidate intents and two spikes
(intent/candidates/); provisional on day 1, binding on day 3 (2026-10-18) unless Byron objects in
an issue. The candidate draft is intent/candidates/fleet-audit.md; this file is what the lab
builds.

## Problem

Byron runs about a dozen small live projects from one Mac, each with a runbook that says what
should be scheduled, and launchd runs whatever was last loaded. Nothing checks that the two
agree, or that a loaded job is doing its work. The host today has twelve non-Apple LaunchAgents:

| Label | Declared | Live state on 2026-10-16 (spike 2) |
| --- | --- | --- |
| com.unattended.tick | every 600 s | loaded, 29 runs, exit 0, receipt 1.4 min old |
| com.management.tick | every 1200 s | loaded, 3038 runs, exit 0, receipt 18.5 min old |
| com.pdw.docker-restart | Sunday 03:30 | loaded, 10 runs, exit 0, log 3 days old |
| com.pdw.caffeinate | KeepAlive | running, pid 32776 |
| homebrew.mxcl.ollama | KeepAlive | running, pid 843, log 7 days old |
| com.koekeishiya.skhd | KeepAlive | running, pid 837 |
| com.koekeishiya.yabai | KeepAlive | disabled by override, service absent (exit 113) |
| org.nixos.skhd | KeepAlive | loaded, no pid, spawn scheduled, last exit 78 EX_CONFIG |
| org.nixos.yabai | KeepAlive | loaded, no pid, spawn scheduled, last exit 78 EX_CONFIG |
| com.google.GoogleUpdater.wake | every 3600 s | loaded, 1301 runs, exit 0, no declared output |
| com.google.keystone.agent.plist | empty plist | no Label, nothing to look up |
| com.google.keystone.xpcservice.plist | empty plist | no Label, nothing to look up |

Two of the twelve are failing in a loop (the nix skhd and yabai, each with a Homebrew twin) and
nobody knew. That is the finding the second spike produced and the supervisor confirmed by hand;
it is the kind of thing this product exists to say. What a person does today to learn it is run
`launchctl print` per label and read nested diagnostic text, which is why nobody does.

What exists: Healthchecks (dead man's switch, needs every job to ping it), LaunchInspector (a
Mac inventory UI whose JSON export lacks pid, exit code and working directory), Drift (snapshot
diffs of labels only). None join a declaration to loaded state to output evidence, and none keep
uncertainty as a result rather than collapsing it to healthy or empty.

## Proposed outcome

By build day 12, a read-only CLI, `fleet-audit`, in `product/fleet_audit/`, Python with uv,
stdlib plus one small YAML parser. It takes a directory of runbooks (Markdown with a frontmatter
block declaring the project's jobs) and the current user's launchd GUI domain, and prints one
line per job with a verdict and a reason that names the evidence. It never changes a job, never
runs a job's command, never reads a file it was not declared.

Commands:

- `uv run fleet-audit declared <dir>`: the registry the runbooks declare, validated (duplicate
  identities, missing plist paths, Label mismatches are errors). `--json` for the records.
- `uv run fleet-audit audit <dir> [--domain gui/501] [--json]`: the audit. Exit 0 all verdicts
  are running, healthy_idle or disabled-as-expected; 1 at least one failing, late,
  declared_not_loaded, loaded_disabled or drift verdict; 2 only cannot_determine remains; 3
  invalid input. JSON keeps every verdict with its observation time, source command and return
  code, so the exit code never hides uncertainty.
- `uv run fleet-audit audit <dir> --fixture <snapshot>`: the same audit over a frozen snapshot
  of launchctl output and stat results, for tests and for the blog.
- `uv run fleet-audit scan`: no runbooks; every non-Apple plist in ~/Library/LaunchAgents gets
  the launchd-only verdicts (running, failing, disabled, cannot_determine). This is what found
  the two nix failures and it is the zero-configuration entry point.

Verdict vocabulary, one per job plus zero or more drift findings:

| Verdict | Meaning |
| --- | --- |
| running | a KeepAlive or long-running job has a pid and launchd says running |
| healthy_idle | loaded, not running, last exit 0, and declared output or receipt within max age |
| late | loaded, declared output or receipt older than max age plus grace |
| failing | last exit nonzero, or KeepAlive with no pid and state spawn scheduled |
| disabled | an override disables it; expected_enabled false makes this healthy, true makes it a finding |
| declared_not_loaded | the runbook declares it, launchd has no such service (history unknown) |
| loaded_disabled | loaded and disabled at once (observed on the host for an Apple job) |
| cannot_determine | evidence missing, unreadable, future-dated, or no freshness contract declared |

Drift findings, when a runbook declares expectations: wrong_program, wrong_arguments,
wrong_working_directory, wrong_schedule, each comparing the registry, the plist on disk and
the loaded definition separately, since the three can differ.

The freshness contract is two fields with distinct meanings: `output.max_age_seconds` is how
old the evidence may be before the job is suspected; `grace_seconds` is how long a run may take,
so a receipt that is max age plus grace old is late and anything younger is not. A receipt
declared as `kind: ticks_jsonl` is read (bounded, last line only), not statted, and its
`result` field is what healthy_idle requires; `kind: mtime` can give healthy_idle only when the
runbook says mtime is sufficient evidence. This is the correction spike 2 forced: the first
policy wording let 20 plus 30 minutes be read as one 50 minute mtime threshold, and the
supervisor's own 45 minute runs would have looked late.

The lab is the first declared project: `runbook/fleet.md` declares com.unattended.tick with argv
`/bin/bash /Users/byron/repos/unattended/bin/tick`, working directory the repo, interval 600,
receipt `state/ticks.jsonl` as ticks_jsonl, max age 20 minutes, grace 30 minutes. The other
eleven jobs are covered by `scan` until their owners write a runbook; the lab does not declare
them (review answer 6).

Out of scope: changing or loading jobs, remediation, alerts, dashboards, remote hosts, system
domains, cron (`crontab -l` is not permitted on this host), GitHub or IaC reconciliation, exact
missed-run accounting across sleep and reboot (a `cannot_determine` with a reason is the
answer there, review answer 5).

## Affected users and systems

Byron and the supervisor first; then anyone running a handful of launchd jobs on a Mac. Reads:
plists under ~/Library/LaunchAgents, `launchctl print gui/<uid>` and `launchctl print
gui/<uid>/<label>`, `launchctl print-disabled gui/<uid>`, the mtime of declared output paths, the
last line of declared JSONL receipts. Writes: stdout and stderr only. The lab's blog shows the
audit of the lab's own loop from the first increment that can produce it.

## Constraints

- Python 3.12 with uv, `pyproject.toml` in `product/fleet_audit/`, stdlib plus PyYAML (or a
  smaller frontmatter parser if one fits in a file). Measure install size; the host has 2.6 GiB
  free and build jobs stop under 1.0.
- Every increment ships with a single proving command that exits nonzero on failure and prints a
  documented healthy line; CI runs it offline against fixtures. Live host runs are the
  supervisor's verification, pasted into the PR.
- The parser from the spike (`spike/launchctl_parse.py`, 454 of 454 labels into records, one
  structural warning) and its five real fixtures are the starting point, rewritten into the
  package, not copied blind. Fixtures are labelled macOS 26.5; nothing claims cross-version
  stability.
- Collection failure can never yield healthy_idle or an empty fleet: `launchctl list` exiting 1
  with no output inside a sandbox is `cannot_determine` for every job, with the return code in
  the reason. This was the sandbox artifact the research jobs hit, and it is the first test.
- Bound every subprocess (time, output size) and every file read (last 64 KiB of a receipt).
- No emojis, no em dashes. Humble output: a verdict names its evidence; `running` says
  "useful work not established" when no output contract exists.

## Increments

Roughly one PR each, two to three build days; the plan (phase 3) fixes files and order.

1. Registry and plist join: frontmatter validation, plist reading, Label match, `declared`.
2. Observer: `launchctl print` collection with explicit domain, parser and records, disabled
   overrides as an independent axis, fixtures and `--fixture` replay.
3. Verdicts: the vocabulary above over records, freshness contract with receipt reading, the
   collection-error rule, `audit` exit codes.
4. Drift: registry versus disk versus loaded for program, argv, directory, schedule.
5. `scan`, text and JSON reports with provenance, the lab's runbook, README, the first live
   report of the host on the blog.

## Open questions

1. Whether the Homebrew twins of the failing nix jobs are the intended ones is Byron's to answer;
   the audit reports both, it does not pick. No action on the host either way (the floor).
2. Should `scan` apply a default freshness contract to interval jobs with declared
   StandardOutPath (interval times three, say)? Leaning no: spike 2 showed defaults invented for
   undeclared jobs create false alarms. The spec may argue otherwise with evidence.
3. The LaunchInspector export gap (pid, exit code, directory) is worth an upstream issue after the
   lab; not in twenty days (review answer 2).
