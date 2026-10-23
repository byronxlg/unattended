# Fix-1: host harness AXE landmark-unique (principles-routes, 0bfcaff)

The host harness (`product/nz_election/tests/screenshots.py --site site`, Chromium, on the populated
build from `site/build_review.py`) stops at its first assertion:

```
AssertionError: AXE_VIOLATIONS: landmark-unique (moderate): two <div class="scroll" role="region"
aria-label="Theoretical seats and overhang">, one at `.seat-module > .seat-data > .scroll`, one at
`div[data-picture=""] > .seat-data > .scroll`.
```

The static seat table (`pipeline/build.py:252`) and the client-rendered copy from
`web/coalitions.mjs:130` are both visible now that the seat-data disclosure is open; on c6d8ff3 the
closed `<details>` kept one out of the accessibility tree. Fix the cause: one visible seat table per
page, or distinct accessible names if both are meant to show (say which and why in last.md). Keep the
`source-seats` aria-describedby contract and the client/server parity assertions.

The harness cannot run in your sandbox and stops at the first failure, so also audit the rest of the
change for anything else the opened disclosures exposed that axe or the harness would catch: duplicate
region labels or ids, duplicate landmarks, focusable scroll regions, PAGE_OVERFLOW from opened
manifest or JSON records at 360 px (downloads/ overflowed in the last round from exactly this),
SMALL_TARGET on links now inline. Add a no-Chromium check that fails on 0bfcaff: no page, after the
client modules have rendered their markup (render the coalitions.mjs output the way existing parity
tests do), has two `role="region"` elements with the same aria-label. Report the check failing on
0bfcaff and passing on HEAD.

Tests on main at c6d8ff3 stay as they are except where this change's registered set moved them (as in
the build brief); this branch's own tests move with it. Nothing weaker.

Done when: `uv run --with pytest pytest -q product` passes, `verify all` PASS all, `bin/lint` ok, the
new check's fail/pass output in last.md; commit in the worktree, do not push, last.md not committed.
