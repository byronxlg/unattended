# L-a follow-up 1 (build round, same thread)

Your stop on the bloc topline was right: the brief said a coalitions config records statements,
and none exists. That was the supervisor's error. The supervisor now supplies the grouping, and it
is a fact with a source, not a prediction:

- Government (coral, the `right` token): National, ACT, NZ First. Source: the 2023 coalition
  agreements (National-ACT and National-NZ First, 24 November 2023),
  https://www.beehive.govt.nz/ or Wikipedia "Sixth National Government of New Zealand"; cite
  the Wikipedia article as the source chip, as the site does for polls.
- Opposition (blue, the `left` token): Labour, Green, Te Pati Maori (macron as the site spells it).
- Every other party: grey, labelled, as now.

Do:

1. Record the grouping in one small committed config under `product/nz_election/` (your choice
   of file and shape), with the source URL and the date of the arrangement, read by the build.
   No other party membership is inferred anywhere.
2. Replace the reader-visible "Bloc totals unavailable: coalition statements have not been
   supplied." (`pipeline/build.py:184`) with the topline the brief describes: "Government
   parties: N seats" / "on the current poll average, M needed" / "Opposition parties: N seats",
   coloured by group, plus one caption line: "Grouped by the 2023 coalition agreements, not by
   any 2026 commitment." Totals come from the allocator output already on the page; when
   seats are withheld (incomplete party coverage) the topline says so in plain words, never an
   internal message.
3. A test that the topline totals equal the sum of the grouped parties' allocator seats, and a
   test that no reader-visible string mentions config or "supplied".
4. Host harness on 28c8771: PASS 79 routes 296 images. Looked at home 390 and 1280: the hero
   lists seven grey party lines at headline size under the internal message. After this round
   the hero holds the two group sentences and the needed line only; per-party seats stay in the
   seat bar and table below. coalitions_browser.py fails at
   check_unassigned_after_unavailable_allocation here and on main; leave it, a separate change
   owns it.

Contracts: main's tests at 091c449 stay as they are except where this grouping moves an
assertion you already moved on this branch; this branch's own tests move with it. Nothing weaker.

Done when, in the worktree: `uv run --with pytest pytest -q product/nz_election` passes,
`uv run product/nz_election/pipeline/verify.py all` prints `PASS all`, `bin/lint` prints
`lint ok`. Commit on the branch, do not push, do not commit last.md. The supervisor runs the
screenshot harness on the host.
