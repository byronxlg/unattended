Committed `3dcc564`. Not pushed.

- Added shared, data-derived EC credit to the home funding summary.
- Confirmed the new regression test fails on `1e6cdc5` and passes after the fix.
- Adjusted desktop donor-column space and phone amount/count hierarchy.

Requested pytest command:
```text
10 failed, 148 passed, 2919 deselected in 147.99s
```

All failures were sandbox-denied Chromium launches:

- `test_phone_rendered_type_and_targets[map, trend, header]`
- `test_browser_handover[absent, zero, complete, recovery]`
- `test_retirement_browser[cached-after-stop, waiting-after-stop]`
- `test_night_design_browser`

`bin/lint`: `lint ok (1174 text files)`.

Visual review remains blocked. Details recorded in uncommitted `last.md`.