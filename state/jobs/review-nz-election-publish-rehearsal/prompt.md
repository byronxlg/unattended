Fresh-context review of PR #96 (nz-election-publish-rehearsal), read-only. Worktree .worktrees/nz-election-publish-rehearsal,
branch change/nz-election-publish-rehearsal, head 9ac171a on base eb61e0a. Diff: git diff eb61e0a...9ac171a.
Judge against REVIEW.md. Brief: state/jobs/nz-election-publish-rehearsal/prompt.md (goal, constraints).

The change: a dispatch-only workflow .github/workflows/nz-election-night-rehearsal.yml and pipeline/night_rehearsal.py
run night_live.py's publication path end to end (first-feed failure, published cycle, failed deployment and recovery,
bounded successor) against an isolated target; night_live.py and publish.py refactored to share orchestration.
Check: the rehearsal can never write the production data branch or deploy production Pages (permissions, refs, any
token use, any path through publish.py that could take a production ref); the production night-live and pages workflows
behave exactly as before (the refactor of night_live.py and publish.py is behaviour-preserving for the real path, incl.
the s197 freeze and the 8 Nov stop); the successor chain is bounded; new tests would fail on the old code and are not
vacuous; nothing on data, provenance, absence or accessibility was loosened.
Supervisor host run: test_night_operation, test_workflows, test_publish* 74 passed; bin/lint ok. Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
