Verdict: **accept**, based on code, inspected screenshots and supplied host results.

- **Critical:** none.
- **Important:** none.
- **Nit:** none.

390×844 question test, read from the screenshot:
1. Government: 67 seats, three above the 64 needed.
2. Labour and National unchanged since 17 July.
3. Enrol by 25 October; advance voting 26 October; election day 7 November.

Fixes confirmed:
- `pipeline/home.py:204`: Q2 appears above the fold.
- `pipeline/snapshot_views.py:99`: 26×26 hex targets; Māori electorate label added.
- `tests/test_home_defects.py:71`: market test reads rendered Methods HTML, requires four rows and retains proposition assertions.
- `pipeline/home.py:375`: one electorate-directory action.
- `web/styles.css:9`: Methods market compaction; unchanged 844px gate passes per host evidence.
- `web/styles.css:10`: candidate-record links receive a 48px minimum at every width.
- `web/styles.css:11`: directory uses the full desktop list column, confirmed visually.

Existing thresholds in `screenshots.py`, `home_checks.py` and `market_checks.py` remain unchanged versus `de9a7c2`; `market_checks.py` is unchanged entirely.

Read-only replay of the directory regression:
```text
801c204 FAIL HOME_PICKER_DIRECTORY_LAYOUT
f2adca9 PASS HOME_PICKER_DIRECTORY_LAYOUT
```
All three built stylesheets match HEAD.

Limitations: PR comments were inaccessible, so review coverage follows your enumerated findings. Local `verify all` could not create a temporary directory; browser verification relies on your supplied host passes. No files changed.