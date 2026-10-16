Fix brief for change/nz-election-1 (PR #9), same worktree .worktrees/nz-election-1. Commit there;
never push. A fresh-context review found four Important items; the supervisor confirmed all four.

Invariants, and where each is enforced:

1. Poll parser: any wikitext construct the scanner does not fully understand fails parse_drift
   (spec "Poll method and assumptions"; plan "Poll parsing and identity"). Attribute parsing in
   poll_parser.py (around lines 140 and 211) only recognises double-quoted values, so
   rowspan='2' on a share cell, and data-sort-value='2026-10-11' against a visible end date of
   12 October, pass without parse_drift. Every merge and sort attribute must be seen whatever
   the quoting form (double, single, unquoted), then validated by the same rules.
2. Poll parser: a named reference is attached to exactly the poll that cites it. The regex at
   about line 151 treats <ref name="x"/> (self-closing, a use) as an opening definition and
   consumes through the next </ref>, so one poll takes the next poll's URL, and an intervening
   inline ref raises a false conflicting_named_ref. Distinguish uses from definitions in the
   scanner; forward references across several rows must resolve to the definition.
3. Allocator contract (spec "Allocator contract"): every malformed input raises exactly
   INVALID_INPUT, in both implementations, with the same accept/reject decision. Today {} raises
   KeyError in Python, a candidate given as an object raises TypeError before identity
   validation, and baseSeats: null is rejected by Python but defaults to 120 in JS. Validate the
   complete shape before any access or arithmetic; missing and null are decided the same way
   in both languages.
4. Allocator JS (web/allocator.mjs): output maps are plain objects, so a party id of "__proto__"
   (accepted by both implementations) serialises as {} in JS while Python returns the seat.
   Results must be independent of the party id string in both languages. Choose the shape;
   the parity runner must show the two agree for this id.

Rules: do not edit any existing test; add regression tests for each item (a single-quoted
rowspan, a single-quoted data-sort-value, a self-closing named ref followed by a definition,
an inline ref between use and definition, the three invalid-input shapes, the __proto__ id in
parity). Never edit anything under product/nz_election/fixtures/. Keep exact arithmetic.
No emojis, no em dashes. The review is in the PR: gh is offline in your sandbox, so the
findings above are the whole list.

Definition of done, run from the worktree root, paste each output in your final message:
1. `uv run --with pytest pytest -q` expected: all passed, the count greater than 108, 0 skipped.
2. `bin/lint` expected: `lint ok (<N> text files)` after `git add`.
3. `git status --short` expected: empty after your commit.
Final message under 30 lines: what changed per item, outputs, anything you disagree with.
