# Research: what readers want from each page (reader-first page plans)

Byron, Telegram 2026-10-20 01:41Z: "Make sure research and planning is done before making the ui.
Start with what will a user be interested in seeing and work back." The supervisor will write one
page plan per page from your findings (`intent/page-plan-template.md`). You research; you do not
design or write code.

## Read first
- `intent/page-plan-template.md` (the sections your findings feed)
- `intent/nz-election/audiences.md` (17 Oct audience research; build on it, do not repeat it)
- `intent/nz-election/intent.md`, `intent/nz-election/schedule.md`
- `product/nz_election/data/` listing and `product/nz_election/snapshots/` (what data we already have)

## Pages, in this order
1. home `/nz-election/` (now to 7 Nov, and election night)
2. vote `/nz-election/vote/` (new: how, where, when to vote; advance voting opens 26 Oct)
3. electorate `/nz-election/electorates/<name>/` (arrivals from search for "<electorate> candidates")
4. night `/nz-election/night/` (results on 7 Nov from 19:00 NZDT, and the week after to the official count)

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
belong on more than one page and which page should own them. Under 1,500 words.
