**Verdict: request changes.**

**Critical:** None found.

**Important:**
- `product/nz_election/pipeline/snapshots.py:161`: Correction values are not validated. In-memory probes confirmed `load('candidate-reconciliation-2026')` accepts `after` values of `""`, `null`, `[]`, `{}`, integers, floats and huge integers for a name correction. Validate `before` and `after` according to `field`, and add rejection tests. This violates the malformed-input requirement.

**Nit:** None.

Checks completed:

- Eight name corrections match the reconciliation’s EC spelling exactly: Sales, Turner, Wellman, Leavasa, Stobo, Arneil, Carter and Stephens. Their spellings also match the [official EC party-list PDF](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf).
- Both affiliation corrections match the recorded EC entries: Kane, row 207; McIntosh, row 231. Both become Independent. Independent verification against the XLSX was blocked by network/content-type restrictions.
- Exactly 60 names and two affiliations changed. No list rank, MP flag or photo changed. All 50 previously omitted ranks remain omitted.
- Boundaries: 71 features, exact registry/hexmap slug coverage, 316,359 bytes. Licence, attribution, source URLs and simplification recorded; explicitly excludes legal-boundary/address-lookup use.
- EC-derived content contains facts and provenance, with no copied source prose found. Join rules and explicit exceptions are recorded; no fuzzy matching found.
- Loaders are offline; all three snapshots load. Existing tests remain untouched, including against `d55b42e`.

Verification limits: `uv run --with pytest pytest -q product` and `bin/lint` both stopped with `Failed to initialize cache … Operation not permitted`. PR-body retrieval also failed. No files changed.