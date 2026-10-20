# home: page plan

status: draft
route: `/unattended/nz-election/`
research job: `state/jobs/research-nz-election-page-questions/last.md`

## Readers and their questions

General readers from search, shared graphics and news links before 7 November; results seekers from 19:00 NZDT on 7 November (then question 5 moves to first and the page hands over to night/).

1. Who looks ahead, and could they get enough seats? - everyone, any day to 7 Nov - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/, https://github.com/byronxlg/unattended/issues/26
2. What changed in the latest polls? - returning readers - evidence: https://github.com/byronxlg/unattended/issues/7
3. When can I vote, and am I running out of time? - rises to 25 Oct (enrolment) and 7 Nov - evidence: https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/, https://vote.nz/2026-general-election/about/overview/key-dates
4. Who is standing where I live? - local arrivals - evidence: https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night
5. Who is winning now, and how much is counted? - first from 19:00 NZDT 7 Nov - evidence: https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/

## Answers

1. Seat bar: "On the poll average these combinations reach 62 of 122; this is not who forms government." One graphic.
2. Party trend chart with the dated latest polls and the change since the previous average.
3. One line with a link out: "Enrol by 25 October; advance voting from 26 October; election day 7 November."
4. Electorate picker (link list or select) to the electorate page.
5. On the night: national seats, percent of voting places reported, update time, link to night/.

## Data, worked back

1. Have: polls family (Wikipedia, CC BY-SA 4.0, hourly pipeline) and allocator.
2. Have: polls family, same cadence; fieldwork dates kept apart from publication and retrieval.
3. Fetch once: EC key dates (https://vote.nz/2026-general-election/about/overview/key-dates), EC copyright, link and dates only; reviewed daily to 7 Nov.
4. Have: `snapshots/candidates-2026.json`, electorate route list.
5. Pipeline: night family (M3 increments 2 to 5), electionresults.govt.nz.

## Page order

At 390, above the fold: date line (3), seat bar and its one-sentence answer (1). Then: poll trend and latest polls (2), electorate picker (4), the rest (markets, social POC) only if each answers a ranked question; otherwise they move off the home. On the night the night summary (5) replaces the seat bar at the top.

## Not shown

Downloads catalogue, a news feed, win probabilities without the seat simulation POC, empty modules (#20, #34, #40). Methods and sources live on methods/ and sources pages, linked once.

## Question test

From the 390x844 screenshot alone a reviewer answers 1 to 3 in five seconds each; from 1280x800 every ranked question without passing an unrelated section. The fresh review logs the answers it read off.
