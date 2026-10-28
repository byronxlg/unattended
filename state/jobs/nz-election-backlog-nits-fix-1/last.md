Committed `715304f`; not pushed.

- `funding_page.py`: home headline now consumes `funding_totals()`.
- `test_funding_totals.py`: compares actual `feed()` data with ranking data and verifies shared computation.
- Real-snapshot visible output unchanged. No main tests edited.

Regression evidence: **1 failed, 5 passed at `80235df`; 6 passed after fix**, recorded in uncommitted `last.md`.

Required verification:
```text
5 failed, 86 passed, 3053 deselected in 88.43s
lint ok (1348 text files)
```

All failures are sandbox-denied Chromium launches:
- `test_phone_rendered_type_and_targets[map/trend/header]`
- `test_funding_party_fragments_without_javascript`
- `test_night_design_browser`

Browser verification remains outstanding.