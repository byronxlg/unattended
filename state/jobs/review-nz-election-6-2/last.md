Read `REVIEW.md` and `git diff 7241c10..HEAD -- product ':!product/nz_election/fixtures'`: **6 files, 136 insertions, 22 deletions**. No changes made; no approval given.

**Important: empty previous source set still breaks publication.**  
`product/nz_election/pipeline/publish.py:92` compares acquisition timestamps before reaching the corrected subset/superset checks at lines 96-99. An empty source set has `fetched_at=None`. Adding its first source raises instead of publishing.
Reproduction: construct an empty `electorate-polls-v1` envelope with `export.envelope([], [], ...)`, then a sourced envelope. Both pass `validate_envelope`; compare their `success_order(...)` values as line 92 does.
Observed output:
```text
empty electorate-polls envelope: valid; fetched_at= None
TypeError: '>=' not supported between instances of 'NoneType' and 'str'
```

Checks and evidence:

1. **Publication:** read-only execution of the actual comparison block produced `add: keep=False`, `drop: keep=True`, `drop+add: keep=True`, `reorder: keep=True`. Same IDs/timestamps with changed URLs or hashes retain existing bytes on a generation tie and publish with a later generation. These metadata changes are not source-set changes.
   Coverage gap at `tests/test_contracts.py:288-299`: only `add` switches to ID 99. `add-regressed` appends existing ID 21, so it now tests regression without source growth. Duplicate source IDs survive validation and collapse in the comparison dictionaries.

2. **Baseline:** `pipeline/verify.py:190-196` and `tests/test_electorates.py:87-98` check present Auckland Central data and explicitly remove candidate votes for the missing case. Search found no remaining assertion requiring Māngere/file 21 to be absent. Read-only capture validation and rendering probes returned:
   ```text
   captures: 111 candidate CSVs: 72
   present/controlled-missing detail: PASS
   ```
   Presence uses real fixtures; absence is explicitly controlled.

3. **Candidate claims:** `tests/test_candidates.py:51-77` covers agreement followed by disagreement; lines 107-120 cover agreeing claims retaining EC provenance. Running those function bodies without pytest, plus three-claim permutations across six fields, returned:
   ```text
   direct candidate regression tests: PASS (4)
   three claims, all order permutations, six fields: PASS (36)
   ```
   Accumulation at `pipeline/candidates.py:104-128` retained claims and unresolved status across those orders.

4. **Test discipline:** requested test stat returned **3 files, 100 insertions, 8 deletions**. `git show f787d3e -- product/nz_election/tests` reveals three replaced assertions beyond the permitted alignment changes: two candidate assertions replace literal `'CHANG, Johan'` with captured `original` and expanded claims; one replaces the Māngere generated-page assertion with controlled rendering assertions. Behavioral coverage remains, but the literal-name and generated-Māngere-page checks are removed, so the strict “no existing assertion removed” requirement is not met. `15a30be` changes count 110→111 and the add-case identity 21→99, adding an absence assertion; no other removals.

5. **Full verification unavailable:** both `uv run --with pytest pytest -q` and `uv run product/nz_election/pipeline/verify.py all` exited 2:
   ```text
   error: Failed to initialize cache at `/Users/byron/.cache/uv`
     Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
   ```
   Therefore neither “344 passed” nor “PASS all” was independently confirmed. Supplemental probes used `.venv/bin/python -B -c`; no filesystem writes.

No security findings or style nits. Open question: whether the supervisor accepts the assertion replacements under the stated test-discipline requirement.

Important findings: 1