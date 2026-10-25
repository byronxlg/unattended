# Result import workflow

Changed `.github/workflows/nz-election-result-import.yml`, pipeline `result_import.py`,
`result_states.py`, `publish.py`, `runbook/night.md`, and `tests/test_result_import.py`.
Dispatch-only settled/official imports pin a reachable data SHA, require reviewed manifest
captures, verify night/waterfall, publish only night through the leased publisher, and
pin the Pages dispatch. Summary records capture hash and input/published SHAs.
Rollback restores pre-import night bytes with a head-bound lease override.
Synthetic paths, manifest annotations and relocated known synthetic hashes are rejected.
No pages/templates changed. No push or production dispatch performed.

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_states*.py product/nz_election/tests/test_workflow*.py product/nz_election/tests/test_night_operation.py product/nz_election/tests/test_result_import.py
1 failed, 133 passed in 202.40s (0:03:22)
FAILED product/nz_election/tests/test_result_states.py::test_result_states_browser
```
Chromium cannot launch under this macOS sandbox: MachPortRendezvousServer
`bootstrap_check_in ... Permission denied (1100)`, then SIGTRAP. Tests were not weakened.
```text
uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py product/nz_election/tests/test_harden.py
108 passed in 129.72s (0:02:09)
uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py -k 'cli_job or malformed or relocated'
9 passed, 24 deselected in 0.24s
bin/lint
lint ok (1059 text files)
source .venv/bin/activate
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/nz-election-result-import.yml'))"
exit 0, no output
```
System python lacks PyYAML; repository environment has it. Scheduled-workflow discovery
remains unchanged because this workflow has no schedule; history contracts passed.
New codes: NIGHT_CAPTURE_NOT_REAL, NIGHT_VERIFY_FAILED, NIGHT_ROLLBACK_CONFLICT.
Reused: MISSING_CAPTURE, CAPTURE_HASH_MISMATCH, UNSAFE_CAPTURE_PATH, UNSAFE_DATA_TREE,
NIGHT_DATA_SHA, PUBLICATION_FROZEN, NIGHT_STATE, NIGHT_BASELINE, NIGHT_LIVE.
Open: rerun browser verification on an unrestricted runner. Real captures must be reviewed
and committed on main before dispatch; the configured official endpoint still needs EC confirmation.
