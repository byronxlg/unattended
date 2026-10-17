# Plan brief: NZ election feed home (Build stage, plan mode)

You are the engineer in the unattended lab (read AGENTS.md and product/nz_election/AGENTS.md).
This job writes the plan for the change `nz-election-home`. Your sandbox is read-only and has no
network: your final message IS the deliverable. The supervisor copies it verbatim into
intent/nz-election/plan-home.md, so write one complete markdown document, title on the first
line, nothing before or after it, under 260 lines. Write for an engineer who never saw this
conversation and will implement from the plan alone in a fresh context, in a worktree, with no
network, one increment per PR.

Read first, in this order: intent/nz-election/home.md (the intent and spec; requirements H1 to
H12; the design section resolves "Nothing is a card"), intent/nz-election/design.md (tokens,
states, source notes, budgets: PR #21 shipped them), intent/nz-election/spec.md ("Supervisor
resolutions" overrides its body), intent/nz-election/plan-m2.md (what shipped in increments 4,
5, 6 and what increment 7 will add: markets.json and the daily workflow, a separate change),
then the code as it is: product/nz_election/pipeline/build.py (route registry, rendering, the
home sentence, source_note), verify.py (check registry, MISSING_SOURCE, SMALL_TARGET),
export.py and publish.py (which families exist and their "Not available" contract),
web/templates/*.html, web/styles.css, web/*.mjs, tests/ (conftest, test_contracts.py, the
route-count pins, screenshots.py and its image counts), config/*.json, runbook.md, REVIEW.md.
Do not write files, do not run anything that mutates.

## What the plan must contain

1. Fragment and route inventory: every id on today's home template and partials, every anchor a
   test or template links to, every route-count and image-count pin in tests and
   screenshots.py, with the file and line. State which move to `/polls/`, which the home keeps,
   and the new counts (routes 79, images: say the number, OG images per route included).
2. Template structure: the partials you will split out of polls.html so the seat strip, party
   rows and threshold watch render identically on `/` and `/polls/` (H3); the new home.html
   module order per the spec table; the night.html copy (H6); the electorate.html change (H7);
   the og.html per-route variants (H8) and how screenshots.py writes `og/<route>.png` and how
   build.py references them with absolute URLs without running a browser.
3. Data joins for the modules, each with its empty and "Not available" rendering: countdown
   from the build time in Pacific/Auckland (H2; name the function and its three fixed-time
   tests); averages per party for the poll module (H4); the electorate selection rule (H5:
   six smallest 2023 winning margins on unchanged boundaries from baseline-2023.json and the
   correspondence config, candidates from candidates.json; say exactly which fields and how
   "incumbent" is derived or, if it cannot be derived from published data, that the marker is
   omitted and the spec is amended); the social aggregate for the home module (H9); markets
   optional.
4. CSS: the module rule, the two-column electorate rows and four-column directory grid at the
   existing breakpoints, the tabs list, all within styles.css under the existing tokens; the
   byte budget check for the home (under 200 KB HTML plus CSS) as a test.
5. Navigation change (H10) and its effect on every page's nav markup and the nav tests.
6. Verification and test inventory: new test files and functions, verify.py check names and
   PASS lines, the screenshot command with route and image counts, `bin/lint`, host-run
   commands marked as such.
7. Build order as a checklist (`- [ ] ` items) in at most three increments, each a PR, each
   closing with `bin/lint` and the full test run and naming its proving command and expected
   output line. Suggested: increment H-a the `/polls/` move with partials, the home feed with
   seats, polls, electorates, directory and method modules, navigation, tests; increment H-b
   night copy, electorate page order, OG per route, screenshots; social module in whichever
   increment the data join makes cheapest. Reorder if the files say otherwise and say why.
   Prefer one increment if the diff would stay under about 1,200 lines.
8. `## Concerns`: anything in the spec you cannot implement as written with the route you would
   take; what in the current code must change, not just grow, and the test that guards it.

Decisions already made (do not reopen): no bundler, no runtime libraries, no fonts, no
headshots, no rating labels, the design tokens and "no cards as boxes" resolution in home.md,
the countdown rendered by the build, `/polls/` keeps every fragment, product code reaches main
only by PR, data families unchanged.
