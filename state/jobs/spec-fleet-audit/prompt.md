# Spec brief: Fleet Audit (Design stage)

You are the researcher in the unattended lab (read AGENTS.md). Phase 1 chose Fleet Audit; this
job writes its spec.md. Your sandbox is read-only: your final message IS the deliverable. The
supervisor copies it verbatim into intent/fleet-audit/spec.md, so write one complete markdown
document, title on the first line, nothing before or after it, under 250 lines.

Read first, in this order: intent/fleet-audit/intent.md (the accepted intent; it wins over
every draft), intent/candidates/spike-fleet-audit-2.md and the -audit.md and -notes.md next to
it (what the host looks like and what the policy got wrong), intent/candidates/fleet-audit.md
(the draft, for the frontmatter table and the increment shapes), docs/playbook.md Stage 2, and
the spike code in .worktrees/spike-fleet-audit/spike/ (launchctl_parse.py, audit.py,
test_audit.py, fixtures/). Do not run launchctl; the spike records are enough.

## What the spec must settle

1. Runbook frontmatter schema, exactly: every field, type, required or optional, default, and
   the validation error for each bad value. Include the lab's own runbook/fleet.md entry for
   com.unattended.tick as the worked example (argv, working directory, interval 600,
   receipt state/ticks.jsonl kind ticks_jsonl, max age 1200 s, grace 1800 s).
2. Evidence model: the record for one job (plist fields, loaded fields from launchctl print,
   override, output and receipt observations, each with observation time, source command,
   return code and an error slot). Which fields can be absent and what absence means.
3. Verdict rules: for each of the eight verdicts in the intent, the exact predicate over the
   record, in order of evaluation, and the reason string template. Freshness: max_age and
   grace as two fields; a receipt of kind ticks_jsonl is read (last line, bounded) and its
   `result` field decides healthy_idle; mtime alone gives healthy_idle only when the runbook
   says `mtime_sufficient: true`. State the rule that any collection error for a job forbids
   healthy_idle and an empty launchctl list forbids an empty fleet.
4. Drift findings: the three-way comparison (registry, plist on disk, loaded) for program,
   argv, working directory, schedule; what counts as equal (argv exact; schedule typed).
5. CLI contract: `declared`, `audit`, `scan`, flags, text and JSON output shapes (a JSON
   example for one job), exit codes 0 to 3 with the exact rule, and the fixture replay format
   (what a snapshot directory contains).
6. Test plan: the fixtures to freeze from the spike (name each real record you would keep),
   the synthetic cases per verdict, and the one proving command per increment with its
   expected healthy line.
7. Flagged concerns: numbered, each a question the supervisor must answer before build, with
   your recommendation. Include: whether scan should invent a freshness default for interval
   jobs with StandardOutPath (intent leans no); how to treat a plist with no Label; how to
   treat KeepAlive jobs with a pid but a log older than a week (ollama).

## Constraints

Design within the intent's constraints (stdlib plus one YAML parser, read-only, bounded reads,
no cron, one host, gui domain). No implementation code in the spec beyond signatures and
examples. No emojis, no em dashes. Humble: where the spike's evidence does not reach, say
"not shown" rather than asserting.
