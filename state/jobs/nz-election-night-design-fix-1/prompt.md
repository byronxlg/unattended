Follow-up 1 on 18ab8ef (PR #94). Host Chromium run of test_design, test_home*, test_night*, test_waterfall:
1 failed, 400 passed, 2 errors. Plus the fresh review (state/jobs/review-nz-election-night-design/last.md) and the
supervisor's look at the 390/1280 screenshots. Fix all of these in one round:

1. ERROR test_night_page.py::test_xml_python_browser_parity and ::test_replay_makes_no_official_feed_request:
   TEXT_CONTRAST: {'text': 'Chlöe Swarbrick (Green Party)', 'fg': [22, 24, 29], 'bg': [0.853176, 0.917412, 0.863765]}.
   The background is reported in 0-1 channels (likely a color-mix()/color(srgb ...) computed value the contrast helper
   reads as 0-255). Either use a token colour that computes to rgb(), or make the helper parse color(srgb ...) correctly.
   The 4.5 threshold stays.
2. FAILED test_night_deployed.py::test_browser_checks[probe]: "FAIL deployed-probe: night-data-transport". Passes on
   main and on another branch on this host; find what the page change broke in the data transport path and fix the page.
3. Review Important 1: eight expanded majority cards push electorate search past two phone screens at 390 (12,209 px
   page); pages/night.md wants a reader to find their electorate in one scroll. Electorate search (or a jump to it)
   right after the hero; combinations compact (for example the three smallest by seat count shown, the rest one line
   each or behind one control).
4. Supervisor: the hemicycle does not draw clean party wedges (an NZ First column runs down the centre with a Labour
   dot inside it). Order seats so each party is one contiguous wedge, blocs on their sides. Review nit: the majority
   marker over near-black NZ First dots needs a contrasting underlay. Both in home_graphics.py, so home's hemicycle
   must still look right (look at home 390 and 1280 too).
5. Supervisor: "Source updated 00:00 on 2024-11-10 (source local time; timezone unverified)" reads as an internal note;
   say it the way a reader needs it, without claiming a timezone the source does not give.
Not in this round: review Important 2 (overlapping historic electorate cells) goes to the hexmap change, which replaces
the layout.

Tests on main at 51c94ce stay untouched except where a presentation assertion pins markup this round changes; the
branch's own tests move with it. Done when: the three failing cases pass in a browser you can launch (if Chromium
cannot launch, say so and give the reasoning), the rest of that host list still passes, bin/lint ok, commit, no push.
