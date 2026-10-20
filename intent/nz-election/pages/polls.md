# polls: page plan

status: accepted 2026-10-20T23:00Z
route: `/unattended/nz-election/polls/`
research job: `state/jobs/research-nz-election-page-questions-2/last.md`

## Readers and their questions

General readers from "latest NZ election poll" searches, shared charts, the home and news links on poll-release days; returning followers to 6 November. Ranks are hypotheses (search data was not reachable), set by what NZ outlets lead with.

1. Who is ahead in the polls now? - everyone, release days - evidence: https://www.1news.co.nz/2023/10/11/poll-labour-lifts-and-greens-strong-peters-has-decision-to-make/
2. Has support actually changed? - returning readers - evidence: https://nzherald.github.io/nzh-poll-of-polls/
3. Could those parties get enough seats together? - near voting - evidence: https://www.1news.co.nz/2023/10/04/poll-labour-stagnates-peters-still-needed-by-national/
4. What did the latest poll find, and when was it taken? - headline checkers - evidence: https://www.1news.co.nz/2023/10/04/poll-labour-stagnates-peters-still-needed-by-national/
5. Could a small party miss out on the 5% threshold? - threshold-sensitive readers - evidence: https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf
6. Why do pollsters disagree, and how is the average made? - specialists - evidence: https://nzherald.github.io/nzh-poll-of-polls/

## Answers

1. "The dated average puts each party at this share": one row per party with the average and its date, largest first.
2. "Average support moved by this many points since <date>": a trend chart of the average with the individual polls as dots.
3. "These blocs reach 61 seats on this average under these electorate assumptions": the seat bar, Government vs Opposition, with the majority line.
4. "This poll surveyed this sample over these dates and reported these shares": a table of recent polls, newest first, linked to the original report.
5. "This party is near 5%; an electorate win changes eligibility": the threshold line on the trend chart plus one sentence per party within two points of it.
6. A link to the Methods section on the average (equal weights over 30 days) and the pollster list; no essay here.

## Graphics

1. Party averages - horizontal bars with direct labels and the value at the bar end - reference: https://projects.fivethirtyeight.com/2024-election-forecast/ (polling averages module) - keeps: party colour fill, direct labels in the text face, one dated caption - changes: up to eight parties, MMP threshold mark at 5%.
2. Trend - lines for the average with poll dots behind at low opacity - reference: https://projects.fivethirtyeight.com/polls/president-general/2024/national/ (polling average chart) - keeps: full content width, thick average lines, labels at each line's last point, dots for polls - changes: NZ party colours, 5% threshold rule, gaps where no poll exists.
3. Seats - one stacked seat bar by bloc with the 61 majority marker - reference: https://projects.fivethirtyeight.com/2024-election-forecast/ (electoral vote bar) - keeps: bar height and the majority label above it - changes: 120-plus seats with overhang, blocs per 2023 agreements, derived Others disclosed.

## Data, worked back

1, 2, 4, 5. Pipeline (have): Wikipedia polling table, hourly, CC BY-SA 4.0, `data/polls.json` and `data/averages.json`.
3. Pipeline (have): `data/seats.json` from the same average; `snapshots/positions.json` for dated statements, publisher copyright.
6. Have: `pipeline/average.py` method on Methods. Pollster methodology: drop (fetch once only if a reader question asks for it).

## Page order

At 390, above the fold: 1 (party averages with the date), then 2 (trend). Then 3 (seats), 5 (threshold sentences, only parties within two points), 4 (recent polls table), 6 (one link line to Methods). Every existing fragment id on polls/ is kept.

## Not shown

Win probabilities and pollster ratings (no validated model); electorate inferences from national polls (electorate pages own that); preferred-PM polls (not asked first); the full source history (Methods owns it, issue #34).

## Question test

Each graphic is screenshotted beside its reference at the same width and does not read weaker. From 390x844 alone a reviewer answers 1 and 2 in five seconds each and reaches 3 with one scroll; from 1280x800 every ranked question is answered without passing an unrelated section. The fresh review logs the answers it read off.
