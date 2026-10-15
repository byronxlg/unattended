Committed `90b239e`; not pushed. Worktree clean.

Updated `acceptance.py`, `capture.py`, `snapshot.py`, and the named test: restored the literal, preserved original plist bytes, documented the shim, and asserted binary byte identity.

Verification outputs:
```text
registry --offline: OK registry
observer --offline: OK observer
pytest -q: 224 passed in 1.18s
bin/lint: lint ok (115 text files)
import grep: product/fleet_audit/fleet_audit/collect.py
```
All requested checks exited 0. Also verified malformed bytes survive capture and replay reports invalid input.

Nothing outstanding.