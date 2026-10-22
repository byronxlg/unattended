# Fix: social daily fails when Jev rotates jev-latest (incident 2026-10-22)

Goal: the social daily must not fail because the upstream moved its default model.

What happened: run 39792706334 (22 Oct, by hand) reserved and spent the day's credits, then all 39
classification batches failed `check=model` (SOCIAL_CLASSIFICATION_FAILED, http 200) and the run ended
SOCIAL_UPSTREAM_FAILED. Cause, probed on the host 16:4xZ 22 Oct: `product/nz_election/pipeline/social.py`
sends `model='jev-latest'` (line ~289) but `classification_response` accepts only `MODEL_VERSIONS`
(line 46: `jev-1.13.0` plus fixture/test). `jev-latest` now answers `jev-1.14.0`. A request naming
`jev-1.13.0` is still served and answers `model: 'jev-1.13.0'`.

Invariant: the version requested and the versions accepted come from one place, so a rotation of the
upstream default cannot fail a day; the model version actually used stays recorded in the aggregate
(`model_versions`) and the strict `model` check stays (nothing weaker). You choose the shape (pin the
request to the accepted version is the obvious one).

Read first: AGENTS.md, product/nz_election/pipeline/social.py, its tests (test_social*.py),
evals/social-classify-exclusion/ (shape of an eval).

Do:
1. The fix in social.py.
2. A regression test with injected transport: a transport that answers `jev-1.14.0` to `jev-latest`
   and echoes a pinned version otherwise; the refresh succeeds. It must fail on main.
3. An eval `evals/social-model-rotation/` in the same shape as the existing social evals, failing on main.
4. One runbook line (runbook section on social) on how to move to a new Jev version deliberately.
Tests on main at the base sha are protected except where the requested model string is pinned; those
may move with the fix. Do not edit workflows.

Done when, in this worktree:
- `uv run --with pytest pytest -q product/nz_election` passes (report the count);
- the new eval passes here and fails on main (show both);
- `bin/lint` prints ok.
Commit on the branch, do not push. Write last.md with the commands and outputs.
