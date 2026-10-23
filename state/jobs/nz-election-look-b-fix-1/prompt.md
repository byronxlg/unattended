Follow-up 1 on nz-election-look-b (build thread, same worktree). Host Chromium works for the supervisor:
`uv run --with pytest product/nz_election/tests/screenshots.py --site /tmp/look-b/after --out /tmp/lookb-shots`
on 92da3e8 stopped at the first page with AXE nested-interactive: `svg.tile-map` has role="img" and contains 71
focusable <a> tiles. Screenshots of home and Nelson at 1280 and 390 were looked at by the supervisor; the layout
direction is right. Fix these, one commit, tests on main at b3badcd stay unweakened (this branch's own tests move
with it):

1. Tile map accessibility: no interactive content inside an element with role img. Keep the 71 links keyboard
   reachable and the accessible table; e.g. role="group" with the label, or role img on a non-interactive wrapper
   with the links outside it. Add a build-time check (verify.py or a test) that rejects focusable descendants of
   any role="img" element, shown failing on 92da3e8.
2. Tile labels read "Mt Albert (2023): Labour Party, 18 votes". Say what the number is: "majority of 18 votes"
   (aria-label and <title>).
3. Te Pāti Māori tiles (#D12C38) are indistinguishable from Labour (#D82C20) in the map and legend. Use a colour
   for Te Pāti Māori that differs clearly from Labour at a glance (check the site's party palette and the
   design principles; change it consistently wherever party colours are defined, with contrast checks still passing).
4. Electorate page winner name shows the raw EC form "BOYACK-MAYER, Rachel Elizabeth" while the candidate list
   says "Rachel Boyack". Show the winner in natural order (given name then surname, normal case; use the
   candidate snapshot's display name when the same person is standing, else title-case the EC form). Keep the EC
   form in Methods records.
5. Electorate page copy "All these electorates remain unchanged from their 2020 boundaries and names." reads as
   a list note on a single-seat page; say it for this seat ("Nelson's boundaries and name are unchanged from 2020.")
   or omit it where it does not apply.

Done: pytest product/nz_election passes; bin/lint ok; verify.py all PASS on the populated build; the new role-img
check fails on 92da3e8 and passes on HEAD; rebuild the populated site to /tmp/look-b/after so the supervisor can
rerun the browser harness. Report in last.md (uncommitted), no push.
