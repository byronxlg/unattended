# night: page plan

status: draft
route: `/unattended/nz-election/night/`
research job: `state/jobs/research-nz-election-page-questions/last.md`

## Readers and their questions

Search, home, news-link and shared-result arrivals from 19:00 NZDT on 7 November; returning readers through the week after (the lab ends 14 Nov; official results are due 27 Nov, the page states the date).

1. Who has enough seats? - from 19:00 7 Nov - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/
2. How complete and current is this? - same - evidence: https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf
3. Who is ahead in my electorate? - same - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/
4. Could this change, and when is it final? - from 8 Nov - evidence: https://elections.nz/media-and-news/2023/official-results-for-the-2023-general-election

## Answers

1. Seat bar with the 62 line: "These combinations currently reach a majority; government formation is separate."
2. "Results cover N percent of voting places, updated HH:MM." Never labelled votes counted.
3. Electorate table: leader, margin, reporting status, linking each electorate page.
4. Status line: "Preliminary; official results due 27 November", then the preliminary to official change.

## Data, worked back

1 to 3. Pipeline: electionresults.govt.nz XML (M3 increments 2, 4, 5), 30 second polling in the client, dated fallback snapshot and official link when the feed is unreachable; EC copyright.
4. Fetch once: EC calendar; pipeline: official-results capture when published (M3 increment 4).
Before 19:00: countdown and the replay rehearsal, labelled as a replay, never as live.

## Page order

At 390, above the fold: 2 as one line, 1 as the seat bar. Then 3 (searchable table), then 4. Before results: the countdown line and a link to vote/.

## Not shown

A replay presented as live, assumed special-vote totals, coalition agreements inferred from arithmetic.

## Question test

From a 390x844 screenshot of the populated replay state a reviewer answers 1 and 2 in five seconds each and finds their electorate (3) in one scroll.
