**Verdict: request changes.**

**Critical:** None found.

**Important:**

- `product/nz_election/web/polls.css:1` - Phone question test fails question 2. At 390×844, National’s +0.2-point change is visible, but Labour’s change and the remaining trend are below the fold. Compact the layout or provide a readable change summary above the fold. `tests/screenshots.py:323` only checks that the trend starts above 844px, which does not establish answerability.
- `product/nz_election/pipeline/polls_page.py:58` - The reused trend helper draws coloured label connectors that resemble falling data series, particularly on desktop. The underlying connector is at `pipeline/home_charts.py:133`. Visually separate connectors from observations and average lines.

**Nit:**

- `product/nz_election/pipeline/polls_page.py:59` - Passing `"Wikipedia contributors."` to `footnote()`, which adds punctuation, produces a double period. Same issue at line 73.

Question-test answers read from the phone screenshot: National leads Labour **28.7% to 27.9%**, dated **24 October**; only National’s **+0.2 points since 26 September** is fully readable; seats are outside the screenshot. Desktop shows Government **67**, Opposition **58**, with **67 needed**.

Read-only verification using `python3 -B -c` produced:

```text
Legacy IDs: 101 missing: []
Other changed HTML: ['methods/index.html']
Threshold None/2.99/3/5/7/7.01: excluded/excluded/included/included/included/excluded
House/majority: 132 67
Ten newest order: True rows: 10
Empty sections/figures/unavailable: False False False
```

No weakening found in other-route assertions, byte/font budgets, or allocator thresholds. Methods changes are expected. Both 132- and 133-seat Houses require 67.

No files modified. Full tests and browser harness were not rerun; one-scroll seat reach and reference side-by-side comparison remain unverified.