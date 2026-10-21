**Verdict: request changes.**

**Critical:** None.

**Important:**

- `last.md:31-35`: Browser and visual acceptance remains incomplete: recorded suite result is `1833 passed, 2 errors` from Chromium launch failures; required 390×844 and 1280×800 screenshots remain absent. Run the browser harness on a permitted host and inspect both sizes before acceptance.

**Nit:** None.

The publication-freeze finding is resolved substantively. The active renderer preserves the sentence and both links; the route gate independently requires the sentence and s197 href. Protected `test_home_routes.py` is unchanged.

Verification:
- Read-only rendering probe: `PASS: 10 phase/data cases, 50 frame/source notes with notice and both links`.
- Same probe against `eb4a0d0`: notice absent in `10/10 cases`.
- Recorded active-build regression: baseline `4 failed`; fixed freeze tests `6 passed`.
- `node --test product/nz_election/tests/night_scheduler.test.mjs`: `1 pass, 0 fail`.

No new fix-3 defects identified. No files changed.