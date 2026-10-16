# Geography and directory

`geography.py registry` generates the committed 71-row registry from validated
captures and reviewed correspondence. Existing slugs are stable ASCII identifiers;
a future display-name change must retain the committed slug. IDs namespace the
Stats NZ code, including its leading zeroes. Missing correspondence displays
"Comparison unresolved".

`daily_refresh.py --out artifacts/nz-election/data` ingests only committed inputs.
The geography family consists of `electorates`, `general-2025` and `maori-2025`,
each with JSON and CSV siblings. Geometry downloads are FeatureCollections with
envelope foreign members. CSV includes `geometry_json`. Official numeric property
values outside coordinate arrays are exported as decimal strings, preserving their
values while keeping the coordinate-only float exception. Source property names
are retained. Every registry field has a locator; derivations include capture and
reviewed configuration hashes. No source documents or identity captures are served.

The offline daily ingestion time is distinct from source acquisition. Status becomes
overdue after 36 hours. A handled validation failure retains the entire previous
family. Publication accepts `--family hourly|daily` and merges only that owner's
files, then regenerates status, licences and inventory. No daily workflow ships here.

## Geometry and references

Projection: spherical Lambert cylindrical equal-area, Earth radius 6,371,008.8 m,
central meridian 173 degrees east, standard parallel 41 degrees south. Longitude
is unwrapped to within 180 degrees of the central meridian. Areas subtract holes.
Reference interior points use horizontal scan lines between vertex heights, tested
against outer rings and holes. SVG coordinates are projected and rounded to one
decimal display unit; rings and components are never dropped.

Run `uv run product/nz_election/pipeline/geo_reference.py <full.geojson> --out
product/nz_election/fixtures/stats-nz/<kind>-2025.reference.json` on the host with
full-detail input outside this repository. The tool prints its input SHA-256.
Commit the independent companions and manifest derivation notes before review.
Tests compare IDs, component counts, interior-point containment, extents within
250 projected metres (the captures use 0.001-degree simplification) and aggregate
area within 1% per layer. Missing companions fail the dedicated acceptance gate;
no simplified capture is substituted as its own reference.

## Enforcers

- Registry identity/search: `test_slug_registry_and_macron_search`.
- Correspondence provenance/totals: `test_correspondence_evidence`.
- Geometry validity and reference fidelity: `test_geojson.py`, `verify.py geography`.
- Linked titles, rings and whole-page/outline budgets: `test_svg_links_titles_and_holes`,
  `test_svg_page_budget`. Index: 284,316 bytes; largest outline: 15,339 bytes.
- No-geometry fallback: `test_missing_geometry_is_unavailable`; module allowlist:
  `scripts.py`; static directory: `verify.py geography`.
- Party identity evidence: `test_party_colour_evidence`; existing strip/explorer
  read the reviewed configuration values.
- Family schemas/atomicity, unchanged hourly files and publication union:
  `test_contracts.py` plus existing publication/race tests.
- Capture inventory count: only the assertion changes from 11 to 25 in
  `test_capture_manifest`.

Host screenshot acceptance remains required. The script produces 12 baseline and
12 additional images (24 total), including both map layers at phone and desktop
sizes. Radio selectors work without JavaScript. Search is the only JS enhancement.
Directory links provide 44px equivalents for tiny map shapes; selection uses a
pattern, strong outline and the named directory entry. Blue focus has white separation.

## Dispatch corrections and remaining acceptance

The supplied branch did not contain increment 4. Commit `6338a9d` restores its
product files from locally available `361760c`, retaining all supervisor captures
and reviewed configuration. A fixed-metadata comparison verifies that all 11 hourly
bundle files remain byte-identical to that increment.

Sandbox Chromium launch fails at macOS MachPortRendezvous with permission denied;
no screenshot inspection is claimed. `bin/lint` also reports pre-existing characters
in immutable captures: `party-identity/grn.html:6071` and `opp.html:303`.
The captures are not edited and the lint check is not weakened.
