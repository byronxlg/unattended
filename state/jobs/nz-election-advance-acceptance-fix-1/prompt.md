# Fix 1 for PR #118 (advance publication acceptance)

Fresh review (request changes), confirmed by its in-memory probe:

1. Important: `product/nz_election/pipeline/advance_acceptance.py:22` (`VisibleText`) accepts text a reader
   cannot see. The correct count and date inside `<p style="display:none">` (or `hidden`, or an ancestor with
   either) still yields ACCEPTED.
   Invariant: acceptance passes only when the count and date sentence is visible to a reader on both home and
   vote/. Choose the mechanism (exclude `hidden`, `aria-hidden="true"`, inline `display:none` /
   `visibility:hidden` and their descendants in the parser; or a rendered check in Chromium if the command
   already has one); say which in last.md and why it is enough for this site's markup (the site uses no
   stylesheet rules that hide the advance line; check `styles.css` for any class that would).
   Add behavioural regression tests on both routes: hidden attribute, inline display:none on an ancestor,
   inline visibility:hidden; each must be rejected with the existing not-published code, and the visible
   case still accepted.

Constraints: fix job; tests on main at the PR's base sha are untouched; this branch's own tests may move with
the fix. Commit in the worktree, do not push.

Done when: the pytest command from your build round's last.md passes, the new cases fail with
advance_acceptance.py at the PR's current head, and `bin/lint` prints `lint ok`. Write commands and output
in last.md.
