**Verdict: request changes.**

- **Important**: [product/nz_election/tests/test_design.py:112](/Users/byron/repos/unattended/.worktrees/nz-election-home/product/nz_election/tests/test_design.py:112) discards `/polls/` transfer bytes and checks only asset presence. The byte and reserved-font budgets now cover home, which excludes explorer dependencies. Explorer code or data can therefore exceed the previously enforced budget without failing. **Invariant:** moving the registered page must not weaken main’s checks. **Verify fix:** enforce both budgets on home and polls; confirm oversized explorer dependencies fail the polls assertion.

Other checks found no H-b implementation leakage. Read-only, in-memory probes reported:

```text
PASS in-memory populated home/polls provenance
PASS absent family polls
PASS absent family baseline-2023
PASS absent family candidates
PASS tied winners excluded
PASS missing results excluded
PASS East Cape eligible
PASS all old root content IDs preserved on polls: 92
```

The selected six are Nelson, Tāmaki Makaurau, Banks Peninsula, Te Tai Tokerau, West Coast-Tasman and Taieri. No incumbent inference, ratings, or raw social posts/handles found. Route and screenshot-count changes reconcile with the plan. Explorer URLs and hash handling appear correctly retargeted; browser behavior remains unverified.

Review limitations: `gh pr view 29 --comments` failed to connect; the connector requires reauthentication. The engineer’s account is absent from local `main`. Only 360 px captures were available, so required phone/desktop visual review remains open. The existing generated bundle failed validation with `INVALID_SOCIAL_FIELDS`.

`uv run --with pytest pytest -q product/nz_election` could not run:
```text
Failed to initialize cache at /Users/byron/.cache/uv
Operation not permitted (os error 1)
```

No files changed.