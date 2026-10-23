# PR #61 fix-1 (fresh review review-nz-election-parties-page)

Two items, same branch, same worktree. Tests on main at the merge base are protected; tests this branch added move with it. Nothing weaker to pass.

1. Picker wraps at phone width. `parties.css` sets `white-space:nowrap` but the chips inherit `nav { flex-wrap:wrap }` from the shared CSS, so seven chips wrap into several rows at 360/390. pages/parties.md wants one row (horizontal scroll if it overflows). Set `flex-wrap:nowrap` on the picker (scoped to the picker, not every nav) with overflow-x auto, and keep each chip's target at least 24 px. Add a check that fails on the current HEAD: at 360 every chip in the picker has the same top offset.

2. Party snapshot validators accept malformed provenance (`pipeline/snapshots.py` around 447). A probe accepted: an unrelated `example.com` list source, an invented licence, a null source locator, copied policy-text fields, and a Policy.nz URL with an empty party slug. Enforce:
   - list snapshot: `source_url` is the EC party list PDF origin (vote.nz or elections.nz host, https); policy-links: `source_url` on policy.nz.
   - licence is one of the licence strings the existing snapshots accept (reuse that check, do not invent a new list).
   - source locator present and non-empty wherever the other snapshots require one.
   - policy-links rows are links only: any key outside the allowed set (party_id, url, source_url, licence, locator, retrieved_at, or whatever the current committed file uses) is rejected, so no policy text can be copied in.
   - policy URL has a non-empty slug after `/parties/` and nothing that is not a slug.
   One rejection test per case, each failing on the current HEAD. The committed snapshot files must still validate.

Not changing: the 44 px label spacing in `home_charts.py:113` stays (labels are now links and need separated targets; supervisor accepts the 290 to 378 px chart height, reasoning on the PR).

Done when: `uv run --with pytest pytest -q product` passes, `.venv/bin/python bin/lint` says lint ok, `PYTHONPATH=. uv run python -m product.nz_election.pipeline verify all` (or the repo's verify command) PASS, and last.md lists each new test with the HEAD it fails on. Commit in the worktree, do not commit last.md, do not push.
