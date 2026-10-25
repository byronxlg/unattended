Fresh-context review of PR #85 (nz-election-result-import), read-only. Worktree .worktrees/nz-election-result-import,
branch change/nz-election-result-import, head 3309ff2. Diff: git diff origin/main...3309ff2. Judge against REVIEW.md.
Brief: state/jobs/nz-election-result-import/prompt.md (in the main checkout at /Users/byron/repos/unattended).

Focus: the dispatch-only workflow cannot publish a settled or official state without the refusal checks passing;
official provenance (URL distinct from the preliminary feed, retrieved on or after 27 Nov) is enforced where
result_states.py reads it; the leased night rollback cannot race the night-live loop or leave data half-written;
publish.py changes do not change behaviour for existing callers; runbook/night.md commands match the code; no secret
or raw upstream text echoed in errors or logs.
Supervisor host run on 3309ff2: result_states*, workflow*, night_operation, result_import tests 143 passed incl. host
Chromium; lint ok; YAML parses, trigger workflow_dispatch only. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
