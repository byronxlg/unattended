Read `git diff ba8914b..ec78040`: five files, 121 insertions, zero deletions. HEAD is `ec78040`. Followed REVIEW.md; no changes or approval.

1. **Bundle binding:** Read-only, in-memory probes using `python3 -B -c` produced:
   ```text
   existing bundle PASS
   inventory only GEOGRAPHY_REGISTRY_HASH_MISMATCH
   registry hash only MIXED_GEOGRAPHY_GENERATION
   all family hashes ACCEPTED
   ```
   Rewriting the payload, all three dependency hashes, CSV siblings and inventory remains accepted. This provides internal consistency, not authentication: no self-contained checksum can prevent coordinated rewriting. No additional finding under that contract.
   
   Producer and validator both hash `canonical(rows).encode('utf-8')`. Canonicalization sorts keys and preserves Unicode; registry round-trip was byte-identical with macrons present. Both geometry envelopes also round-tripped identically; decimal-string properties remain strings and are outside the registry digest.
   
   Missing, empty, null, list, object, huge-integer and unusual-Unicode hashes returned `GEOGRAPHY_REGISTRY_HASH_MISMATCH`; floats returned the earlier `INEXACT_NUMBER`.
   
   Rejecting pre-fix geography bundles is acceptable given none were published. Local artifacts need regeneration; existing poll-only bundles need no migration. No other migration path identified.

2. **Important: CSS token parsing silently omits valid assets**, [svg_budget.py:25](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/tests/svg_budget.py:25).
   In-memory filesystem probes with six-byte `<svg/>` assets returned **0**, expected **6**, for both:
   ```html
   <style>x{background:url("../maps/a\"b.svg")}</style>
   <style>x{background:url("../maps/map.svg?x=/*")} /* real comment */</style>
   ```
   The regex mishandles escaped quotes; comment stripping consumes quoted URL content through the subsequent comment terminator. Both bypass the required SVG budget. Parse CSS strings, escapes and comments together.

3. **Important: SVG data URIs bypass the budget**, [svg_budget.py:29](/Users/byron/repos/unattended/.worktrees/nz-election-5/product/nz_election/tests/svg_budget.py:29).
   Probe `<style>x{background:url("data:image/svg+xml,%3Csvg/%3E")}</style>` returned **0** without crashing, although the decoded SVG is six bytes. Extension-only detection omits embedded SVGs of arbitrary size. Count decoded SVG bytes or explicitly reject this form.

   Other CSS probes passed: whitespace and uppercase/query/fragment references returned **6**; duplicate stylesheets, cyclic nested imports and a shared HTML/CSS SVG returned **6**, with each stylesheet read once.

4. **Assertions preserved:** `git diff --numstat ba8914b..ec78040 -- '*test*'` returned `45 0`, `35 0`, `36 0`. No existing assertions removed or changed.

5. **Verification:** `uv run --offline --with pytest pytest -q -p no:cacheprovider` could not start: `Failed to initialize cache ... Operation not permitted`. Full verification/build/screenshot runs were not repeated. Your reported 306 passes and host checks remain supervisor evidence. Independently computed SVG size: **284316 bytes**. Existing screenshot directory contains 28 PNGs, so it does not independently establish the reported 24-image run.

Nits: none. No additional security findings. Open questions: none.

Important findings: 2