# Plan brief: NZ election M1 (Build stage, plan mode)

You are the engineer in the unattended lab (read AGENTS.md). This job writes plan.md for the
product change `nz-election`, milestone M1 only. Your sandbox is read-only and has no network:
your final message IS the deliverable. The supervisor copies it verbatim into
intent/nz-election/plan.md, so write one complete markdown document, title on the first line,
nothing before or after it, under 300 lines. Write for an engineer who never saw this
conversation and will implement from the plan alone in a fresh context, in a worktree, with
no network.

Read first, in this order: intent/nz-election/spec.md (the "Supervisor resolutions" section
overrides the body where they differ; the M1 scope there is the whole scope of this plan),
intent/nz-election/intent.md, intent/research/nz-election-data-sources.md (sections 1, 5, 8:
exact URLs, the wikitext shape, the s191-193 rules and the 2023 fixture), AGENTS.md (Design
section), .github/workflows/pages.yml and ci.yml, bin/blog (how site/ is built and what must
be preserved), bin/lint, pytest.ini, REVIEW.md. Do not write files, do not run anything that
mutates.

## What the plan must contain

1. Layout: every file under product/nz_election/ that M1 creates (pipeline, fixtures, tests,
   web, config, AGENTS.md, runbook.md), the two workflow files (.github/workflows/
   nz-election-hourly.yml and the pages.yml diff), and how the root test run
   (`uv run --with pytest pytest -q`) collects the product tests without breaking the existing
   tests/ (check pytest.ini and the root layout). uv inline metadata, stdlib first; name any
   dependency and why it is unavoidable.
2. Fixtures the supervisor must capture before the build (the sandbox has no network): for
   each, the exact URL, the file name under fixtures/, and the manifest fields (url, captured
   at, sha256, reviewer). At least: the Wikipedia wikitext of the opinion polling page at a
   pinned revision (name the API URL that returns wikitext with the revision id), the 2023
   party-quotients CSV, the 2023 party votes CSV, and the 2023 party lists if a CSV exists.
   Say what the build does if a capture is absent (fail the test with a named message, never
   fabricate).
3. The poll parser: wikitext table shape, the columns kept, how event rows, footnotes,
   merged cells and the Māori-roll and preferred-PM tables are excluded, the row id scheme
   (stable across revisions), the reviewed party mapping file, what `parse_drift` means in
   code. Function signatures.
4. The allocator contract from the spec, implemented twice (Python, ES module) with shared
   golden inputs under fixtures/ and a parity test. Name the edge tests from the spec as
   test functions.
5. The averaging method as functions: window selection, coherent vector check, exact
   integer shares with a scale, published method_version. What the polls page shows when the
   vector is incomplete.
6. Data contracts for M1 outputs (polls.json, averages.json, seats.json, status.json,
   manifest.json, CSV siblings, LICENCES.md) with the envelope from the spec; the exact keys.
7. The hourly workflow: trigger (cron 17 * * * * plus workflow_dispatch), steps, how it
   bootstraps the orphan `data` branch when absent, how it commits only its own files, the
   non-fast-forward retry, the concurrency group, what it writes to the Action summary on
   failure, and how status.json is still published after a handled failure. The pages.yml
   change: workflow_run trigger on this workflow's exact name, a second checkout of the
   `data` branch into a separate path, the product build step before `bin/blog build`, the
   build manifest with both SHAs, and what happens when the data branch does not exist yet
   (the first deploys happen before the first hourly run: the product build must render
   "no data yet" pages, not fail).
8. The web layer: build.py rendering (templates, how pages are generated without a bundler),
   the ES modules M1 ships (seat strip interaction only if any; otherwise none), CSS tokens
   from the spec's Design section, the six routes M1 produces under site/nz-election/
   (polls at /, electorates, night and campaign as placeholders, downloads, methods), the
   source-note component, and the no-JS behaviour.
9. Verification: verify.py with the M1 checks (polls, thresholds, provenance, pipeline) and
   their PASS lines; the screenshot script (serves site/ under /unattended/, 390x844 and
   1280x800, writes PNGs plus a manifest, uses the installed Chromium) and its PASS line with
   the M1 route and image counts; the pytest files and test function names; `bin/lint`.
10. Build order as a checklist (`- [ ] ` items) in increments that each ship as a PR:
    increment 1 is allocator plus poll parser plus fixtures plus tests (no UI); increment 2
    is the pipeline outputs, build.py, the six pages, screenshots; increment 3 is the two
    workflows and the data branch bootstrap. Each item names its proving command and the
    expected output line. Finish each increment with `bin/lint` and the full test run.
11. `## Concerns`: anything in the spec you cannot implement as written for M1, with the
    route you would take; anything in pages.yml or bin/blog that the product build could
    break; the Pages minutes estimate for hourly builds.

Decisions already made (do not reopen): no bundler, no runtime libraries, no fonts
downloaded; the type stack is the system sans from the spec; the data branch is created by
the workflow, never pushed from a machine; builds never fetch; fixtures are captured by the
supervisor; the seat strip is the hero with the party counts inside it; copy in voter words.
