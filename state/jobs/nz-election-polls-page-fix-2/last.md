Committed `a538aae`; not pushed.

Removed the polls CSS override causing a 120 px desktop hero strip where 144 px is required. This conflict is absent on `382c962`. Tests unchanged.

Verification:
- Live build: `PASS build: 81 routes`
- Verifier: `PASS all`
- Targeted tests: `38 passed`
- Full suite: `2034 passed, 1 failed, 2 errors`
- Lint: `lint ok (830 text files)`

All three test failures and the screenshot harness are blocked by Chromium `Permission denied (1100)`. No browser measurement or visual inspection was possible; completion still requires the host harness.

Details and expected screenshot paths are in uncommitted `last.md`. Artifacts remain uncommitted.