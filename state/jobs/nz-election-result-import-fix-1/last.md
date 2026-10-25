Committed `2c40bed`; not pushed.

Imports now reject `NIGHT_IMPORT_CONFLICT` unless the complete night bytes match the verified bundle, including lease retries.

Both regressions failed on `3309ff2` and pass with the fix. Requested suite: **146 passed, 1 failed**. The existing browser test remains blocked by Chromium’s sandbox permission error. Lint: `lint ok (1059 text files)`.

Protected tests unchanged. Commands and outputs recorded in uncommitted `last.md`.