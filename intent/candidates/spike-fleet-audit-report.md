# Fleet Audit launchctl observer spike

The host-specific format is useful enough to fixture, but not a reliable universal
interface. Of 454 labels in the GUI services block, all 454 returned exit 0; 453
produced structurally usable records, and **8** had all four requested fields:
state, program, argv and interval/calendar schedule. No record had all nine
requested fields present. Missing values remain null, not inferred from program,
state, plists or default scheduler behavior.

[Full per-label table](table.md) names all 454 labels, fields present, missing
fields and warnings. [Normalized records](records.json) and [collection snapshot](snapshot.json)
retain the evidence. The snapshot includes separate stdout, stderr, return codes,
commands and a UTC timestamp. Only credential-like environment values are redacted;
no job, argv or schedule fields were intentionally redacted. No other project's
files or output logs were read. No plists were needed for this experiment.

| Four-field completeness | Count | Explanation |
| --- | ---: | --- |
| Complete | 8 | Interval/calendar and explicit argv available |
| Missing schedule | 288 | No run interval or calendar descriptor in the output |
| Missing argv and schedule | 151 | Neither explicit arguments nor supported schedule |
| Missing argv | 4 | Timer present, no arguments block |
| Missing program, argv and schedule | 2 | Submitted jobs expose program identifiers instead |
| Structurally rejected | 1 | Malformed nested diagnostic output |

The eight complete labels are com.apple.geoanalyticsd,
com.apple.loginwindow.LWWeeklyMessageTracer, com.apple.pluginkit.pkreporter,
com.google.GoogleUpdater.wake, com.management.tick, com.pdw.docker-restart,
com.unattended.tick and us.zoom.updater.

The four timed jobs without argv are com.apple.ap.adprivacyd,
com.apple.appleseed.seedusaged, com.apple.speech.speechdatainstallerd and
com.apple.talagent. talagent has two calendar dictionaries, preserved as a list.
The two without executable paths are com.apple.Passwords.MenuBarExtra and
com.docker.helper. A program identifier is not an executable path.

com.apple.networkserviceproxy is the structural failure. Its descriptor contains
file-descriptor fields joined to following keys and key-material joined to a
closing brace on the same line. The parser refuses to guess at this nesting and
returns nullable fields plus warnings. Fifteen other services contain duplicate
keys; these are preserved as lists and warned about rather than silently overwritten.
Nineteen submitted jobs have a submitter description instead of a plist path;
that field remains null with a warning. The full table names each affected label.

Schedules here mean only `run interval` or `com.apple.launchd.calendarinterval`.
XPC activities, background tasks, KeepAlive and event-based launches are not
normalized into timer schedules. Thus 8/454 measures the requested field coverage,
not the proportion of healthy services or the parser's syntax acceptance rate.

## Disabled versus absent

Six overrides say disabled. Five are also absent (per-service exit 113):
com.apple.ManagedClientAgent.enrollagent, com.apple.Siri.agent,
com.apple.FolderActionsDispatcher, com.apple.ScriptMenuApp and
com.koekeishiya.yabai.

com.apple.appleseed.seedusaged.postinstall is disabled **and loaded** (exit 0),
a combination not observed in the candidate's earlier research.

Four additional queried labels are absent: homebrew.mxcl.supervisor, com.okx.a2a,
com.openai.chat-helper (all explicitly enabled overrides), and
com.google.keystone.agent (no override). No enumerated label was absent during
collection. These observations say nothing about whether a service was ever loaded.

`launchctl list` returned 1 with empty stdout and stderr. `crontab -l` through zsh
returned 127, empty stdout and `zsh:1: operation not permitted: crontab` on stderr.
Neither is evidence of an empty inventory.

## Reproduction and limitations

All files are under spike/. `collect.py` uses only read-only launchctl print/list
and crontab commands, with a ten-second timeout per call. `launchctl_parse.py` is
163 lines, stdlib only, tested with Python 3.12. Five real JSON fixtures retain the
original command, status and output streams. Synthetic tests additionally cover
list descriptor syntax, truncation, duplicates and arguments containing syntax.
Tests also exercise the frozen host-wide snapshot and real multi-calendar job.

The host was identified as macOS 26.5 by the candidate, not independently verified.
Collection is sequential, not atomic. Tick changed from running during initial
inspection to not running in the final frozen snapshot. There is no cross-version
compatibility claim. Diagnostic output cannot unambiguously encode every possible
argument with embedded newlines or indentation; only the observed argv format and
explicit synthetic cases are covered. Missing schedules are unknown, not "none".
The spike uses timeouts but does not bound subprocess output bytes.

The sandbox denies the default uv cache, so verification uses a cache inside spike/:

```sh
export UV_CACHE_DIR="$PWD/spike/.uv-cache"
uv run --with pytest pytest -q spike/
```

Replay the table without touching the host:

```sh
uv run --python 3.12 spike/launchctl_parse.py
```

`uv run --python 3.12 spike/collect.py` replaces the snapshot and fixtures with live
observations; frozen run-count assertions will then require explicit review.
