Committed `fa330051dfbf36e86817e93f4e2378badd0bb6cf`. Not pushed.

- Moved portrait credits below answers in `parties_page.py`; retained authors, licences and accessible references. Processing notes remain in Methods/snapshots.
- Updated `styles.css`, `parties.css` and `DESIGN.md` to keep values intact while allowing stacked rows.
- Added regression tests; attribution test fails on base `3dcc564`.
- Updated `test_parties_captions.py` and `test_parties_refine.py` because they explicitly required the removed processing copy. Funding files untouched.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "parties or home or design"
11 failed, 219 passed, 2849 deselected in 144.08s (0:02:24)

bin/lint
lint ok (1175 text files)
```

All 11 failures were sandbox-denied Chromium launches: map/trend/header, four home handovers, two retirements, night design, parties picker.

Outstanding: screenshots and visual review blocked by `MachPortRendezvousServer: Permission denied (1100)`. Details in uncommitted `last.md`.