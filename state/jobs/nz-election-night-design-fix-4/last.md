Committed, no push:

- `5aa1172`: merged origin/main; retained all 29 main browser assertions.
- `8eedc0c`: kept search caveats visible and replaced branch markup assertions with behavior checks.

Verification:
- Requested pytest suite: `14 failed, 447 passed, 2 errors`.
- All failures/errors were Chromium startup denials (`Permission denied (1100)`); browser checks and screenshots require host verification.
- `bin/lint`: `lint ok (1132 text files)`.
- `git merge-tree --write-tree origin/main HEAD`: exit 0.

`last.md` and artifacts remain uncommitted.