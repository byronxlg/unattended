Verdict: **request changes**

**Critical:** None found.

**Important**

- [last.md:27](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-page/last.md:27): Required screenshots were never captured. The screenshot-first question test remains unverified for Wellington North, Te Tai Tonga and Port Waikato. DOM order passes, but cannot establish readability or above-fold placement. Capture and inspect the required phone and desktop views before acceptance.
- [electorate_pages.py:73](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-page/product/nz_election/pipeline/electorate_pages.py:73): Incumbent flags come from `candidates-2026`, not the reconciliation snapshot. Names, parties and ranks use reconciliation correctly; incumbency uses an explicit source flag rather than inference, but still fails your reconciliation-only requirement. The replacement tests preserve this alternate sourcing.

**Nit**

- [snapshot_views.py:130](/Users/byron/repos/unattended/.worktrees/nz-election-electorate-page/product/nz_election/pipeline/snapshot_views.py:130): Methods still describes square tiles on detail pages, which this change removes.

Read-only verification using `.venv/bin/python -B -c …` produced:

```text
PASS 71 seats: DOM order, absent-text gate, provenance, locator cap
max locator bytes 21759
```

The locator has Stats NZ attribution, licence and an enforced 24,000-byte cap. No page or transfer budget increased. Apart from incumbent sourcing above, the seven assertion replacements track removed modules without unrelated weakening. Full pytest and visual checks were not rerun.