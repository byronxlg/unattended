Committed `f787d3e` on top of `7241c10`. No push or rebase.

Diff: **6 files, 131 insertions, 21 deletions**: pipeline `{publish,candidates,verify}.py` and tests `{test_contracts,test_candidates,test_electorates}.py`.

- Source additions now advance; removals and timestamp regressions retain published data. Proven by `test_baseline_source_set_advancement`.
- Missing-baseline verification uses controlled present/missing data. `test_verifier_accepts_present_mangere` proves file 21 can arrive without breaking verification.
- Reviewed claims accumulate without replacing EC provenance. Extended `test_conflicts_preserved` checks repeated claims, all provenance and “Unresolved” rendering; `test_agreeing_claims_keep_official_provenance` covers agreement alone.

Assertions strengthened: the permanent Māngere-missing assertion became both present and controlled-missing checks; the single-conflict check became repeated-claim checks across three fields. `test_required_baseline_captures` is unchanged. Regressions reproduced on the original code before fixes.

Verification:
```text
uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS candidates: 71 electorates
PASS electorates: 71 pages
PASS all
uv run product/nz_election/pipeline/daily_refresh.py --out artifacts/nz-election/data
PASS refresh: daily bundles
uv run product/nz_election/pipeline/build.py --data artifacts/nz-election/data --out site/nz-election
PASS build: 77 routes
uv run --with pytest pytest -q
1 failed, 343 passed in 88.84s (0:01:28)
bin/lint
lint ok (281 text files)
```

Sole failure: `test_required_baseline_captures`, missing `candidate-votes-by-voting-place-21.csv`.