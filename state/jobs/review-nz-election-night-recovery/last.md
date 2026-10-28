Verdict: **request changes**.

- **Important** - `product/nz_election/pipeline/night_start.py:84`: Dispatch can bypass both safeguards through the exposed CLI. `--dispatch` without `--state` skips the six-attempt budget; supplying `--state` still acquires no lock. Concurrent direct invocations can overwrite reservations or dispatch alongside the watchdog. Require dispatch through the locked wrapper, or enforce the shared lock and ledger at this entry point.

- **Important** - `product/nz_election/tests/test_night_operation.py:928` and `:997`: The budget and post-reservation cutoff tests fail on `1d1d9fa` because its `main()` rejects the new `state` keyword, before exercising either behavior. The invalid-ledger tests at `:988` have the same issue. Add regression coverage through an interface supported by both revisions so baseline failures demonstrate excess dispatch or late dispatch.

Within the default watchdog path, reservations precede dispatch, uncertain failures consume budget, and the existing outer lock remains in place. Any listed noncompleted run suppresses recovery, including a slow running loop. The cutoff is rechecked immediately before invoking `gh`; this does not guarantee an already-started request finishes before 8 November 06:00Z.

The recovery-outcome tests and expired-marker test do target baseline behavior meaningfully. These are static conclusions: read only the requested diff and `REVIEW.md`; no tests executed or files changed.