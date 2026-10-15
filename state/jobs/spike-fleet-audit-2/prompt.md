# Spike 2: Fleet Audit interpretation on the real host

Same worktree, same throwaway branch (the supervisor committed your spike/ files as 57253ed;
the sandbox now allows commits, so commit this time). Under 20 minutes of work. Read first:
spike/README.md (yours), intent/candidates/fleet-audit.md section "Interpretation and remaining
one-day checks", and the supervisor's policy in intent/candidates/review-2026-10-16.md under
"Fleet Audit" (output age 20 minutes for ticks, grace 30 minutes; cannot_determine is a finding).

## Goal

Answer with evidence: when the parser's records for the host's twelve non-Apple LaunchAgents
(the plists under ~/Library/LaunchAgents not starting with com.apple) are interpreted with that
policy, does the audit produce at least one true finding a person would act on, and is every
verdict defensible against the plist and the service's own state?

## Do

1. Write spike/audit.py (stdlib only, under 200 lines) that, for each of the twelve plists:
   reads the plist with plistlib (declared label, program, schedule, KeepAlive, RunAtLoad,
   StandardOutPath/StandardErrorPath), takes the parsed `launchctl print gui/$(id -u)/<label>`
   record (reuse spike/launchctl_parse.py; collect live, read-only), reads the disabled
   override, and stats the declared log paths if any (mtime only, never contents). Then assigns
   one verdict from: running, healthy_idle, late, failing, disabled, declared_not_loaded,
   loaded_disabled, cannot_determine, with a one-line reason naming the evidence.
2. Print the audit as a table: label, declared schedule, loaded, pid, runs, last exit, log age,
   verdict, reason. Save it as spike/audit.md and the raw records as spike/audit.json.
3. For every verdict that is not running or healthy_idle, say in the final message whether you
   believe it is true (and why a person would act) or a policy artifact. Check at least the
   two tick loops against bin/tick's own behaviour (tick can exit 0 after a skip; its receipt is
   state/ticks.jsonl in each repo, mtime only).
4. Add tests to spike/test_parse.py or a new spike/test_audit.py for the verdict function over
   frozen records: one of each verdict, built from the real records where available and
   synthetic otherwise, plus the rule that a collection error can never yield healthy_idle.
5. Commit on this branch.

## Constraints

Read-only on the host: never bootstrap, bootout, enable, disable, kickstart, load or run any
job. Read only plists under ~/Library/LaunchAgents, launchctl output, and file mtimes of
declared log paths and state/ticks.jsonl; never file contents of other projects. No
dependencies. Do not edit anything outside spike/. No emojis, no em dashes.

## Definition of done

`uv run --with pytest pytest -q spike/` exits 0 with more tests than before (17). Final message
under 60 lines: the audit table, the answer to the goal question, which findings are true and
which are artifacts, and what the policy got wrong.
