Committed `06fcfa8`; not pushed. Worktree clean.

Updated `capture.py` to withhold malformed plist bytes, `snapshot.py` to preserve registry-error replay, and the requested tests.

Verification outputs:
```text
registry --offline: OK registry
observer --offline: OK observer
pytest -q: 225 passed in 1.13s
bin/lint: lint ok (115 text files)
import grep: product/fleet_audit/fleet_audit/collect.py
```

All requested checks exited 0. Nothing outstanding.