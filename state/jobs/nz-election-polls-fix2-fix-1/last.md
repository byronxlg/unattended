Committed `1714c77`; not pushed. `last.md` remains uncommitted.

Rewritten assertions:
- Altered or removed exceptions retain August 8-11 fieldwork with `kind='release-date'`.
- Matching exceptions use `kind='documented-exception'`.
- Before-start and bound-plus-one dates raise `invalid_dates`, preserving private date details and public locator.
- The incident case uses an out-of-bound sort and still pins `table:15/row:19`.

Verification:
```text
evals/polls-release-date-sort/check.sh:
PASS release-date row parsed

evals/polls-date-exception-revision/check.sh:
PASS exception row parsed on revision 9999999999

Saved live-file parse:
Live revision 1381086195: rows=44, Freshwater 2026-10-19 exists=True

uv run --with pytest pytest -q product/nz_election:
698 passed in 290.44s (0:04:50)

bin/lint:
lint ok (508 text files)
```

All other baseline tests and fixture bytes remain unchanged. No open questions.