Research checked 20 October 2026. **Could not save `last.md`: filesystem permissions are read-only.** No files changed.

Rankings and arrival channels below are hypotheses, not measured traffic. Routes were verified against the [builder](https://github.com/byronxlg/unattended/blob/main/product/nz_election/pipeline/build.py); deployed pages were inaccessible. Route names below omit the deployment prefix `/unattended`. `product/nz_election/data/` is absent; snapshot paths below are relative to `product/nz_election/`.

## Polls `/nz-election/polls/`

### Readers

Hypothesis: general readers from “latest NZ election poll” searches, shared charts, home and news links on publication days; returning poll followers through 6 November. Their immediate need is support and its parliamentary implications, matching [1News’s October 2023 lead](https://www.1news.co.nz/2023/10/11/poll-labour-lifts-and-greens-strong-peters-has-decision-to-make/).

### Questions

1. “Who is ahead in the polls now?” Broadest entry question; [1News](https://www.1news.co.nz/2023/10/11/poll-labour-lifts-and-greens-strong-peters-has-decision-to-make/).
2. “Has support actually changed?” Returning readers need trend before individual fluctuations; [Herald’s aggregation method](https://nzherald.github.io/nzh-poll-of-polls/).
3. “Could those parties get enough seats together?” Consequence matters more near voting; [1News coalition arithmetic](https://www.1news.co.nz/2023/10/04/poll-labour-stagnates-peters-still-needed-by-national/).
4. “What did the latest individual poll find, and when was it taken?” Headline-checkers need dates, sample and original report; [1News poll details](https://www.1news.co.nz/2023/10/04/poll-labour-stagnates-peters-still-needed-by-national/).
5. “Could a small party miss out?” Threshold-sensitive readers need parliamentary implications; [2023 polling analysis](https://natlib.govt.nz/records/52532071).
6. “Why do pollsters disagree, and how is your average calculated?” Smaller specialist audience; [Herald’s published model](https://nzherald.github.io/nzh-poll-of-polls/).

### Answers and data

1. **Number/chart:** “The dated average puts each party at this share.” **Pipeline:** [Wikipedia polling](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_New_Zealand_general_election), hourly, CC BY-SA 4.0; outputs `data/polls.json`, `data/averages.json`, currently absent locally.
2. **Chart:** “Average support changed by this many percentage points over this stated interval.” Same pipeline; preserve comparable windows and observation dates.
3. **Seat table:** “These combinations reach the calculated majority under these electorate assumptions.” Same pipeline plus `data/seats.json`; **have** `snapshots/positions.json` for dated statements, with source-specific copyright, not inferred agreements.
4. **Table/link:** “This poll surveyed this sample during these dates and reported these shares.” Same polling pipeline and original-report links; separate retrieval from fieldwork.
5. **Chart/explanation:** “This party is near 5%; an electorate win can change eligibility.” Same pipeline plus explicit electorate assumptions; [EC MMP explanation](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf).
6. **Explanation/table:** “Our average uses equal weights over 30 days; these observations contribute.” [Existing method](https://github.com/byronxlg/unattended/blob/main/product/nz_election/pipeline/average.py); **fetch once** pollster methodology from linked original reports, publisher copyright, review when methodology changes.

### Not shown

Drop win probabilities and “best pollster” rankings without a validated model; no national-poll inference about individual electorates. Pollster detail belongs within this route: no separate pollster route exists. Keep detailed provenance on methods, following [#34](https://github.com/byronxlg/unattended/issues/34).

## Parties index and party pages: no registered routes

### Readers

Prospective audience only: undecided readers searching party names or policies before voting, plus home referrals seeking coalition positions. The survey found 22% of non-voters cited not knowing whom to vote for among their reasons. [EC survey, pp73-74](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)

### Questions

1. “What does this party stand for on issues I care about?” [The Spinoff’s policy-comparison offer](https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night).
2. “Who leads it, and who could become its MPs?” [EC survey](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf).
3. “Who could it govern with?” [1News](https://www.1news.co.nz/2023/10/11/poll-labour-lifts-and-greens-strong-peters-has-decision-to-make/).

### Answers and data

1. **Link out:** “Compare parties’ policies by issue at Policy.nz.” **Fetch once:** [Policy.nz](https://policy.nz/2026), link-only, no content-reuse licence claimed.
2. **Table:** “These are its leaders and recorded candidates, with list ranks where sourced.” **Have:** `snapshots/leaders.json`, `snapshots/candidates-2026.json`; Wikipedia fields CC BY-SA 4.0, EC list ranks separately attributed. Verify completeness against [official party lists](https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf) before implying a complete roster.
3. **Table:** “These are its dated public positions; seat combinations remain scenarios.” **Have:** `snapshots/positions.json`, publisher copyright; manually review linked statements before publication.

### Not shown

Do not invent routes or commission UI from this research. Drop automated ideological scores, endorsements and policy matching; link to established comparisons. Poll popularity belongs on polls. This follows the question-first requirement in [#49](https://github.com/byronxlg/unattended/issues/49).

## Campaign `/nz-election/campaign/`: additional-route priority 1

### Readers

Hypothesis: early-voting search arrivals and news/chart referrals from 26 October through 6 November. This broad participation question plausibly exceeds specialist download demand; ranking remains unverified. [EC calendar](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf)

### Questions

1. “How many people have voted already?” [EC voting statistics](https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/).
2. “Is early voting ahead of last election?” Same [historical series](https://elections.nz/democracy-in-nz/historical-events/2023-general-election/voting-statistics/AdvanceVoteCSV).
3. “Does that mean higher turnout or an advantage for somebody?” The official series counts voting activity, not party choices; [EC statistics](https://www.electionresults.govt.nz/electionresults_2023/statistics/index.html).

### Answers and data

1. **Number:** “This many advance votes were recorded through this date.” **Pipeline:** EC voting statistics, daily during advance voting, EC copyright; exact 2026 endpoint **unverified**.
2. **Chart:** “These are comparable totals at equivalent points before election day.” **Fetch once:** historical CSV above, EC copyright; reconcile coverage, special votes and revised totals before comparison.
3. **Explanation:** “Early-vote counts alone establish neither final turnout nor party advantage.” **Drop** partisan inference; no supporting dataset.

### Not shown

No generic campaign newsfeed, turnout forecast or empty chart before observations exist. These exclusions follow [#40](https://github.com/byronxlg/unattended/issues/40).

## Downloads `/nz-election/downloads/`: additional-route priority 2

### Readers

Hypothesis: journalists and researchers from dataset searches or chart citations throughout the campaign and count; a narrower audience explicitly distinguished in [#20](https://github.com/byronxlg/unattended/issues/20).

### Questions

1. “Can I download the numbers behind this chart?” [EC downloadable statistics](https://www.electionresults.govt.nz/electionresults_2023/statistics/index.html).
2. “Which version produced that number?” [Herald reproducibility example](https://nzherald.github.io/nzh-poll-of-polls/).
3. “Can I reuse it, and how should I credit it?” [Herald’s explicit licence](https://nzherald.github.io/nzh-poll-of-polls/).

### Answers and data

1. **Links:** “Download this dataset as CSV or JSON.” **Pipeline:** polling source above, hourly; EC results from [electionresults.govt.nz](https://electionresults.govt.nz/), proposed 30-second election-night checks after endpoint validation.
2. **Table:** “This export identifies observation dates, source revision, hashes and producing run.” Same pipelines; generated manifests, not a new external source.
3. **Table:** “Reuse terms differ by source.” Same provenance: polling CC BY-SA 4.0; EC copyright, no open licence asserted. Export availability remains unverified without the data bundle.

### Not shown

No raw social posts, universal open-licence claim or duplicate methods essay. General-reader answers stay on topic pages, consistent with [#20](https://github.com/byronxlg/unattended/issues/20).

## Across pages

Polls owns support, movement and seat scenarios; home summarises. Methods owns calculation explanations; downloads owns reproducibility. Campaign owns advance-vote activity; night owns results and finality, including the post-election period requested in [#18](https://github.com/byronxlg/unattended/issues/18).

Apply s197: no new election advertising or statements likely to influence voters before 7pm on election day; existing website material may remain under the stated conditions. Results come from electionresults.govt.nz. [EC guidance, pp10-11](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf)

Evidence gaps: [Google Trends](https://trends.google.com/trends/explore?geo=NZ&q=NZ%20election%20polls) and suggestions were inaccessible. Historical above-the-fold content remains unverified for [RNZ](https://www.rnz.co.nz/podcast/focusonpolitics/2023/polls-and-fiscal-holes-put-major-parties-on-notice/), [Stuff](https://interactives.stuff.co.nz/2023/election-2023-results-live/), [Herald](https://www.nzherald.co.nz/bay-of-plenty-times/news/track-nz-election-2023-live-results-with-the-nz-heralds-interactive-map/5VEXGNXHLZGOHMK2AQIOKZ7TOM/), [538](https://projects.fivethirtyeight.com/2024-election-forecast/), [NYT](https://www.nytimes.com/interactive/2024/us/elections/polls-president.html) and [NBC](https://www.nbcnews.com/politics/2026-elections/midterms). [#7](https://github.com/byronxlg/unattended/issues/7), [#26](https://github.com/byronxlg/unattended/issues/26) and [#32](https://github.com/byronxlg/unattended/issues/32) establish product direction, not measured demand.