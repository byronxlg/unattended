# L-a2: look follow-up and seats on the home (build round)

PR #33 (L-a, the 538 look) merged as 85c3b14 on Byron's word ("Just merge freely. Then send me
the link to get feedback."). This round carries what its reviews found, plus the change that makes
the home show seats at all. You are in `.worktrees/nz-election-look-a2` on
`change/nz-election-look-a2` from 85c3b14. Read `AGENTS.md`, `intent/nz-election/look-538.md`,
`intent/nz-election/spec.md` (the averaging paragraph, amended today), then
`product/nz_election/pipeline/{build.py,average.py,seats.py,home.py}`,
`product/nz_election/web/styles.css`, `product/nz_election/config/seat-groups.json`.

## Items

1. Bloc colours. Government (National, ACT, NZ First) is coral and Opposition (Labour, Green,
   Te Pati Maori) is blue, directly above a seat bar where National is blue and Labour red: a
   reader matches the wrong colours. Swap: Government blue (the `left`/blue token or a renamed
   one; your choice), Opposition coral/red. The supervisor's earlier brief assigned them wrongly.
2. Seat bar order. Segments are ordered by party size, so the majority marker does not show
   either group crossing it. Order Government parties first, then others (grey), then Opposition,
   so the "N needed" marker reads against the groups the headline names.
3. Social page label. Replacing the social heading with a question removed the visible "Proof of
   concept" label once the page is populated (`pipeline/build.py` near 536 at 85c3b14). Keep the
   question heading and add a persistent notice band (the pale yellow band from look-538.md)
   saying it is a proof of concept with its sample size and date range, in both empty and
   populated states.
4. Section marker. The current-section marker in the section nav follows `:target`
   (`web/styles.css` near 31), so after scrolling it stays on the last clicked section. Either
   update it progressively from the visible section with a small script (plain anchors still
   work with JS off, and with JS off no section is marked current) or drop the current marker;
   your choice, say which.
5. Others as remainder (unblocks seats). The live home shows "Seat estimate unavailable ...
   Incomplete party coverage" because Talbot Mills rows (2026-01 to 2026-08) and Anacta rows
   (2026-09-10, 2026-10-10) leave Others blank on Wikipedia, so average.py marks every window
   since 2026-07-18 incoherent. The spec's averaging paragraph now carries the exception: when
   a row names every party but Others is blank, derive Others as 100 minus the named parties
   for that row only, when the remainder is between 0 and 10 points; label the row derived on
   /polls/ (and in the published exclusions/derivations data), and name the rule and the
   affected pollsters on the methods page. Never derive a named party; a remainder outside the
   bound leaves the row as today (incoherent, disclosed). Then the home topline, seat bar and
   coalition browser render real seats on current data.
   `coalitions_browser.py` currently fails at `check_unassigned_after_unavailable_allocation`
   on main (the fieldset is hidden because seats are withheld); after this item it should pass;
   if it still fails, say why rather than editing the check.

## Contracts

Main's tests at 85c3b14 stay as they are except where an item above moves a contract by design
(the bloc colour tokens, the bar order, the social heading text, the coherent-vector rule now
admitting derived Others); move those assertions to the new behaviour, never weaker, and list
each moved assertion in your summary. Add tests: topline group colours match the seat bar's
party colours; bar segment order follows the groups; the populated and empty social page both
show the proof-of-concept band; Others derivation (blank Others derived within bound, out of
bound stays incoherent, a blank named party is never derived, derived rows are labelled in the
output data).

## Done when

In the worktree: `uv run --with pytest pytest -q product/nz_election` passes,
`uv run product/nz_election/pipeline/verify.py all` prints `PASS all`, `bin/lint` prints
`lint ok`, and a build on the current live polls fixture shows a seat topline (say the numbers
in your summary). Commit on the branch, do not push, do not commit last.md. The supervisor runs
the screenshot harness and coalitions_browser.py on the host.
