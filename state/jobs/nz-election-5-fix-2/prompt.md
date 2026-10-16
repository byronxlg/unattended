# Follow-up 2: nz-election increment 5, fresh review findings

Same worktree `.worktrees/nz-election-5`, HEAD e8d1d77, on PR #13 (CI green). A fresh-context
review found four items; the supervisor confirmed three as Important and one as Minor. Each
item below names the invariant and where it is enforced today. Choose the shape yourself, then
check your diff against every consumer of the shape you touch. Read first: `AGENTS.md`,
`intent/nz-election/plan-m2.md` lines 36 to 42 and 160 to 175, `pipeline/export.py`
`validate_bundle`, `pipeline/publish.py` lines 40 to 120, `pipeline/refresh.py` around 106,
`pipeline/daily_refresh.py`, `tests/test_geography.py`, `tests/test_geojson.py`.

## 1. Important: a registry or config correction must not invalidate last-good geography

Invariant (plan-m2 line 40, spec requirement 15): families fail and retain independently; a
last-good bundle on the data branch stays valid until its own family is regenerated. Today
`validate_bundle` (export.py:287 to 294) requires the existing bundle's registry and config
input hashes to equal the current checkout's `config/electorates.json` and
`config/electorate-correspondence.json`. `publish.py:81` and `refresh.py:106` call it on the
bundle already on the data branch, so one merged registry note raises `REGISTRY_MISMATCH` and
blocks the polls publish as well. Separate snapshot integrity (the bundle is internally
consistent with the hashes it records) from current-input validation (this checkout would
regenerate geography). The latter belongs where geography is produced, not where an existing
bundle is read. Regression tests: an existing valid bundle plus a changed registry note in
memory still validates and publishes polls; a freshly generated geography family against the
current config still records the current hashes; a bundle whose recorded hashes do not match
its own bytes is still rejected.

## 2. Important: reference companions are hash-pinned like every capture

Invariant (plan-m2 line 40, `test_capture_manifest`): every fixture the tests depend on has a
manifest entry and is loaded through `captures()`, so a byte change raises
`CAPTURE_HASH_MISMATCH`. `fixtures/stats-nz/{general,maori}-2025.reference.json` have no entry
and `test_geojson.py:57` reads their bytes directly. Add both to the manifest (record how they
were produced: `geo_reference.py` on the host from the full-detail files, input sha256 as the
companion itself records) and load them through `captures()`. Do not regenerate or edit the
companion bytes. `test_capture_manifest` count moves from 25 to 27; say so in the report.

## 3. Important: the page budget measures what the rendered page needs

Invariant (plan-m2 line 172, decision 7): `test_svg_page_budget` measures all inline and
linked SVG bytes required by the rendered electorates page, both layers included, in
uncompressed UTF-8, against `index_svg_max_bytes` (300,000), and every detail outline against
`outline_svg_max_bytes` (30,000). Today it measures one `g.svg()` call, so a page that
embedded the map twice (the reviewer's probe: 568,632 bytes) would pass. Measure from the
output of the page builder (`electorates_page` or the built `site/` route), summing every
inline `<svg>` and every linked `.svg` the page references. Keep the outline gate.

## 4. Minor: Python and JS produce the same search key for the same input

Invariant (plan-m2 line 166): the precomputed `data-search-key` (geography.py `search_key`,
NFD, strip marks, casefold, collapse whitespace) and the JS query normaliser
(`web/electorates.mjs:5`, NFD, strip marks, toLocaleLowerCase) agree. They diverge on
characters where casefold and lowercase differ (ſ, ß). Make them agree in both directions and
add a parity test that feeds the 71 names plus a few probes (macrons, doubled spaces, ſ, ß)
through both (Node is available for the JS side as in increment 4's parity test).

## Rules

Existing tests change only by addition; do not loosen any assertion or raise any budget.
Keep the increment 4 files untouched. Commit in the worktree; never push.
Definition of done, run and quote the output:

```
uv run --with pytest pytest -q            # all passed, count stated (288 plus your additions)
uv run python product/nz_election/pipeline/verify.py all   # PASS lines as before
bin/lint                                  # ok
```

Report: per item, the files changed, the regression test names, and any departure from the
invariant as stated with the reason.
