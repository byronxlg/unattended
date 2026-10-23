**Verdict: request changes.**

**Critical:** None found.

**Important**

- [electorate_pages.py:66](/Users/byron/repos/unattended/.worktrees/nz-election-principles-routes/product/nz_election/pipeline/electorate_pages.py:66), [build.py:371](/Users/byron/repos/unattended/.worktrees/nz-election-principles-routes/product/nz_election/pipeline/build.py:371): Source disclosures became open source dumps instead of moving full provenance to Methods. Both 360 px electorate screenshots show repeated name/party source locators consuming substantial space before the second candidate. Polls similarly exposes every individual source record below its table. This satisfies principle 4 but violates principle 5’s compact footnotes and Methods destination. Move detailed records to anchored Methods sections, retaining adjacent attribution/licence and existing fragment compatibility.

**Nit:** None.

Read-only verification against the populated build stamped `ee29ad1`:

```text
disclosures: 78 routes passed
landmarks: 79 routes passed, including client rendering
market budgets: 79 routes passed
source-note budgets: home and polls passed
local fragments: 291 checked, none broken
baseline IDs removed: none
home HTML: byte-identical to baseline
screenshot hashes: all matched
```

Inspected all six requested screenshots, plus social POC, market and earlier-window evidence. Social POC labelling remains visible; home market geometry remains compact. No existing harness check was removed or loosened. Existing test edits adapt disclosure markup and visible JSON expectations without removing substantive checks.

Limitations: full tests/browser harness were not rerun in this read-only session. `gh pr view 37 --comments` failed to connect; Doppler discovery also failed because its keyring secret was unavailable. PR comments could not be reviewed.