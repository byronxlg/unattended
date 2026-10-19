# nz-election-look-b: absent means absent, and look like the reference

Byron, issue #40 (Telegram 2026-10-19 04:46Z, 04:47Z): "It still looks no where near as good as the reference."
"There is a real problem with it saying data not available. In that case just don't show it. I want this to
look great. Do better." Read `gh issue view 40` in full (operator evidence and the concrete list), `gh issue view 32`
(the reference: FiveThirtyEight's 2024 presidential forecast page), intent/nz-election/design-principles.md, and
product/nz_election/snapshots/ with pipeline/snapshots.py (leaders, candidates, enrolment, Port Waikato 2023,
history, hexmap, positions: fetched this morning, render from them).

This is a visual round. It replaces measures-first rounds: the test is a side-by-side look at 1280 and 390.

## 1. Absent means absent (a rule with a check)

- A field, row, card or module with no data is not rendered. No "Not available", "Unavailable", "pending",
  "Withheld", "missing", "not supplied" (any case) on any public page except methods/; the reason goes to
  methods/ or the build log. An empty module is dropped with its nav link.
- Build check (verify.py or the visible-text tool, your choice) that fails on those strings in built HTML
  outside methods/; show it failing on main and passing on your head.
- Electorate and party pages: no provenance blocks; one "Sources and method" link per module, as home has.
- Tests and harness contracts that pin the old placeholder text or old page structure move with this change;
  nothing that checks a real property (accessibility, overflow, budgets, fragments, provenance reachable from
  methods/) is weakened. Say in last.md which assertions moved and why.

## 2. Home, at reference weight

- Hero is a graphic first: one large answer line in the display face, then the seat-outcome graphic (seat bar
  by bloc with the 61-seat majority line, or a dot plot of plausible outcomes under the stated averaging),
  large enough to be the first thing seen at 390.
- A map: the hexmap snapshot, every electorate coloured by 2023 holder's party colour, margin as shade, a
  legend, links to the electorate page, an accessible table equivalent. This is the page's centre of gravity.
- Charts: party trend lines 3 px plus, party-coloured, end labels in the text face, shaded ranges where the
  data has them, real axes; electorate margins in party colours, not grey.
- People: party leaders with photos from the snapshot (licence credit in Methods, a short credit line where
  the licence needs it).
- Type and rhythm: one display face at large sizes for headings and the answer; mono only for small numeric
  labels, never for prose; generous section spacing; each module one strong graphic plus one sentence. No
  all-caps eyebrows. Keep the existing party colours and the committed fonts (or one added display face
  under the font budget, self-hosted, licence recorded).

## 3. Electorate page: one screen to the point

At 1280 the first screen answers: who holds it, by how much (2023 margin), who is standing in 2026 (candidate
rows with party colour, list rank where known, photo for sitting MPs), and where it is (its hex highlighted on
the small map or its geometry). Target under 2,500 px at 1280 for a typical electorate (nelson). Port Waikato
uses the 2023 by-election snapshot.

## Constraints

- Static site, no new runtime dependencies, node_modules unchanged. Byte and font budgets stay enforced
  (raise one only with the number and the reason in last.md).
- Fragment IDs that exist on main stay resolvable.
- Commit in the worktree, do not push, do not commit last.md.

## Done when

`uv run --with pytest pytest -q product/nz_election` passes, `bin/lint` ok, `verify.py all` PASS, the new
absent-text check fails on main and passes on head, the screenshot harness passes (if Chromium is blocked in
your sandbox, say so; the supervisor runs it), and last.md lists the commit, the moved assertions, the nelson
page height at 1280, and the pages you looked at.

## Carried from PR #41 review

The compact electorate footnote (pipeline/electorate_pages.py:33-35) dropped the stale and refresh-failed
warning. Keep freshness honest without placeholder text: a module whose family is overdue or failed shows
its as-of date ("Data to 18 October") in its one footnote line; the warning detail lives on methods/.
