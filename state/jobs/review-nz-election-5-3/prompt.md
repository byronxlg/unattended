Fresh-context review of the fix commit on branch change/nz-election-5 for
https://github.com/byronxlg/unattended/pull/13 (NZ election increment 5, geography and
directory). Worktree .worktrees/nz-election-5, read-only. Follow REVIEW.md. Important or Nit, at
most five nits, nothing bin/lint reports. Do not approve.

Scope is the fix diff only: `git diff ba8914b..ec78040` (121 insertions, 0 deletions, five
files). The second fresh review (logged on PR #13) found two items, now addressed:
1. A retained geography bundle is bound to its own recorded inputs: daily_refresh.py records
   sha256(canonical(registry rows)) as input_hashes["electorates.data"]; validate_bundle
   (pipeline/export.py around 288) recomputes it from the bundle's own electorates.json data and
   raises GEOGRAPHY_REGISTRY_HASH_MISMATCH. No checkout reads.
2. tests/svg_budget.py collects CSS url(...) SVG references from style attributes, <style>
   blocks and linked stylesheets (stylesheet-relative resolution, nested @import-style .css
   url() followed once per stylesheet).

Check, in this order:
1. Item 1: can a bundle still be altered in a way that leaves every recorded hash consistent
   with the altered bytes (consider the inventory, MIXED_GEOGRAPHY_GENERATION, and the
   electorates envelope hashing a payload it also carries)? Is the canonical form used by the
   producer byte-identical to the one validate_bundle recomputes, including key order, unicode
   (macrons) and the decimal-string geometry properties? Known consequence, judge it: a
   geography bundle produced before ec78040 (no electorates.data key) is rejected, so the
   supervisor's stale local artifacts failed refresh, daily_refresh and build until regenerated.
   No geography bundle has ever been published to the data branch (increment 5 is not merged),
   so there is no live bundle to migrate; say whether anything else needs a migration path.
2. Item 2: does css_urls handle url() values with whitespace, uppercase extensions, query
   strings or fragments, escaped quotes, and data: URIs without crashing or miscounting? Is a
   stylesheet referenced twice counted once, and an SVG referenced from both HTML and CSS
   counted once? Does the comment stripper mis-handle a url containing the characters /* ?
3. Did any existing test assertion change? `git diff ba8914b..ec78040 -- '*test*'` should show
   no removed lines.
4. Supervisor host run on ec78040 after regenerating artifacts: 306 passed, verify all PASS,
   refresh, daily_refresh and build PASS (6 routes), screenshots 24 images, lint ok. Electorates
   page SVG total 284,316 bytes before and after item 2.

Report: the diff you read, each check with its evidence (commands and output where the
read-only sandbox allows), Important findings with file:line and a reproduction, nits, and
"Important findings: N" as the last line.
