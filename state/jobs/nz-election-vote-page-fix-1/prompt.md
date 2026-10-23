Fix round 1 on PR #57 (change/nz-election-vote-page, head 3228381). Fresh review request changes; the supervisor
ran the host harness at real time (PASS 80 routes 318 images) and looked at vote-before and vote-open at 390 and
1280: the question test passes, so review item 1 is closed by the supervisor. Fix these two:

1. product/nz_election/tests/screenshots.py:418: answer 3's check reads only the bottom coordinate, so a
   display:none answer (zero rect) passes. Require the answer element to be visible with nonzero width and height
   and its whole box inside the first viewport, and its text non-empty. Show the check failing on a deliberately
   hidden answer 3 (a unit-level or fixture probe is fine; say how in last.md), then passing on HEAD.
2. product/nz_election/pipeline/vote_page.py:44: answer 3's copy is hardcoded and the snapshot records only toggle
   it. The published guidance must come from snapshots/voting.json (render the records' summaries, or add approved
   compact copy fields to those records with their source), so a snapshot correction changes the page. A test that
   edits the snapshot copy in a fixture and sees the page change.

Constraints: tests on main at the base sha stay untouched; this branch's own tests may move. No other scope.
Done: `uv run --with pytest pytest -q product` passes, `bin/lint` ok, commit on the branch, do not push, report the
counts and the failing-then-passing evidence in last.md (not committed).
