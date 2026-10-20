# Research: what readers want from the polls and parties pages (reader-first page plans, round 2)

Byron, Telegram 2026-10-20 01:41Z: "Make sure research and planning is done before making the ui.
Start with what will a user be interested in seeing and work back." Round 1 covered home, vote,
electorate and night (`state/jobs/research-nz-election-page-questions/last.md`; read it, do not repeat
it). This round covers the live pages that get a plan before their next UI change. The supervisor
writes one page plan per page from your findings (`intent/page-plan-template.md`). You research; you
do not design or write code.

## Read first
- `intent/page-plan-template.md`, `intent/nz-election/pages/home.md` (an accepted-shape example)
- `state/jobs/research-nz-election-page-questions/last.md`, `intent/nz-election/audiences.md`
- `product/nz_election/data/` and `product/nz_election/snapshots/` listings (what data we have)
- the route list the site builds (grep the build for registered routes) to name the live pages exactly

## Pages, in this order
1. polls `/nz-election/polls/` (poll average, individual polls, pollster detail)
2. party pages and the parties index, if the site has them (name the routes you find)
3. any other live route a reader reaches from search, ranked by likely arrivals; at most two more

## For each page
- Who arrives, from where (search, social share, home, a news link), on which day.
- The questions they bring, in the reader's words, ranked by how many readers have them and how much
  they matter on the day, at most seven, each with evidence URLs: Google Trends or search suggestions
  for NZ election terms, the Electoral Commission's voter and non-voter survey (2023), what RNZ, Stuff,
  NZ Herald, 1News and The Spinoff led their 2023 election and results pages with, what 538, NYT and
  NBC put above the fold, Byron's issues on byronxlg/unattended (#7 #18 #20 #26 #32 #34 #40 #49).
- For each question: the one-sentence answer form (number, chart, map, table, link out) and the data
  it needs, marked have (path under data/ or snapshots/), fetch once (source URL, licence), pipeline
  (source URL, cadence), or drop (why).
- What readers expect that the page should leave out, and why.

## Constraints
- Read-only. Web live. Cite every claim with a URL; mark anything you could not verify as unverified.
- NZ specifics: Electoral Act s197 (no election advertising or statements likely to influence voters on
  election day before 7 pm); results feed is electionresults.govt.nz.
- No raw social posts or handles in your output.

## Output (your final message, saved as last.md)
One section per page with the headings: Readers, Questions (ranked numbered list, each line with
evidence URLs), Answers and data, Not shown. Then a short "Across pages" section: questions that
belong on more than one page and which page should own them. Under 1,200 words.
