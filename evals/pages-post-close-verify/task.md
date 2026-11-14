# pages-post-close-verify

Incident: from polling close (2026-11-07 06:00Z) the Pages workflow failed "Verify election pages"
216 times on 7 and 8 November with `FAIL all: CAMPAIGN_DATA`, so nothing deployed after
2026-11-06 02:35Z and the live site never showed election night. Cause: `route_checks.check_site`
re-rendered each electorate's candidate cards without the build clock, while the built page used
the post-close state, so the comparison failed on every build made after the close. The aggregate
check reports any failure as `CAMPAIGN_DATA`, which hid the route check's own reason.

Task: `verify.py all` must accept a site built at a clock after polling close.

Check: `evals/pages-post-close-verify/check.sh`, last line `PASS post-close build verifies`.
