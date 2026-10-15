# Spike 2 notes (spike/audit-notes.md, written by Codex)


## Answer

Yes: two actionable observations, org.nixos.skhd and org.nixos.yabai. Both plists
request KeepAlive=true; both services are loaded and enabled, have no PID, are
spawn scheduled, and last exited 78: EX_CONFIG. An operator should establish which
installation is intended, then repair its configuration or retire the obsolete
definition. The Homebrew skhd is concurrently running. That is evidence of parallel
installed definitions, not proof they conflict. No configuration files, executable
contents or other-project logs were read to diagnose a cause. A snapshot does not
prove continuous failure or predict whether the next spawn will work.

The twelve plists yield nine loaded services, one explicitly disabled and absent
service, and two empty dictionaries without declared labels. Verdict counts: three
running, two failing, one disabled, six cannot_determine. No observed late,
healthy_idle, declared_not_loaded or loaded_disabled cases. The tests cover these
four remaining verdicts using explicitly synthetic variants of real records.

See audit.md for the table and audit.json for selected plist declarations, raw
launchctl streams/status, parsed records, overrides, exact stat errors and mtimes.
Collection timestamp: 2026-10-15T13:37:56.188884+00:00. Rows have individual observation
times; commands and stats are sequential, not an atomic snapshot.

## Every non-running verdict

| Label | Assessment and potential action |
| --- | --- |
| org.nixos.skhd | True failure observation: enabled KeepAlive job, no PID, spawn scheduled, exit 78. Reconcile intended installation and repair or retire the failed definition. |
| org.nixos.yabai | True failure observation, same evidence. The differently named Homebrew definition is disabled, not a working substitute established by this audit. |
| com.koekeishiya.yabai | True disabled/absent configuration, not necessarily a fault. Disabled override plus exact service-not-found exit 113. Confirm intent when reconciling the two yabai definitions; do not automatically enable it. |
| com.google.keystone.agent.plist | True declaration gap: empty dictionary, no Label. Investigate whether an obsolete updater placeholder should remain. Calling it an absent declared service would be an artifact of filename inference. |
| com.google.keystone.xpcservice.plist | Same empty-dictionary evidence and uncertainty; no service lookup was invented from its filename. No proof an updater is broken. |
| com.google.GoogleUpdater.wake | Policy/evidence limitation, not a demonstrated fault: 3600-second timer matches, loaded, not running, 1301 runs, last exit 0; no declared logs or completion freshness contract. Add a contract if health needs auditing. |
| com.management.tick | Policy/evidence limitation: 1200-second timer matches; last exit 0; receipt and log ages both 18.5 minutes. Fresh tick output, but no evidence of supervisor result contents. Add scoped completion evidence rather than restart a seemingly timely loop. |
| com.unattended.tick | Same limitation: 600-second timer matches; last exit 0; receipt and log ages both 1.4 minutes. No age violation. Supervisor completion remains unknown. |
| com.pdw.docker-restart | Policy/evidence limitation: declared and loaded Sunday 03:30 match, no PID, 10 runs, exit 0, log age 4336.5 minutes. No weekly completion deadline or log-write semantics. Do not apply the tick threshold or claim healthy/late from these facts. |

The cannot_determine findings are true statements about missing evidence or policy.
Treating them as operational faults requiring restarts would be an artifact. The
running labels report only observed process state, not health. Old Ollama log mtime
(10542.6 minutes) and missing skhd log files do not contradict their running PIDs.
The missing /tmp log paths returned ENOENT, not sandbox permission errors.

## Tick behavior and policy problems

The authorized repository bin/tick inspection establishes:

- A live supervisor PID causes a log message and exit 0 before the receipt append.
- A normal tick appends state/ticks.jsonl even when no supervisor was needed, or
  when a usage-limit marker prevents launching it. A fresh receipt therefore does
  not establish a completed supervisor run.
- Supervisor exit status/result is stored in the receipt. The shell's final Python
  append can exit 0 even when that stored supervisor status is nonzero.
- The default supervisor timeout is 2700 seconds (45 minutes); receipt writing
  follows the wait. Timer period plus work duration can exceed a simple age bound.

Management's receipt and log were statted, never opened. Its bin/tick contents were
not read because other-project file contents are forbidden. The management check
uses the task's stated skip possibility and treats its completion as unknown; it
does not assume its implementation is byte-identical to the lab script.

This implementation interprets 20-minute maximum age plus 30-minute grace as a
50-minute threshold, applied to the receipt rather than log mtime. Ages over 20
but at most 50 minutes are within grace, not late. Future mtimes and missing or
unreadable required evidence are cannot_determine. A late verdict means only that
the receipt age violates that numerical policy; it does not prove missed execution.
Long supervisors and pre-receipt skips could make such a verdict a policy artifact.
Neither real tick crossed even the initial 20-minute threshold in this snapshot.

The policy requests both tick activity and supervisor completion, but mtime-only
access cannot verify the latter. It also supplies no expectations for updaters,
weekly jobs or permanent daemons. Filling those gaps with the tick threshold would
create false alarms. Useful next policy work: separate process state, tick activity,
supervisor outcomes and expected intentional disablement; define per-job evidence
and time budgets including runtime, sleep and skips. No such new defaults were
invented for these twelve records.

## Implementation and checks

Only spike/ changed. audit.py is stdlib-only and under 200 lines. It reuses the
previous collector's read-only subprocess wrapper and credential redaction, and
launchctl_parse.normalize. All nonempty declarations match the loaded program,
argv, explicitly declared working directory and supported schedule when loaded.
KeepAlive, RunAtLoad and stdout/stderr paths are retained from the plist; KeepAlive
and RunAtLoad loaded drift are not independently normalized by the first spike.
Unknown overrides, lookup failures, parser warnings or compared-field differences
cannot produce healthy_idle. A recognized exact service-not-found response can
support absence, not health. Duplicate stdout/stderr paths are statted once.

The synthetic healthy_idle case gives an updater an explicit output-age-only
contract and recent output. That contract does not claim supervisor completion.
It is not applied to the real updater or either tick. Synthetic late tests use a
stale receipt; disabled/loaded and enabled/absent variants exercise independent
axes without changing the host.

Verification: `uv run --with pytest pytest -q spike/`.
