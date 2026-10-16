Fresh-context review of branch change/nz-election-3 against main (merge-base 21edfd3), for
https://github.com/byronxlg/unattended/pull/11 (NZ election increment 3), HEAD 2ac4067. Worktree
.worktrees/nz-election-3, read-only. Follow REVIEW.md. Important or Nit, at most five nits,
nothing bin/lint reports. Do not approve.

Context: this increment adds the first network code (product/nz_election/pipeline/fetch.py),
live mode in refresh.py, the `NZ election hourly` workflow, orphan data branch bootstrap in
publish.py, and pages.yml changes (workflow_run, pinned data checkout into _nz-election-data,
rollback inputs, build manifest). The plan is intent/nz-election/plan.md ("Hourly refresh and
publication", "Pages workflow change", "Build order: Increment 3"); the spec is
intent/nz-election/spec.md (network paragraph near line 114, status and manifest contract near
137, publication concurrency and workflow_run near 145 to 147). The engineer's report is
state/jobs/nz-election-3/last.md. You cannot run GitHub Actions; reason from the YAML and the
Python it invokes.

Scope, in this order:
1. `.github/workflows/nz-election-hourly.yml` and `.github/workflows/pages.yml` (`git diff
   21edfd3..2ac4067 -- .github/workflows`). Walk the first live run on a repository with no
   refs/heads/data step by step: what every step does when the data checkout is absent, what
   refresh.py writes to GITHUB_OUTPUT on a fresh bundle, on a handled failure (HTTP error,
   parse_drift, validation) and on an unexpected exception; whether the publish job runs in each
   case and what the run's conclusion is; whether pages.yml then triggers (workflow_run guards:
   head_branch, head_repository, github.ref on a workflow_run event), resolves the data ref, and
   checks it out. Then the steady-state run with a data branch present. Check: permissions per
   job (GITHUB_TOKEN never reaches a step that does not need it; persist-credentials false
   everywhere; the extraheader in publish.py is the only credential path and the token does not
   land in argv or logs); nothing under _nz-election-data is executed or imported (build.py and
   verify.py read it as data only); the rollback inputs (validated before use, the manifest
   records rev-parse of what was checked out, a code_sha checkout replacing the tree after
   fetch-depth 0 keeps bin/metrics working); the concurrency groups (pages cancel-in-progress
   false, publication group) against the spec; whether the engineer's claim "handled failure then
   fails the workflow" matches the file (the supervisor believes it does not: validated=true is
   written before the non-zero exit and the step has continue-on-error) and which behaviour the
   spec asks for; the `Build election pages` step now runs before `bin/blog build` where it used
   to run after (does bin/blog build clear or overwrite site/nz-election).
2. `product/nz_election/pipeline/fetch.py` against the spec network paragraph: User-Agent and
   maxlag on every request, 20 s timeout passed to the transport, 2 MiB cap enforced before the
   body is read whole (read(LIMIT + 1) or equivalent, not Content-Length alone), at most three
   attempts, Retry-After honoured and an excessive value a handled failure rather than a sleep,
   redirects refused, non-JSON and wrong-page bodies rejected with named error codes, revision
   and timestamp validated through export.timestamp, no other host reachable. Can any exception
   escape acquire() that refresh.py would treat as unexpected when it is a handled network
   condition (URLError, socket.timeout, IncompleteRead, UnicodeDecodeError, json errors)?
3. `publish.py` diff: orphan bootstrap (attempt-numbered orphan branch name, what happens on
   retry after a lost race, no stale index from the code checkout leaking into the data commit),
   ownership of product/nz_election/data/ only, the lease rule and success_order untouched,
   the publication job's validate-before-git (export.validate_bundle on the downloaded artifact;
   symlinks, traversal, non-allowlisted names rejected).
4. `refresh.py` live mode: run URL and SHA recorded from the Actions environment, handled
   failures publish a status entry and retain last-good exactly as the fixture path does,
   unexpected errors abort without swapping, the GITHUB_OUTPUT contract matches the YAML.
5. The 8 new tests (`git diff 21edfd3..2ac4067 --stat -- '*test*'` must show only additions):
   does test_workflows.py pin every contract listed in plan.md's test inventory, and would
   each new test fail on 21edfd3? Any test that opens a socket or depends on the network?

Host run stands at 2ac4067: 240 passed, bin/lint ok, yaml ok, refresh and build and verify all
PASS, no-data build PASS, screenshots PASS 6 routes 12 baseline images (no template or style
changes in this increment; do not re-judge screenshots). The supervisor ran the pages.yml
manifest step's Python locally with the env set by hand and it produced the expected fields.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
