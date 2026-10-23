# nz-election-home-design follow-up 1 (supervisor host review of 5cc640b)

Host: screenshots.py PASS 79 routes 296 images on artifacts/home-design/after. Full-page
screenshots served under the /unattended prefix at 1280x800 and 390x844 are in
artifacts/home-design/ (h1280-0.png, h1280-2.png, h390-0.png). Look at them first. The direction
is right (charts, derived hero, 700 px column, one nav row); these defects block the PR:

1. Chart text scales with the viewport. The SVGs scale by viewBox, so at 1280 the poll, trend and
   threshold labels render about 22 to 26 px (larger than the h2) and at 390 about 9 px (below
   legibility). Text in every home chart must render at the body/caption sizes of the page at
   every width (no chart label under 12 px or over the body size at 360, 390, 1280). Either
   size the SVG in CSS px with no scaling, or put the labels in HTML beside a scaling mark layer;
   your choice. Add a Chromium check in screenshots.py (computed or measured glyph height of chart
   text at 360 and 1280) that fails on 5cc640b.
2. The threshold module is not a graphic: it renders as large text lines ("ACT: 8.1% / At or above
   5%"). Make it a horizontal bar per party with the 5% reference line, party colour, value
   label, and the status (Needs 5%, Electorate assumed) as a small label, the same visual grammar
   as the other charts.
3. Latest polls are three stacked panels of seven rows (21 rows, the longest module on the
   page). Show one row per party with one dot per pollster (dot plot, 538 style: a shared 0 to
   max axis, pollster distinguished by shape or a small legend, the newest poll emphasised), so
   the module is about seven rows tall. Exact values stay in the visually hidden table.
4. Hero wording: "would have a majority of 3" reads as a 3-seat lead over the opposition (the
   lead is 7). Say it plainly from the same derived numbers, e.g. "the governing parties would
   have 67 seats, 3 more than the 64 needed". Keep the equal and below cases derived the same way.

Constraints: same as the brief. Tests on main at 6e5f3bf are protected except the contracts the
brief already names as moving; your branch's own tests move with this follow-up. Do not commit
last.md or artifacts/.

Done when: pytest product/nz_election passes, verify.py all PASS, bin/lint ok, the new check
fails on 5cc640b and passes on HEAD (say how you showed it), committed on change/nz-election-home-design.
Chromium is unavailable in your sandbox: the supervisor runs screenshots.py on the host.
