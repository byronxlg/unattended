The main gaps are **deployed acceptance evidence and repeatable hardening checks**, not missing replay or freeze implementations. No files changed; no network or full-suite runs.

Paths below use `P = product/nz_election`. The requested `P/verify.py` does not exist; the executable is `P/pipeline/verify.py`. “Done” distinguishes recorded verification from checks rerun here.

| Item | Status | Evidence |
|---|---|---|
| **30 Oct: `night` PASS** | Done, recorded | `docs/journal.md:2334,2392`: passing on deployed data and main. |
| `waterfall` PASS | Done, recorded | Same journal entries; `P/pipeline/verify.py:354` checks leaders, golden allocation and incomplete-input suppression. |
| Demo replay on `/night/` | Done, implemented | `P/pipeline/night.py:45-69` packages two demo observations; `P/runbook/night.md:82` documents selection. |
| 2017, 2020, 2023 archives on `/night/` | Done, recorded | `docs/journal.md:2334`; `P/runbook/night.md:16,82`. These correctly remain single **Final snapshots**, not fabricated timelines. |
| Timed illustrative replay | Done, implemented | `P/runbook/night.md:75-85`: 60x, pause/reset, ten-second endpoint, 2,851,211 votes and House 122. Local browser assertions: `P/tests/night_browser.py:74-100`. |
| Live-feed CORS/WAF probe from deployed origin | **Missing evidence** | Explicitly open at `docs/journal.md:2334`. Earlier evidence is curl, not browser fetch (`:1901`). `P/tests/night_smoke.py:5-27` validates local files only. |
| Dated fallback when feed fails | Partial acceptance | Packaged snapshots and last-good retention documented at `P/runbook/night.md:16-34,201-206`; deployed failure demonstration remains unrecorded. Actions transport supersedes direct browser XML (`intent/nz-election/plan-m3.md:58`). |
| **4 Nov: all evals green** | **Partial** | Eight executable checks exist; shell syntax passes. Historical individual PASS records exist, but no current all-eight run found. CI runs lint/pytest, not these scripts (`.github/workflows/ci.yml:19-29`). |
| `pages-home-bytes-live` eval | Runnable, network-dependent | `evals/pages-home-bytes-live/check.sh:7-12` fetches data, builds a pinned historical bundle and runs `all`. Not run here. |
| `pages-verify-polls-only` eval | Runnable, offline workload | `evals/pages-verify-polls-only/check.sh:5-9` creates temporary fixtures/site and runs `all`. |
| `polls-date-exception-revision` eval | Runnable, offline | `evals/polls-date-exception-revision/check.sh:7` starts its Python assertion check. |
| `polls-release-date-sort` eval | Runnable, offline | `evals/polls-release-date-sort/check.sh:5` starts injected-row parser assertions. |
| `social-classify-exclusion` eval | Runnable, injected transport | `evals/social-classify-exclusion/check.sh:7`. |
| `social-model-rotation` eval | Runnable, injected transport | `evals/social-model-rotation/check.sh:5`. |
| `social-query-length` eval | Runnable, offline | `evals/social-query-length/check.sh:6`. |
| `social-retry-budget` eval | Runnable, injected transport | `evals/social-retry-budget/check.sh:5` invokes `check.py`; usage and expected result in its `README.md:3-11`. |
| `verify.py all` PASS | Partial milestone coverage | Recorded PASS at `docs/journal.md:2334`. Current CLI lacks `campaign` (`P/pipeline/verify.py:381,390`); `all` skips absent night/waterfall families (`:438-440`). PR #75 remains unmerged in the latest record (`docs/journal.md:2401`). |
| Every scheduled workflow green three days running | **Missing complete evidence** | Daily successes recorded for 20-23 Oct (`docs/journal.md:2325`), but social failed on 22 Oct (`:1976`) and cron delays persisted (`:2299`). Later successes do not establish a complete three-day window (`:2307`). Scheduled workflows are daily, hourly and social-daily. |
| Social s197 freeze installed and tested | Done implementation; boundary probe passed here | `P/tests/test_social.py:109-114` tests six boundaries and no collection while frozen; `P/tests/test_night_operation.py:139-156` covers publication families and rollback/deploy guards. Actual window: 6 Nov 23:30 to 7 Nov 19:00 NZDT (`P/pipeline/deployment_guard.py:6-7`). |
| **6 Nov: runbook with 60x procedure** | Done, needs consolidation | `P/runbook/night.md:73-107` provides procedure and expected timing. Root operations guide does not link it; older text still says live operation is future work (`:47-50`). |
| Timed full replay against deployed site | **Missing evidence** | Existing browser harness builds localhost fixtures and advances a simulated clock (`P/tests/night_browser.py:35-44,84`). Actions rehearsal succeeded (`docs/journal.md:2251`), but that mode only produces artifacts (`P/runbook/night.md:218-222`). Neither proves the deployed timed rehearsal. |
| Rehearsal defects fixed or recorded | **Missing acceptance record** | No completed deployed rehearsal report found with timings, code/data SHAs, screenshots, browser logs and defect disposition. Required by `intent/nz-election/plan-m3.md:62`. |

Cheap verification output:
- `python3 -B P/pipeline/verify.py night --help`: exit 0; lists `night`, `waterfall`, `all`, `--data`, `--site`; no `campaign`.
- `bash -n` across all eval scripts: `PASS eval shell syntax (8 checks)`.
- In-memory `social.frozen()` probe: `PASS freeze boundaries (4 cases): [False, True, True, False]`.
- `uv run --offline ... --help` was blocked by cache permissions; direct Python worked.

Build next, in order:

1. **Close the deployed night acceptance gap.** Add a deployed-origin browser probe, separate from local smoke and injected fault tests; record exact URLs, browser/time, code/data SHAs, CORS failures and dated fallback. Files: new `P/tests/night_deployed.py`, `P/runbook/night.md`, `runbook/nz-election.md`. Proposed proof: `uv run --with playwright python P/tests/night_deployed.py --origin https://byronxlg.github.io --probe`. Preserve the approved Actions transport.

2. **Make Harden a repeatable release gate.** Land reviewed PR #75 first; add an eight-eval runner and scheduled-run history checker, then capture a complete three-day window. Reuse existing freeze tests. Files: `bin/nz-election-harden`, `P/tools/check_workflow_history.py`, `.github/workflows/ci.yml`, operations runbooks. Proof: `bin/nz-election-harden --data <bundle> --site <site>` plus focused `pytest -q P/tests/test_social.py P/tests/test_social_fix_round1.py P/tests/test_night_operation.py`. Require explicit campaign/night/waterfall PASS lines, not only `PASS all`.

3. **Automate and execute the deployed rehearsal.** Extend the deployed harness with real elapsed timing, pause/resume/reset, archive selection, final golden totals, request logging, fallback checks and both viewport captures. Files: `P/tests/night_deployed.py`, `P/runbook/night.md`, dated rehearsal report. Proposed proof: `uv run --with playwright python P/tests/night_deployed.py --origin https://byronxlg.github.io --rehearse --speed 60`. Record defects and actual Actions/Pages durations; artifact-only rehearsal cannot close this row.