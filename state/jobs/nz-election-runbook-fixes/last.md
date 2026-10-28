Committed `349281f`; not pushed. Fixed all seven items in the two runbooks. Source checks recorded in uncommitted `last.md`. No code, tests, or DESIGN.md changes.

Verification:
```text
$ bin/lint
lint ok (1360 text files)

$ git diff origin/main --stat
 product/nz_election/runbook.md       | 29 +++++++++++++++---------
 product/nz_election/runbook/night.md | 43 ++++++++++++++++++++++++------------
 2 files changed, 47 insertions(+), 25 deletions(-)
```

`git diff --check origin/main`: no output.

Open questions: none.