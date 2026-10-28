Committed `dd3b4dd`, not pushed.

- Added party summaries, jump links and JS-free fragment expansion, preserving all 146 returns and EC provenance.
- Tightened desktop funding layout.
- Added data and browser regression tests; existing tests unchanged.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "funding or design"
5 failed, 73 passed, 3012 deselected in 89.71s (0:01:29)

bin/lint
lint ok (1281 text files)
```

All failures were Chromium launch permission denials:
- `test_phone_rendered_type_and_targets[map]`
- `test_phone_rendered_type_and_targets[trend]`
- `test_phone_rendered_type_and_targets[header]`
- `test_funding_party_fragments_without_javascript`
- `test_night_design_browser`

Screenshots and pixel measurements require host verification. Details recorded in uncommitted `last.md`.