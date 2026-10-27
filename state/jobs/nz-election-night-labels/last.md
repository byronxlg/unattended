# Night replay labels

Files changed:
- product/nz_election/pipeline/night_page.py: distinguish final-count coverage from live update clocks; use shared bloc labels.
- product/nz_election/pipeline/home_graphics.py: export BLOC_NAMES.
- product/nz_election/pipeline/home.py: consume BLOC_NAMES without changing home wording.
- product/nz_election/tests/test_night_page.py: behaviour test across historical archives and illustrative replay frames.

Before and after:
- "Results cover 100.0 percent of voting places, updated 00:00." becomes "Results cover 100.0 percent of voting places; 2023 final count."
- Illustrative final-frame coverage adds "; 2023 final count, frame 3 of 3." Only live preliminary reporting retains "updated HH:MM". Full dated source timestamps remain in provenance.
- "Labour, Green<br>and Māori" becomes "Opposition".
- "National, ACT<br>and NZ First" becomes "Government".
- The existing party legend continues to name the parties.

Verification:
Command: uv run --with pytest --with playwright pytest -q product/nz_election/tests -k night
Output tail:

```text
=========================== short test summary info ============================
FAILED product/nz_election/tests/test_night_deployed.py::test_browser_checks[probe]
FAILED product/nz_election/tests/test_night_deployed.py::test_browser_checks[rehearse]
FAILED product/nz_election/tests/test_night_deployed.py::test_browser_checks[faults]
FAILED product/nz_election/tests/test_night_design_followup.py::test_night_design_browser
ERROR product/nz_election/tests/test_night_page.py::test_xml_python_browser_parity
ERROR product/nz_election/tests/test_night_page.py::test_replay_makes_no_official_feed_request
4 failed, 358 passed, 2712 deselected, 2 errors in 152.50s (0:02:32)
```

All six browser outcomes above failed at Chromium launch: MachPortRendezvousServer bootstrap_check_in Permission denied (1100).
Focused command: uv run --with pytest pytest -q product/nz_election/tests/test_home.py product/nz_election/tests/test_night_page.py -k 'not xml_python_browser_parity and not replay_makes_no_official_feed_request'
Output: 56 passed, 2 deselected in 14.35s
Command: bin/lint
Output: lint ok (1172 text files)
git diff --check: no output.
Direct render probe confirmed historical final-count wording and retained live update clock.

Open verification: screenshots at 390x844 and 1280x800 were attempted with the populated night_browser harness, but Chromium launch was sandbox-denied. No screenshots were produced or visually reviewed. Browser and visual checks need a host that permits Chromium.
No product questions. No data, workflow, CSS or template changes.
