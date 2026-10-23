Follow-up 2 on PR #39 (fresh review request changes). Same worktree, same branch, commit on top of 58a08dd. Do not commit last.md or artifacts/.

1. Important, product/nz_election/pipeline/home_charts.py around line 101: a trend series whose last observation is earlier than the plotted end must not get a connector or label that reads as data up to the right edge. End-labels sit at the series' own last point (or, if they must sit in a label column, the connector lies outside the data area and is visibly distinct, e.g. dashed and grey), and a stale endpoint names its date (e.g. "National 29.6% (12 Oct)"). Add a test that drops one party's final 14 days from a fixture and asserts no path or connector for that party extends past its last observation's x, and the label carries the date. Show the test failing on 58a08dd in last.md.
2. Nit, line 10: pollster symbols keep their shape at every width: no non-uniform scaling of markers (e.g. position by scaled coordinates but draw markers in an unscaled layer, or preserveAspectRatio plus computed positions). A measurement at 360 in last.md: marker bbox width/height ratio within 0.9 to 1.1.
3. Nit, line 106: the trend's date labels match the first and last plotted data positions, not the module edges.

Tests on main at 6e5f3bf are protected; this branch's own tests may move with the change, nothing weaker. Existing harness checks stay as strict.

Done when: `uv run --with pytest pytest -q` passes, `bin/lint` ok, the site builds and `site/screenshots.py` harness PASS as before (79 routes), and last.md lists the commit, the failing-then-passing test output and the 360 marker measurement.
