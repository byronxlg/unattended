Follow-up 1 on nz-election-electorate-facts (build thread, same worktree, PR #54). Fresh review found one Important:

1. product/nz_election/pipeline/snapshots.py:161: correction values are not validated. `load('candidate-reconciliation-2026')`
   accepts `after` (and `before`) values of "", null, [], {}, integers, floats and huge integers for a name correction.
   Validate `before` and `after` according to `field` (a name is a non-empty, trimmed string; an affiliation is a
   non-empty string from the set the snapshot already uses, or whatever invariant you find the consumers rely on;
   read them first), reject with the loader's existing error style, and add rejection tests covering at least
   "", null, a list, an integer, for both a name and an affiliation correction.

Constraints: one commit; do not push. Tests on main at the base sha stay unweakened; this branch's own tests move
with it. No other changes to data or sources.

Done when, in the worktree:
`uv run --with pytest pytest -q product` passes (count reported in last.md) and `bin/lint` prints ok;
the new tests fail if the validation is removed (say how you checked).
