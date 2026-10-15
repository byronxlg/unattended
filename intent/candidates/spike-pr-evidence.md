# Spike result: pr-evidence

Job spike-pr-evidence, final message verbatim from state/jobs/spike-pr-evidence/last.md. Supervisor verification on 2026-10-16 02:40 NZ: `uv run --with pytest pytest -q spike/` in .worktrees/spike-pr-evidence, output in intent/candidates/spike-verification-2026-10-16.md.

**No for the small receipt alone; yes with the draft’s additional evidence:** exclusive assignment, clean start, ancestry, explicit output commits and no-other-writer attestations. Negative fixtures produced zero false exact links.

Created `spike/`: 117-line implementation, seven fixtures, tests, raw self-receipt and probe evidence.

Verification:
```text
UV_CACHE_DIR=/tmp/pr-evidence-uv-cache uv run --with pytest pytest -q spike/
...........                                                              [100%]
11 passed in 0.01s
```

Real squash scenario:
```text
UV_CACHE_DIR=/tmp/pr-evidence-uv-cache uv run spike/squash_demo.py
saved snapshot: exact, 3 original commits
walking main: 0/3 original commits
squash attributed to invocation: False
```
Every Git command and output is in [squash-transcript.txt](spike/squash-transcript.txt).

GitHub probe using the draft’s query:
```text
gh api graphql -f query="$(cat spike/github-query.graphql)"
exit=0
{"data":{"repository":{"pullRequests":{"nodes":[]}}}}
```
Network reachable; no live PR attribution tested.

Notable finding: clean HEAD boundaries cannot establish authorship. Exactness depends on trusted writer attestations.

**Commit blocked by sandbox permissions:**
```text
fatal: Unable to create '/Users/byron/repos/unattended/.git/worktrees/spike-pr-evidence/index.lock': Operation not permitted
```
Files remain uncommitted. The final receipt records unchanged HEAD and literal final status; the required post-commit capture could not be completed.