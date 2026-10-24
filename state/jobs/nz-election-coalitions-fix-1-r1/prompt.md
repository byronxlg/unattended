# Follow-up 1: coalitions fix (PR #72)

The fresh review found one Important issue, and the supervisor agrees.

78a9b94 sets the explorer's `[data-live]` to "Seats are unavailable" when `scenario()` returns no
seats (coalitions.mjs:166). That text is visible to readers: build.py:283 renders it as a normal
paragraph and coalitions.mjs:199 shows its container. Byron's rule (issue #40) is that a reader never
sees "not available" wording. The static gate in product/nz_election/tools/check_visible_text.py:86
(ABSENT_TEXT) catches this in built HTML but cannot see text the client adds at runtime.

Do this:
1. Replace that runtime message with something a reader can act on: say why there is no seat count
   for this allocation and what change brings one back (for example lowering the electorate seats),
   using what `scenario()` actually knows. Pick the wording yourself. It must not match the
   ABSENT_TEXT patterns in check_visible_text.py.
2. Your supervisor authorizes changing exactly one pre-existing assertion: coalitions_browser.py:167
   on main at 8a8d484 (`'Seats are unavailable' in ...[data-live]`). Make it assert the new message,
   and also run that `[data-live]` text through the same check_visible_text ABSENT_TEXT patterns, so
   a regression back to absent wording fails the test. Every other assertion in that function stays
   as it is: the cleared picture and the 70/71 unassigned counts.
3. Do not touch any other test, and do not commit last.md or anything under state/.

Done when (report the output of each):
- `uv run --with playwright python product/nz_election/tests/coalitions_browser.py` prints PASS coalition browser
- with only coalitions.mjs:166 put back to the 78a9b94 text, that same command fails on the ABSENT_TEXT check (then restore it)
- `uv run --with pytest pytest -q product/nz_election/tests/test_absent_presentation.py` passes
- `bin/lint` prints ok
Commit on change/nz-election-coalitions-fix. Do not push.
