Confirmed that the new out-of-range mtime observation fails snapshot deserialization. Full tests could not run because sandbox restrictions blocked uv cache access and the existing virtual environment lacks pytest.

Review comment:

- [P2] Allow timestamp-conversion failures to round-trip through snapshots - /Users/byron/repos/unattended/.worktrees/fleet-audit-5/product/fleet_audit/fleet_audit/files.py:110-114
  When an output file has an mtime outside Python's datetime range, this now records `exists=True`, `mtime=None`, and a stat error. However, `snapshot.output_observation()` rejects that combination as `inconsistent output evidence`. Consequently, capture produces a snapshot that cannot be replayed, turning a recorded observation failure into invalid input. Update the snapshot validator to accept this failure representation and add a round-trip test.