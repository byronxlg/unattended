# Spike result: fleet-audit

Job spike-fleet-audit, final message verbatim from state/jobs/spike-fleet-audit/last.md. Supervisor verification on 2026-10-16 02:40 NZ: `uv run --with pytest pytest -q spike/` in .worktrees/spike-fleet-audit, output in intent/candidates/spike-verification-2026-10-16.md.

**Yes, for host-specific fixtures, with limits:** 454 labels, 453 structurally usable records, **8 complete** with state, program, argv and schedule.

The [full 454-row table](spike/table.md) names every label, present/missing fields and warnings.

| Missing required fields | Labels |
| --- | ---: |
| None | 8 |
| Schedule | 288 |
| Argv and schedule | 151 |
| Argv | 4 |
| Program, argv and schedule | 2 |
| All, structural rejection | 1 |

`com.apple.networkserviceproxy` fails because nested diagnostic fields and closing braces run together. The remaining omissions reflect unavailable fields or unsupported schedule types. Details and affected names: [report](spike/README.md).

**Disabled and absent:** `com.apple.ManagedClientAgent.enrollagent`, `com.apple.Siri.agent`, `com.apple.FolderActionsDispatcher`, `com.apple.ScriptMenuApp`, `com.koekeishiya.yabai`.

**Disabled but loaded:** `com.apple.appleseed.seedusaged.postinstall`, a surprising difference from earlier research.

**Absent without a disabled override:** `homebrew.mxcl.supervisor`, `com.okx.a2a`, `com.openai.chat-helper`, `com.google.keystone.agent`. All nine absent lookups returned 113; no enumerated label was absent.

`launchctl list`: exit 1, empty output. `crontab -l`: exit 127, operation not permitted.

Added only `spike/` files: 163-line parser, collector, five real fixtures, tests, snapshot, normalized records and report. Verified with:
```text
export UV_CACHE_DIR="$PWD/spike/.uv-cache"
uv run --with pytest pytest -q spike/
.................                                                        [100%]
17 passed in 0.06s
```

Cross-version reliability remains untested. **Commit blocked:** the sandbox denied creation of the worktree’s Git `index.lock` outside the writable directory. Files remain uncommitted.