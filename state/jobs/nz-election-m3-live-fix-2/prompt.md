# nz-election-m3-live fix-2 (PR #65, fresh review request changes)

The fresh review of PR #65 (727561e) found two Important defects in `pipeline/night_live.py`.
Fix both on change/nz-election-m3-live. This is a fix job: tests on main at the PR base may not be
weakened or edited; tests this branch added may move with the code.

1. night_live.py:182, deployment recovery lost across runner restarts. If data publication
   succeeds but the Pages deploy fails, the successor run sees `unchanged`, its `pending_sha` is
   empty, and it never retries the deploy; unchanging final results can stay unpublished. Make
   the deployed state recoverable from durable evidence (persist it with the data, or reconcile
   the published data SHA against the deployed SHA at the start of each run). Invariant: a run
   that finds published data newer than the last confirmed deploy deploys it, whatever happened
   to the runner that published it.

2. night_live.py:143, unchanged acquisitions never update retrieval freshness. Four successful
   cycles produced changed, unchanged, unchanged, unchanged; at 06:15 the published retrieval time
   was still 06:00 and the browser reported stale. Freshness (last successful acquisition) and
   result change (whether to redeploy) are separate contracts: a successful unchanged fetch must
   advance the retrieval time readers see, without turning every cycle into a full results
   redeploy unless that is the only way; say which you chose and why (cost in Actions minutes per
   hour on the night).

Definition of done:
- A regression test for each item that fails on 727561e and passes on your commit (name them in
  last.md and show the failing output on 727561e).
- `uv run --with pytest pytest -q product/nz_election/tests/test_night_page.py product/nz_election/tests/test_night_operation.py` passes.
- `uv run product/nz_election/tests/night_browser.py <out>` exits 0 if Chromium starts; if not,
  say so and the supervisor reruns it on the host.
- `bin/lint` ok. Commit on change/nz-election-m3-live; do not commit last.md or artifacts/.
