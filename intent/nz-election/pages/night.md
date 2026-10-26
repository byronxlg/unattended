# night: page plan

status: accepted 2026-10-20T14:33Z
route: `/unattended/nz-election/night/`
research job: `state/jobs/research-nz-election-page-questions/last.md`

## Readers and their questions

Search, home, news-link and shared-result arrivals from 19:00 NZDT on 7 November; returning readers through the week after (the lab ends 14 Nov; official results are due 27 Nov, the page states the date).

1. Who has enough seats? - from 19:00 7 Nov - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/
2. How complete and current is this? - same - evidence: https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf
3. Who is ahead in my electorate? - same - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/
4. Could this change, and when is it final? - from 8 Nov - evidence: https://elections.nz/media-and-news/2023/official-results-for-the-2023-general-election

## Answers

1. Seat hemicycle with the majority line: "These combinations currently reach a majority; government formation is separate."
   A jump to electorate search follows the hero. The electorate search and table follow before the detailed seat arithmetic. The three smallest winning combinations then appear as compact cards with party chips, seat totals and a majority mark; all combinations sit behind one control.
2. "Results cover N percent of voting places, updated HH:MM." Never labelled votes counted.
3. Electorate table: leader, margin, reporting status, linking each electorate page. Search precedes the map; filtering hides the map so the matching leader stays beside the search within one scroll. The provisional-status and original-boundary caveats stay visible while filtering. Clearing the search restores map-first browsing.
4. Status line: "Preliminary; official results due 27 November", then the preliminary to official change.

## Graphics

1. Seat answer - the shared home hemicycle (one dot per seat), live, with the reporting share beside the bloc totals - reference: https://www.nbcnews.com/politics/2026-elections/midterms ("Battle for control") - keeps: majority marker, totals in the display face - changes: live preliminary counts.
2. Reporting - one thick progress bar of voting places reported with the update time - reference: https://www.nbcnews.com/politics/2026-elections/midterms (hero status line) - keeps: one number, large - changes: voting places, never "votes counted".
3. Electorates - the home hex map coloured by current leader, shade by margin, uncounted grey, above the table - reference: https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/ ("Who's favored to win each state?") - keeps: map first, table second - changes: leader on the night, not a rating.

## Data, worked back

1 to 3. Pipeline: electionresults.govt.nz XML (M3 increments 2, 4, 5), 30 second polling in the client, dated fallback snapshot and official link when the feed is unreachable; EC copyright.
Graphic 3: have `snapshots/hexmap.json` (the home hex layout).
4. Fetch once: EC calendar; pipeline: official-results capture when published (M3 increment 4).
Before 19:00: countdown and the replay rehearsal, labelled as a replay, never as live.

## Page order

At 390, above the fold: 2 as one line, 1 as the seat hemicycle. Then 3 (searchable table), then 4. Before results: the countdown line and a link to vote/.

## Not shown

A replay presented as live, assumed special-vote totals, coalition agreements inferred from arithmetic.

## Question test

From a 390x844 screenshot of the populated replay state a reviewer answers 1 and 2 in five seconds each and finds their electorate (3) in one scroll.
