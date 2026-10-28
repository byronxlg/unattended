Fresh-context review of PR #121 (nz-election-import-rehearsal), read-only. Worktree .worktrees/nz-election-import-rehearsal,
branch change/nz-election-import-rehearsal, base origin/main. Diff: git diff origin/main...HEAD. Judge against REVIEW.md.

Goal: an Actions workflow_dispatch rehearsal (input import_only) exercises settlement capture, official result import and
rollback end to end on synthetic local adapters, isolated from production: no write permission, no credentials, no push
to the data branch or Pages, and the production CLI paths (result_import.py, settlement_capture.py) keep their real
defaults so nothing synthetic can reach a real import.
Check: the new job's permissions and checkout; whether the default `rehearse` job still runs when import_only is false
and is skipped when true; whether any injected adapter (capture_reader, pin_data, publisher, provenance_check) can be
reached from the CLI or workflow arguments; whether the rehearsal's PASS lines prove the transitions it claims (settled,
official, rollback each verified, not just exit 0); the runbook section matches the code.

Output: verdict accept or request changes, then findings ranked Important/Nit with file:line. You cannot approve.
