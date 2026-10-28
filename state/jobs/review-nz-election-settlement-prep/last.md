The synthetic-label guard can reject genuine election XML based on ordinary party names. Runtime verification was blocked by the read-only sandbox.

Review comment:

- [P2] Restrict synthetic-label detection to provenance fields - /Users/byron/repos/unattended/.worktrees/nz-election-settlement-prep/product/nz_election/pipeline/settlement_capture.py:35-36
  When genuine XML contains a name such as `DemocracyNZ` or `Democratic Alliance` (both occur in the repository's EC party captures), scanning the entire row matches the unanchored `demo` pattern inside `raw_xml` and raises `NIGHT_CAPTURE_NOT_REAL`. This prevents preparing a legitimate settlement capture despite valid provenance. Check explicit provenance labels rather than arbitrary election content, while retaining the known-synthetic XML comparison.