# Spec brief: NZ Election 2026 (Design stage)

You are the engineer in the unattended lab (read AGENTS.md). This job writes spec.md for the
product change `nz-election`. Your sandbox is read-only: your final message IS the deliverable.
The supervisor copies it verbatim into intent/nz-election/spec.md, so write one complete
markdown document, title on the first line, nothing before or after it, under 300 lines.
Write for a plan job and then a builder who never saw this conversation.

Read first, in this order: intent/nz-election/intent.md (the "Supervisor decisions" and
"Constraints" sections bind; the "Open questions" each state a preferred answer: take it unless
you find a concrete reason not to, and record the reason), intent/research/nz-election-data-sources.md
(the whole file; it settles which hosts are scriptable, licences, the XML feed schema, the
2023 fixture numbers, the boundary files and sizes), docs/playbook.md (Stage 2), REVIEW.md,
.github/workflows/pages.yml and bin/blog (how site/ is built and deployed today), AGENTS.md
(the Design section), posts/README.md (voice). You may run read-only commands to confirm
shapes: `curl -sI https://electionresults.govt.nz/electionresults_2023/xml/election.xml`,
`curl -s "https://en.wikipedia.org/w/api.php?action=parse&page=Opinion_polling_for_the_2026_New_Zealand_general_election&prop=wikitext&format=json&formatversion=2" -A "unattended-lab/0.1 (github.com/byronxlg/unattended)" | head -c 4000`,
and the ArcGIS query in research section 3 with `returnCountOnly=true`. Do not write files.

## What the spec must contain

1. Requirements, numbered, grouped by the four views in the intent and by the data pipeline.
   Each requirement names the source (table row in the research file), the licence line the UI
   shows for it, and how it is verified (a command with expected output, or a screenshot).
   M1 and M2 requirements are marked; M3 and M4 are listed with less detail.
2. Data pipeline design: one scheduled Actions workflow per cadence (hourly polls and markets;
   daily electorate and campaign data; 30 s polling is browser-side on the night, not Actions).
   Each job: inputs, the JSON files it writes (path, schema as a short example, a `source` and
   `fetched_at` field on every file), failure behaviour (keep the last good file, write
   `status.json`), and how a deploy is triggered. Decide the data branch question and write
   down the consequence for pages.yml.
3. Site layout: URL for every page under the existing Pages site (the blog lives at
   `/unattended/`; propose the sub-path), the directory layout under `product/nz_election/`
   (pipeline, tests, fixtures, `web/` static source) and how the Pages build copies `web/` and
   data into `site/`. No bundler: plain HTML, CSS and ES modules; any vendored library named
   with size and licence. Prefer SVG drawn from simplified GeoJSON over map tiles.
4. Allocator: s191 to s193 as a pure function with its signature, the 2023 fixture it must
   reproduce exactly (party votes, quotients, electorate seats in, seats out, overhang 2,
   House 122) and the edge cases (threshold with and without electorate seat, exhausted list,
   independents reducing 120, ties).
5. Design section, applying AGENTS.md Design and the brief below: a compact token system
   (4 to 6 named colours as hex, with party colours as a separate semantic set taken from the
   parties' own identities), typeface choices and roles (system or self-hosted; no webfont CDN;
   name the file and licence if self-hosted), type scale, layout concept per view with an ASCII
   wireframe at phone width and desktop width, alignment rules, and what the one memorable
   element is. Mobile first. The hero of the polls view is the thing a reader came for: the
   current seat picture, not a headline about the app.
6. Provenance: how every number carries its source and time (a shared component, its markup),
   and the downloads page listing every JSON and CSV with the run that produced it.
7. Accessibility and quality floor: keyboard focus, reduced motion, colour contrast for party
   colours on both themes if two themes, text alternatives for the map, works with JS disabled
   for the static tables where feasible.
8. Testing: unit tests for allocator, poll parser (against committed wikitext fixture), XML
   feed parser (against committed demo files), GeoJSON simplification check; a Playwright
   script that screenshots each page at 390x844 and 1280x800 into a known directory; the
   command for each and its expected output.
9. Concerns: a `## Concerns` section listing every risk or ambiguity you found with a proposed
   resolution, each one flagged for the supervisor to accept or change. Include at least:
   Wikipedia table drift, Pages deploy frequency and quota, the share-alike obligation on the
   derived poll table, the 2026 feed ids, and what happens if the XML WAF exemption closes.
10. Out of scope: what the spec deliberately leaves out and why (Policy.nz, Hansard, census
    profiles until a source clears).

## Design brief

Subject: the 2026 New Zealand general election under MMP, for NZ voters and politics watchers
reading on their phones between now and 7 November, and on the night. The job of the page is to
answer "who is winning, by how much, and where does that number come from" faster than any
news site, and to let anyone take the data. The vernacular to draw from: the orange of the
Electoral Commission's own voting campaign, the proportional bar of 120 seats, the shape of the
country, ballot-paper plainness. Avoid the generic defaults: no cream-and-terracotta, no dark
page with one acid accent, no identical rounded cards with the same shadow, no tracked-out
caps eyebrows, no middle-dot meta strings, no arrows on links, no decorative numbering, no
page-load animation on every section. Spend boldness in one place and name it. Every label is
a plain sentence-case phrase a voter would use (party vote, electorate, seats, poll, source).
