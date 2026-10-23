Verdict: **request changes**.

- **Important** · `product/nz_election/pipeline/night.py:160`: Mode validation checks label agreement, not source provenance. Keeping one demo observation and changing its row and sequence modes to `Final snapshot` passes `prepare()` and `validate()` in an in-memory probe. Simulated results can therefore publish without their mandatory demo label. Bind permitted modes to source/derivation provenance.

- **Important** · `product/nz_election/pipeline/xml_parser.py:110`: Percentage validation is skipped when summed votes are zero. Setting every 2023 party vote to zero while retaining nonzero percentages and seats is accepted as valid votes `0`, House `122`. Reject this contradictory result with `XML_TOTAL`.

- **Important** · `product/nz_election/pipeline/verify.py:331`: Night verification builds fresh fixtures instead of checking the supplied artifact. A valid `--data` bundle without any night family can pass generic validation, then receive `PASS night` from an unrelated temporary build. Apply the night smoke checks to supplied data.

- **Important** · `product/nz_election/pipeline/xml_parser.py:44`: Empty count elements fail as `XML_FIELDS`, whereas other malformed count tokens fail as `XML_COUNT`. Probes confirmed `<votes/>` and whitespace produce `XML_FIELDS`. This violates the documented all-malformed-counts error contract; current tests exercise `count()` directly and miss the XML path.

No page code changed. Existing tests were not weakened; only the capture-count pin changed. Atomic directory exchange remains intact; no partial-publication defect found by inspection.

Read-only probes confirmed archive totals: 2017 `2591896 / 120`, 2020 `2886420 / 120`, 2023 and replay `2851211 / 122` (votes / House).

`uv run --with pytest pytest -q product` could not run:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open file .../sdists-v9/.git:
Operation not permitted (os error 1)
```
No files edited. Full-suite verification remains outstanding.