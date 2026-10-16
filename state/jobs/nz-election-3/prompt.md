# Build brief: nz-election increment 3 (hourly workflow, data branch bootstrap, Pages data checkout)

You are the engineer in the unattended lab (read AGENTS.md, then product/nz_election/AGENTS.md).
You are in the worktree `.worktrees/nz-election-3` on branch `change/nz-election-3`, based on
main at 21edfd3, which has increments 1 and 2 merged (232 tests, six routes live in no-data mode
at https://byronxlg.com/unattended/nz-election/). Commit there; never push.

## Goal

Increment 3 of intent/nz-election/plan.md "Build order": the product goes from a static skeleton
to a site fed by a scheduled job. Four pieces:

1. `pipeline/fetch.py`: the only code in the product that talks to the network. Fetches the
   current revision and wikitext of the Wikipedia polling page through the API, serially, with
   the spec's User-Agent, `maxlag=5`, 20 s timeout, 2 MiB response cap, at most three attempts,
   `Retry-After` honoured and an excessive delay turned into a handled failure. Never fetches
   linked news sources or any other host. Tests inject a fake transport; no test ever opens a
   socket.
2. `refresh.py` live mode next to the existing `--fixtures` mode: acquires through fetch.py,
   records the real run URL and code SHA from the Actions environment, writes the same bundle
   contract. Handled failures (HTTP, validation, `parse_drift`) publish a status entry and retain
   the last-good bundle exactly as the fixture path does; unexpected errors abort without swapping.
3. `.github/workflows/nz-election-hourly.yml` (`name: NZ election hourly`) and the publication
   transport in `publish.py` for a real remote: orphan `data` branch bootstrap when
   `refs/heads/data` is absent, ownership of `product/nz_election/data/` only, the retry and
   older-run rules already enforced in `publish.publish`, an Action summary.
4. `pages.yml`: `workflow_run` on that workflow name, read-only data ref resolution, a second
   checkout of that exact SHA into `_nz-election-data/`, `cancel-in-progress: false`, rollback
   dispatch inputs (pinned code and data SHAs), the build manifest recording the SHAs actually
   checked out. Absent ref stays the supported first-deploy state.

Plus `tests/test_workflows.py`, the runbook sections the plan names (failed refreshes, missing
data, retries, rollback, Pages minutes measurement) and the product AGENTS.md rules this teaches.

## Read first, in this order

1. intent/nz-election/plan.md: "Hourly refresh and publication" (all ten points), "Pages workflow
   change", "Verification and test inventory" (test_workflows), "Build order: Increment 3",
   "Supervisor decisions" 2, 3 and 4.
2. intent/nz-election/spec.md: the network paragraph near line 114, the status and manifest
   contract near line 137, the publication concurrency and `workflow_run` paragraphs near lines
   145 to 147, "Supervisor resolutions".
3. product/nz_election/pipeline/{refresh,publish,export,storage,build}.py and runbook.md as they
   are. Build on them. `export.validate_bundle`, `export.timestamp` (canonical
   `YYYY-MM-DDTHH:MM:SSZ`, `INVALID_TIMESTAMP`) and `publish.success_order` are the invariants
   three review rounds settled; do not loosen any of them.
4. .github/workflows/pages.yml and tests/test_metrics_integration.py::test_pages_workflow_contract
   (the root test that pins pages.yml: `bin/metrics` before `bin/blog build`, the literal
   `GH_TOKEN` env, `fetch-depth: 0` on the first step). It must keep passing untouched.
5. product/nz_election/tests/test_pipeline.py and test_build.py: the local bare-repository
   transport pattern and `test_no_data_first_build`; extend the pattern, do not fork it.
6. REVIEW.md (how you will be reviewed).

## Constraints

- No network in your sandbox, ever, and none in any test. fetch.py takes its HTTP function as a
  parameter (or an equivalent seam you choose); production wires `urllib.request` from the
  standard library. Tests prove: User-Agent and maxlag sent, timeout passed, oversize body
  rejected before it is read whole, `Retry-After` waited (with an injected sleep) and capped,
  three attempts then a handled failure with a named error code, non-JSON and wrong-page bodies
  rejected, revision and timestamp validated through `export.timestamp` where they are instants.
- You cannot run GitHub Actions. test_workflows.py parses both YAML files and asserts the
  contracts the plan names (triggers, permissions per job, concurrency groups and their
  cancel-in-progress values, the trusted-branch and same-repository guards on `workflow_run`,
  the checkout steps and their refs, the literal build command, no step that executes anything
  from `_nz-election-data/`). Orphan bootstrap and status-after-handled-failure are proven
  against local bare repositories under tmp_path through publish.py, the same way
  test_pipeline.py does it; a bare repository with no `data` ref is the bootstrap case.
- Permissions: the refresh job has `contents: read`; only the publication job has
  `contents: write`; pages.yml keeps `contents: read` on build and the existing deploy
  permissions. `GITHUB_TOKEN` only, no secrets, no new actions beyond those already used
  (checkout, setup-uv, upload-artifact and download-artifact for the staged bundle,
  upload-pages-artifact, configure-pages, deploy-pages). Pin new actions by major tag like the
  existing ones.
- The hourly workflow's artifact between jobs is data, not code: the publication job validates
  it with `export.validate_bundle` before touching git. Reject symlinks, traversal and
  non-allowlisted filenames (the allowlist already exists in export.py).
- Data ref resolution in pages.yml is read-only (`git ls-remote` or the REST ref endpoint through
  `gh api`); an empty result is "absent" and builds in no-data mode; a non-zero exit is a failure
  that stops the build. Then `actions/checkout` with `ref: <sha>` and `path: _nz-election-data`,
  `persist-credentials: false`. Nothing under that path is ever executed or imported.
- Rollback inputs are optional `workflow_dispatch` inputs: validate as 40 lowercase hex before
  use, fail the run on anything else, and write the SHAs actually checked out (not the inputs)
  into `site/nz-election/build-manifest.json`, which already exists with `data_sha` null on
  first deploy. Keep its existing fields; add `build_run_url` and `data_available` if missing.
- Do not force push; `--force-with-lease` against the fetched tip is already the rule. Never
  `git add .`. A byte-identical commit is skipped (already enforced).
- Never edit anything under product/nz_election/fixtures/. Never edit existing tests; add new
  test files or new functions. Exact arithmetic stays. Python 3.12+, stdlib only at runtime.
- Do not edit state/, posts/, prompts/, bin/, root tests, ci.yml, or any file outside product/,
  .github/workflows/nz-election-hourly.yml and .github/workflows/pages.yml.
- No emojis, no em dashes anywhere, including workflow names and summaries. Comments say why.
- When the plan's wording and existing code disagree, follow the code, record the departure in
  your final message, never stop to ask.

## Definition of done

Run from the worktree root and paste each command's output in your final message:

1. `uv run --with pytest pytest -q product/nz_election/tests/test_workflows.py` expected: all
   passed (plan target 4: `test_hourly_contract`, `test_orphan_bootstrap`,
   `test_pages_triggers_and_pinned_checkouts`, `test_status_published_after_handled_failure`;
   name what you merged or added and why).
2. `uv run --with pytest pytest -q product/nz_election/tests/test_pipeline.py product/nz_election/tests/test_build.py`
   expected: all passed, the fetch tests included wherever you placed them.
3. `uv run --with pyyaml python -c "import yaml,sys;[yaml.safe_load(open(p)) for p in sys.argv[1:]];print('yaml ok')" .github/workflows/pages.yml .github/workflows/nz-election-hourly.yml`
   expected: `yaml ok`.
4. `uv run product/nz_election/pipeline/refresh.py --fixtures --out artifacts/nz-election/data`
   expected: `PASS refresh: polls bundle` (the fixture path is unchanged).
5. `uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/does-not-exist --out /tmp/nz-nodata`
   expected: `PASS build: 6 routes`.
6. `uv run product/nz_election/pipeline/verify.py all` expected: the four check lines then `PASS all`.
7. `uv run --with pytest pytest -q` expected: all passed, 0 skipped, count greater than 232.
8. `bin/lint` expected: `lint ok (<N> text files)`. Stage new files first.
9. `git status --short` expected: empty after your final commit.

The supervisor runs the screenshot command on the host after your commit (no template changes
are expected this increment; say so if you made any) and, after merge, dispatches `NZ election
hourly` and checks orphan creation, status publication and the following Pages run.

Final message under 40 lines: files changed, the nine outputs, how the first live run will behave
on a repository with no `data` branch (step by step, from the workflow file), departures from
the plan, open questions for the supervisor.
