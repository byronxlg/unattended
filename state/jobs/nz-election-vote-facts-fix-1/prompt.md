Follow-up 1 on nz-election-vote-facts (build thread, same worktree, PR #53). Fresh review found one Important:

1. product/nz_election/pipeline/snapshots.py:251: malformed UTC offsets pass validation. An `at` of
   `2026-10-26T00:00:00+12:60` loads: Python normalises it to +13:00, the offset check passes, and the loader
   returns the malformed string unchanged. Validate the offset text itself (hours 00-14, minutes 00-59, the exact
   +HH:MM form the snapshot uses) before parsing, and add a regression test expecting `voting_date_invalid` for
   `+12:60` (and one other malformed form of your choice).

Constraints: one commit; do not push. Tests on main at the base sha stay unweakened; this branch's own tests move
with it. No other changes to data or sources.

Done when, in the worktree:
`uv run --with pytest pytest -q product` passes (count reported in last.md) and `bin/lint` prints ok;
the new test fails if the offset validation is removed (say how you checked).
