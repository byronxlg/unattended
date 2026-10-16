Committed `980d06e` on `change/nz-election-design`. Not pushed; worktree clean.

Diff: 2 files, 3 insertions, 3 deletions.
- `build.py`: removed the overhang segment’s `aria-label`.
- `coalitions.mjs`: removed the same attribute and added overhang count to the seats-table caption.

Segments remain presentational in both renderers. Overhang remains accessible through the tables. Tests and `verify.py` unchanged.

Verification tails:

```text
pytest -q product/nz_election/tests
287 passed in 141.83s (0:02:21)

refresh.py --fixtures ... && build.py ... && verify.py all ...
PASS build: 77 routes
PASS all

rg -n 'aria-label' .../coalitions.mjs .../build.py
No segment or overhang element has an aria-label.

bin/lint
lint ok (313 text files)
```

Screenshot harness and axe were not run in the sandbox. Host verification remains pending.