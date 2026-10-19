# nz-election-snapshots fix-1 (PR #42, fresh review Important)

The fresh review found one Important: in `product/nz_election/pipeline/snapshots.py` (about line 110)
record-level `licence` is only checked for nonempty text. A leader record or a copied coalition quote
with `licence: "nonsense"` loads without error. Photo licence validation already works.

Fix: validate record licences against an allowed set (the photo rule's set, plus whatever statement the
EC / Wikipedia / Crown-copyright facts actually carry today; read the committed snapshots to see the
values in use and name the set once as a constant). Unknown licence raises `ValueError` naming the file
and record. Add negative tests: a leader with `licence: "nonsense"` and a copied quote with
`licence: "nonsense"` each raise; every committed snapshot still loads.

Constraints: tests on main at the base sha (05b311b) are not edited; this branch's own tests may move.
No templates, styles, workflows. Commit in the worktree, do not push, do not commit last.md.

Done when, from the worktree:
- `uv run --with pytest pytest -q product/nz_election` passes (report the count)
- `bin/lint` prints ok
- the two new negative tests fail on c737231 and pass on HEAD (say how you checked)
