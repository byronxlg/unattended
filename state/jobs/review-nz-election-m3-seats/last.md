Verdict: **request changes**.

Critical: None found.

Important:

- `product/nz_election/pipeline/night_electorates.py:81`: SVG clips all seven Māori electorates. Their layout x=15 produces polygon coordinates 451-479, outside the viewBox’s 450-wide boundary. Expand the viewBox and verify every electorate remains visible and selectable.
- `product/nz_election/pipeline/xml_parser.py:157` and `web/night-parser.mjs:102`: Reported ties discard their zero margin. Reproduced 100-100 with all places counted: `leader=None, margin=None, status='final'`. Consequently, `night_electorates.py:58` displays “Not yet reported” for a known margin. Preserve zero for reported ties.
- `product/nz_election/web/night.css:2`: Interactive hexagons render approximately 17×18 px, with closely spaced targets. Increase target size or provide an adequately sized selection control. The existing screenshot target check explicitly excludes SVG links.

Nit:

- `product/nz_election/runbook/night.md:88-94`: Stale instructions still claim 20 images and no electorate map/table, contradicting the new 44-image registry and implementation.

Verification: read-only test subset produced **`38 passed, 2 deselected in 0.31s`**. Final bundle validated; in-memory ABSENT_TEXT, backing-row and landmark checks passed. Freeze notice remains intact. Replay code makes no feed requests. Detail parity executes independent implementations, although positive-count cases deserve coverage. Edited pre-existing checks retain their contracts.

Limitations: GitHub was unreachable, so PR-body claims remain unchecked. Full pytest, verifier and lint commands failed on denied uv cache access. No screenshots were present to inspect, so the five-second question test and visual acceptance remain unverified.