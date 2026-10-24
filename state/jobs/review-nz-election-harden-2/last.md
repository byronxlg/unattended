Verdict: **request changes**

Critical: None.

Important:
- [check_workflow_history.py:53](/Users/byron/repos/unattended/.worktrees/nz-election-harden/product/nz_election/tools/check_workflow_history.py:53): Midnight splits a real success gap into two independently passing gaps. Probed three days with hourly successes at 03:00, 06:00, …, 21:00 NZ each day. The **six-hour overnight gaps** still produced `PASS workflow history`, exit 0. Compare consecutive successes across days and add a regression test. Item 4 remains incomplete.

Nit: None.

Read-only probes using `python3 -B -c` confirmed items 1-3 reject cases that returned PASS on `5835b0e`. The one-success/23-failures case also now fails; corresponding regression tests are present. No existing check weakening or token disclosure found in the reviewed changes.

No pytest run. `uv run` could not create its temporary directory under the read-only sandbox, so probes used installed Python directly.