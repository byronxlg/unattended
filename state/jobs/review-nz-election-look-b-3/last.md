Verdict: **request changes**.

Critical: None.

Important:

- [content_checks.py:72](/Users/byron/repos/unattended/.worktrees/nz-election-look-b/product/nz_election/pipeline/content_checks.py:72): `EMPTY_MODULE` is trivially satisfiable. Adding only `<svg aria-describedby="source-map"></svg>` after the old empty closest-seat heading makes both absence and landmark checks pass. Require actual content; reject empty graphics and hidden-only content.
- [content_checks.py:55](/Users/byron/repos/unattended/.worktrees/nz-election-look-b/product/nz_election/pipeline/content_checks.py:55): `EMPTY_PROVENANCE` counts script text as provenance. Replacing the old Port Waikato empty anchor with `<span id="source-baseline-2023"><script>0</script></span>` passes the full landmark page check. Exclude non-content descendants and test this bypass.

Nit: None.

Verified:

- All 71 electorate maps have legends and 71-row exact-value tables.
- Port Waikato boundary sentence and source target are fixed.
- All 43 poll sample cells render empty when absent, in both source modes.
- Saved pre-fix builds fail all three new gates as intended.
- Fix commit changes no main-era assertion beyond permitted `test_average.py`; the changed map assertion was branch-added.
- No new visual regression found in the six inspected home, Nelson and Port Waikato screenshots.

Commands, using `.venv/bin/python` because `uv` cache access is blocked:

- `-m product.nz_election.pipeline.landmark_checks /tmp/look-b/after/nz-election`  
  `PASS landmarks: 79 routes including client-rendered tables`
- `product/nz_election/tools/check_visible_text.py /tmp/look-b/after/nz-election`  
  `PASS visible text: 79 routes, no whitespace-free run over 200 characters; absent-text gate passed`

Limitation: PR comments could not be retrieved; reviewed against the supplied first-review summary. No files changed.