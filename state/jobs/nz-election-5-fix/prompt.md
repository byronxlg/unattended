# Follow-up: nz-election increment 5, screenshot harness fails on SVG anchors

Same worktree `.worktrees/nz-election-5`, now rebased onto main (your two commits are 7bd1091
and the restore commit was dropped as already on main). The supervisor ran the host-only steps:

- `geo_reference.py` produced both reference companions; committed as
  `fixtures/stats-nz/{general,maori}-2025.reference.json` (HEAD). Do not regenerate or edit them.
- `verify.py geography`, `verify.py all`, `refresh.py --fixtures`, `daily_refresh.py`, `build.py`
  all printed their PASS lines on the host.
- `uv run --with pytest pytest -q`: 288 passed (test_reference_capture_required now passes).
- `bin/lint`: ok (captures under fixtures/ are now exempt on main).

The screenshot run fails before any image is written:

```
uv run --with playwright python product/nz_election/tests/screenshots.py --site site --out artifacts/nz-election/screenshots
  File ".../product/nz_election/tests/screenshots.py", line 206, in main
    text = check_page(page, url, site, origin)
  File ".../product/nz_election/tests/screenshots.py", line 63, in check_page
    parsed = urlsplit(href)
TypeError: unhashable type: 'dict'
```

Cause: `check_page` collects `a[href],link[href]` with `els.map(e=>e.href)`. On an SVG `<a>`
(your index map links every path to its directory anchor) `e.href` is an SVGAnimatedString,
serialised as `{baseVal, animVal}`. The page with the map is the first page where this happens.

## Ask

Fix the link collection so SVG anchors are resolved to absolute URLs and checked like HTML
anchors (resolve the attribute against `document.baseURI`; do not skip SVG anchors, do not
narrow the selector). The check must still assert BAD_PREFIX, BROKEN_LINK and the fragment-id
check for every map link. Change nothing else in the harness unless the run exposes another
host-only failure, in which case fix the harness, never the product to suit the harness, and
name each change in the report. You cannot launch Chromium in your sandbox; keep the edit
minimal and self-evidently correct, and run `uv run --with pytest pytest -q` (expect 288
passed) and `bin/lint` before committing. Commit in the worktree; never push.

Report: the diff of screenshots.py in full, the test count, and any departure.
