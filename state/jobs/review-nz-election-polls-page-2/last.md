Verdict: **request changes**

**Critical:** None.

**Important**
- `product/nz_election/tests/screenshots.py:327` - Fix-1’s required visual verification remains incomplete. Supplied screenshots show the old connectors, duplicate punctuation, and no leading-party summary. Run the populated-state harness at `93696cc` and inspect fresh 390×844 and desktop captures, confirming both change answers above the fold and seats within one scroll.

**Nit:** None.

Question test on supplied screenshots: National leads 28.7% to 27.9%; Labour’s change is clipped on the phone; the full capture shows governing parties at 67 seats, with 67 needed.

Code checks support resolution of all listed findings: neutral ticks, punctuation, change summary, and night startup hydration. Fold checks are stronger; JS/no-JS equality remains exact. No other-route assertion, byte/font budget, or allocator threshold was weakened.

Read-only verification:
- Cached Python, pytest with `-s -p no:cacheprovider`: **14 passed, 5 deselected**.
- Real chart and summary assertions against archived live data: **PASS**.
- Legacy IDs: **101, none missing**.
- Overhang: **132 seats, 67 needed**.

No new code defects found. Acceptance remains pending current visual evidence.