Page plan: intent/nz-election/pages/electorate.md

Goal: answer electorate question 3 ("What do these candidates stand for?") on every electorate page that has a real
destination. Today 0 of 71 electorate pages show the Policy.nz link: `policy_link()` in
product/nz_election/pipeline/electorate_pages.py:82 looks up `electorate_slug`, but snapshots/policy-links.json holds
only seven party records (and every party record's `source_url` points at the Labour page, a provenance defect).

Read first: intent/nz-election/pages/electorate.md (answer 3, data 3: fetch once, link only, no ingestion),
product/nz_election/pipeline/electorate_pages.py, product/nz_election/pipeline/snapshot_views.py and the snapshot
validator for policy-links (grep policy-links under product/nz_election), the electorate page tests, AGENTS.md.

Do:
1. Find Policy.nz's real 2026 electorate destinations (the site's own electorate index or sitemap). Record one entry per
   electorate you confirmed returns HTTP 200 and names that electorate: `electorate_slug` (our slug), `url`,
   `source_url` (the index page you found it on), `retrieved_at`, licence line as the party records. Never construct a
   URL from a pattern without fetching it; an electorate you cannot confirm is omitted and listed in last.md.
2. Fix the party records' `source_url` to the page each was actually read from.
3. Keep the validator strict (it may need to accept the electorate record shape; nothing weaker for existing records):
   duplicate slugs, unknown slugs (not one of our 71) and non-policy.nz hosts fail.
4. A test that fails on main: a populated electorate page renders the link, inside the first section after the
   candidate cards per the plan's page order, and a slug absent from the snapshot renders nothing (no "not available"
   text; the absent-text gate applies).
5. If Policy.nz has no electorate-level pages at all, stop and say so in last.md with the evidence; do not substitute
   party links on electorate pages without that being decided.

Tests on main at the current base are protected; tests that pin the policy-links record count or shape move with the
registered set, nothing weaker.

Done when, in the worktree:
- `uv run --with pytest pytest -q product/nz_election/tests/` passes (report the count), and the new test fails with
  electorate_pages.py and snapshots/policy-links.json from origin/main.
- `bin/lint` prints `lint ok`.
- last.md states N of 71 electorates linked, the omitted list with reasons, and screenshots at 390x844 and 1280x800 of
  two electorate pages (one linked, one omitted) under artifacts/ (not committed), showing the link within one scroll.
Commit in the worktree; do not push.
