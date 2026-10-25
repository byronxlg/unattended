**Verdict: request changes**

**Critical:** None.

**Important:**

- **bin/tick:33-34:** Watchdog execution blocks the host loop without an overall timeout. The Python timeout covers only `gh run list`, not `uv` startup or `gh workflow run`. Either can stall before supervisor checks. Extracted-function probes confirmed both delays propagate to tick. Bound the entire operation and ensure timeout permits tick to continue.

- **bin/tick:33-34:** Eligibility checking and dispatch are separate, unlocked operations. Overlapping ticks can both observe no run and dispatch; workflow concurrency does not prevent duplicate dispatches. An extracted-function probe produced two dispatches. Serialize the check/dispatch operation and retain a successful-attempt marker to cover run-list visibility lag.

- **bin/tick:34:** Dispatch can cross the closing boundary after Python returns eligibility. A decision at 8 November 05:59:59Z remains actionable after 06:00Z, especially with a slow dispatch command. The workflow guard prevents live work afterward, but the watchdog does not satisfy the stated dispatch-window guarantee. Put dispatch under the bounded, clock-aware operation and test this transition.

**Nit:** None.

Confirmed: `END` is freeze end/poll close, 7 November 06:00Z. Cron times map to 19:02 and 19:07 NZDT. The ten-minute grace and inclusive `createdAt >= END` comparison are correct. Probes reject exactly 8 November 06:00Z; missing `gh` and query timeout fail closed. The trigger assertion change preserves coverage, but new tests omit blocking and overlapping calls.

Read-only probes completed; `bash -n bin/tick` passed without output. Pytest was not run.