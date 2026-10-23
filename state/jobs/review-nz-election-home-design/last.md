Verdict: **request changes**.

**Critical:** None.

**Important**

- `product/nz_election/pipeline/home_charts.py:101`: Trend label connectors can imply observations across missing periods. Removing National’s final 14 days leaves its data path ending at x=165, but adds an indistinguishable coloured line to x=350 and labels the old value “National 29.6%”. Keep connectors outside the data area, distinguish them visually, and identify stale endpoint dates.

**Nit**

- `product/nz_election/pipeline/home_charts.py:10`: Non-uniform SVG scaling distorts the pollster symbols. At phone widths, circles and squares become narrow ellipses and rectangles. Preserve symbol dimensions independently of position scaling.
- `product/nz_election/pipeline/home_charts.py:106`: Trend dates span the entire module rather than the plotted interval. Align them with the actual first and last data positions.

Checked:

- Hero totals, majority and overhang are derived; above/equal/below probes passed.
- Charts retain accessible values and provenance links.
- `HOME_CHART_TEXT_SIZE` incorporates SVG screen scaling, rather than trusting CSS font size alone.
- Main-test changes match permitted navigation/election-night moves; existing harness checks were not loosened.
- Inspected 360/390/1280 screenshots: coherent hierarchy, restrained colour, no visible horizontal clipping.

Read-only probe output: `PASS: five chart fallbacks/provenance, three hero cases, three analytical typography cases`.

Limits: Chromium was not rerun. PR comments were unavailable through both CLI networking and the connected API.