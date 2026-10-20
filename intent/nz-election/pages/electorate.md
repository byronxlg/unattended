# electorate: page plan

status: draft
route: `/unattended/nz-election/electorates/<name>/`
research job: `state/jobs/research-nz-election-page-questions/last.md`

## Readers and their questions

Search arrivals for "<electorate> candidates", local shares and home referrals before voting; result checkers on election night.

1. Who can I vote for here? - before voting - evidence: https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf
2. Is this my electorate? - before voting - evidence: https://vote.nz/2026-general-election/voting-in-the-election/what-to-do
3. What do these candidates stand for? - undecided - evidence: https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night
4. Who won last time, and by how much? - interested readers - evidence: https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night
5. Who is leading here now? - first from 19:00 NZDT 7 Nov - evidence: https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/

## Answers

1. Candidate table: name, party, list rank where one exists.
2. One line: "Check your enrolled electorate at vote.nz" and the boundary map link.
3. Link to Policy.nz for this electorate.
4. 2023 result on its then boundaries (winner, margin), labelled when boundaries changed.
5. On the night: leader, margin, reporting status.

## Graphics

1. Candidates - race card per candidate: party colour bar, name large, party, list rank, incumbent tag - reference: https://www.nbcnews.com/politics/2026-elections/midterms ("Senate battlegrounds" race cards) - keeps: card anatomy, party colour as the first read - changes: initials or party mark, no headshots without a licence.
2. Where it is - a locator map of the electorate on the NZ outline at card size - reference: https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/ (state map) - keeps: one strong shape, no chrome - changes: boundary geometry fetched once.
4. 2023 result - horizontal bars of candidate vote share in party colours with the margin annotated - reference: https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/ ("What are the closest races?" margin bars) - keeps: thick bars, direct labels - changes: labelled as 2023 boundaries where they changed.

## Data, worked back

1. Have: `snapshots/candidates-2026.json` (CC BY-SA 4.0); fetch once a reconciliation against the EC candidate release.
2. Fetch once: vote.nz link; `snapshots/hexmap.json` is schematic, never an address lookup.
3. Fetch once: Policy.nz link, no ingestion.
4. Have or fetch once: 2023 EC results (EC copyright), boundary comparability; Port Waikato from its snapshot.
5. Pipeline: night family, electorate results.

## Page order

At 390, above the fold: electorate name, candidate table (1), the "is this mine" line (2). Then 3, then 4. On the night 5 goes to the top.

## Not shown

Competitiveness ratings from old margins, national polls as local polls, enrolment as turnout.

## Question test

From 390x844 alone a reviewer answers 1 and 2 in five seconds each and finds 3 within one scroll.
