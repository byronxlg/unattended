Committed `91dbd4f`; not pushed.

Added tests:

- `test_svg_budget_css_strings_escapes_and_comments`
- `test_svg_budget_rejects_svg_data_uris`
- `test_svg_budget_ignores_non_svg_data_uris`

CSS is now tokenized before URL resolution. Both reviewer probes count **6 bytes**. SVG data URIs, percent-encoded or base64, are rejected with `SVG_DATA_URI_NOT_BUDGETED`; non-SVG data URIs are ignored.

Electorates page total: **284,316 bytes**, unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests
225 passed in 43.00s

git diff ec78040 --stat
 product/nz_election/tests/svg_budget.py     | 118 ++++++++++++++++++++++++++++
 product/nz_election/tests/test_geography.py |  42 ++++++++++
 2 files changed, 160 insertions(+)

uv run product/nz_election/pipeline/verify.py all
PASS polls
PASS thresholds
PASS provenance
PASS pipeline
PASS coalitions
PASS geography: 64 general, 7 Māori
PASS all

bin/lint
lint ok (254 text files)
```

No removed lines. Product code, fixtures, assertions, and budgets unchanged.