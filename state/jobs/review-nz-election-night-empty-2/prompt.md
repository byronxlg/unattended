Fresh review of PR #129 (branch change/nz-election-night-empty, stacked on change/nz-election-home-stale). Read REVIEW.md first. Review only the diff `git diff change/nz-election-home-stale...HEAD` (three dots). Goal: night/ with no live capture renders a ready, honest shell that the first live capture fills; no stale or invented figures; Page plan intent/nz-election/pages/night.md; DESIGN.md. Tests must check data, absence and accessibility, not markup or class names. Verdict accept or request changes, findings ranked Important/nit with file:line.

## Second round

The first review asked for absence-of-figures checks in the empty states. Check fix-2 (acf37ae) delivers them
as data/visible-text assertions, and that the merge of origin/main (6d2473c) kept main's behaviour in
night_page.py and result_states.py apart from the has_snapshot branch. Verdict accept or request changes.
