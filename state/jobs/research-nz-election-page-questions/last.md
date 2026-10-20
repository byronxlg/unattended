Research checked 20 October 2026. Rankings and arrival routes below are hypotheses, not measured site traffic. No files changed: the read-only workspace prevented saving `last.md`.

## Home `/nz-election/`

### Readers

General readers arriving through search, shared graphics and news links before 7 November; results seekers that evening. Prioritise analysis here while keeping voting help reachable, consistent with [#20](https://github.com/byronxlg/unattended/issues/20) and [#26](https://github.com/byronxlg/unattended/issues/26).

### Questions

1. “Who looks ahead, and could they get enough seats?” Before polling day, the main analysis question; [1News’s final-poll coverage](https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/) connected polling to parliamentary combinations.
2. “What changed in the latest polls?” Returning readers need movement and dates; supported by the analysis remit in [#7](https://github.com/byronxlg/unattended/issues/7).
3. “When can I vote, and am I running out of time?” Deadline urgency rises through 25 October; Google ranked “How to vote” first among NZ’s 2023 trending how-to searches. [Google](https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/)
4. “Who is standing where I live?” Local entry point; The Spinoff promoted electorate profiles alongside policy comparisons. [Coverage plan](https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night)
5. “Who is winning now, and how much is counted?” Becomes first after 19:00 NZDT on 7 November; “Election Results” ranked third among 2023 trending news searches. [Google](https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/)

### Answers and data

1. **Chart:** “These poll-based seat scenarios show which combinations reach a majority, not who will form government.” **Pipeline:** [poll observations](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_New_Zealand_general_election), hourly, CC BY-SA 4.0; require dated inputs and allocation assumptions.
2. **Chart:** “Support changed by this amount between these dated observations.” Same pipeline; distinguish fieldwork dates from publication and retrieval.
3. **Link out:** “Enrol by 25 October; advance voting begins 26 October.” **Fetch once:** [official dates](https://vote.nz/2026-general-election/about/overview/key-dates), EC copyright, no open licence stated; review daily through voting.
4. **Link/table:** “Choose your electorate to see its candidates.” **Have:** `snapshots/candidates-2026.json`, Wikipedia-derived names CC BY-SA 4.0, EC list-rank fields separately attributed.
5. **Numbers:** “These are the current preliminary seats, reporting progress and update time.” **Pipeline:** night’s results source and cadence below; share its dataset.

### Not shown

No downloads catalogue as the main answer, duplicate news feed, unsupported win probabilities or empty modules. These exclusions follow [#20](https://github.com/byronxlg/unattended/issues/20), [#34](https://github.com/byronxlg/unattended/issues/34) and [#40](https://github.com/byronxlg/unattended/issues/40).

## Vote `/nz-election/vote/`

### Readers

Task-focused search arrivals, home referrals and shared practical links: enrolment questions through 25 October, overseas questions from 21 October, domestic voting questions from 26 October through 7 November. These moments follow the [official calendar](https://vote.nz/2026-general-election/about/overview/key-dates).

### Questions

1. “Where can I vote today, and when is it open?” Locations led additional information requests in survey table 25. [Survey, p38](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)
2. “Am I enrolled, and is it too late?” Rank first through 25 October because missing the deadline prevents participation; registration also appeared in Google’s trending searches. [Dates](https://vote.nz/2026-general-election/about/overview/key-dates), [Google](https://blog.google/intl/en-nz/products/2023_12_year-in-search-heres-what-kiwis/)
3. “What do I bring, and how do my two votes work?” Only 56% of enrolled non-voters knew they could vote without an EasyVote card. [Survey, p34](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)
4. “How do I vote overseas or get help if I cannot attend?” Smaller audience, high consequence; practical-access barriers appeared among non-voters’ reasons. [Survey, p74](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)
5. “Where can I compare candidates and policies?” Not knowing whom to vote for was a reason for 22% of non-voters. [Survey, pp73-74](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)

### Answers and data

1. **Link out:** “Use the official finder for places and opening hours.” **Fetch once:** destination from [Vote NZ](https://vote.nz/2026-general-election/voting-in-the-election/what-to-do); daily link review, no copied venue database.
2. **Link out:** “Check enrolment now; the deadline is 25 October.” **Fetch once:** official calendar and enrolment destination.
3. **Short explanation/link:** “You have a party vote and an electorate vote; follow these official preparation instructions.” **Fetch once:** [official guidance](https://vote.nz/2026-general-election/voting-in-the-election/what-to-do).
4. **Links:** “Choose overseas, assisted or accessible voting instructions for your circumstances.” **Fetch once:** [overseas guidance](https://vote.nz/2026-general-election/overseas/vote-from-overseas) and [accessible formats](https://vote.nz/2026-general-election/resources/information-in-accessible-formats); include NZ-time deadlines.
5. **Link out:** “Compare policies and candidates at Policy.nz.” **Fetch once:** [destination](https://policy.nz/2026), reviewed weekly; no ingestion.

All EC guidance retains EC attribution; no open licence asserted. Independently summarise and review operational guidance daily.

### Not shown

Drop a local eligibility engine, stored addresses and copied opening hours: official services own these changing answers. Drop policy recommendations; offer comparisons instead. [Official guidance](https://vote.nz/2026-general-election/voting-in-the-election/what-to-do)

## Electorate `/nz-election/electorates/<name>/`

### Readers

Primarily hypothesised “electorate candidates” search arrivals before voting, followed by local shares and home referrals; result-checkers on election night. Local-result demand is supported by the [Herald’s national-and-electorate map](https://www.nzherald.co.nz/bay-of-plenty-times/news/track-nz-election-2023-live-results-with-the-nz-heralds-interactive-map/5VEXGNXHLZGOHMK2AQIOKZ7TOM/).

### Questions

1. “Who can I vote for here?” Candidate knowledge is a documented barrier. [Survey](https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf)
2. “Is this my electorate and roll?” Correct identification precedes choosing candidates. [Official voting guidance](https://vote.nz/2026-general-election/voting-in-the-election/what-to-do)
3. “What do these candidates stand for?” Policy comparison accompanied local profiles in [The Spinoff’s coverage](https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night).
4. “Who won last time, and is this close?” Local-contest interest is evidenced by those battleground profiles, not proof of current competitiveness. [The Spinoff](https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night)
5. “Who is leading here now?” Becomes first after results begin; 1News explicitly offered national and local tracking. [1News](https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/)

### Answers and data

1. **Table:** “These candidates contest this electorate.” **Have:** `snapshots/candidates-2026.json`; **fetch once** reconciliation against [EC’s candidate release](https://elections.nz/media-and-news/2026/candidate-and-party-lists-released), EC copyright; review corrections.
2. **Link out:** “Check your enrolled electorate with Vote NZ.” **Fetch once:** official destination; `snapshots/hexmap.json` is schematic, unsuitable for address lookup.
3. **Link out:** “Read candidate comparisons at Policy.nz.” **Fetch once:** relevant [comparison destination](https://policy.nz/2026); link-only.
4. **Table:** “This was the previous contest on its then-current boundaries.” **Fetch once:** [2023 results](https://www.electionresults.govt.nz/electionresults_2023/statistics/index.html), EC copyright, and boundary comparability; **have:** `snapshots/port-waikato-2023.json` for that separate by-election.
5. **Table:** “This candidate leads by this many votes at this reporting stage.” **Pipeline:** electorate results, same source/cadence as night.

### Not shown

Drop inferred competitiveness from old margins, national polls presented as local polls, and enrolment totals presented as turnout. Missing local evidence cannot answer these questions. [EC statistics definitions](https://www.electionresults.govt.nz/electionresults_2023/statistics/index.html)

## Night `/nz-election/night/`

### Readers

Search, home, news-link and shared-result arrivals after 19:00 NZDT, 7 November; returning readers from 8 November through the official count on 27 November. [Dates](https://vote.nz/2026-general-election/about/overview/key-dates)

### Questions

1. “Who has enough seats?” National outcome first. [1News](https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/)
2. “How complete and current is this?” Essential context for preliminary totals. [EC media kit](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf)
3. “Who is ahead in my electorate?” Local outcome next. [1News](https://www.1news.co.nz/2023/10/12/tonights-1news-final-leaders-debate-what-you-need-to-know/)
4. “Could this change, and when is it final?” Moves first after election night; 2023 official results changed seats and electorate outcomes. [EC release](https://elections.nz/media-and-news/2023/official-results-for-the-2023-general-election)

### Answers and data

1. **Seat table:** “These combinations currently reach a majority; government formation remains separate.”
2. **Numbers:** “Results cover this percentage of voting places, updated at this time.” Do not label places as votes counted.
3. **Table:** “Here are electorate leaders, margins and reporting status.”

For 1-3, **pipeline:** [electionresults.govt.nz](https://electionresults.govt.nz/), proposed 30-second polling; exact public 2026 XML endpoint/CORS remains unverified. EC copyright, no open licence stated; retain dated fallback snapshots and an official link.

4. **Status/table:** “These results remain preliminary; official results are due 27 November.” **Fetch once:** calendar; **pipeline:** daily official-status review and event-driven replacements, preserving election-night totals for comparison. [EC calendar](https://vote.nz/2026-general-election/about/overview/key-dates)

### Not shown

No simulated replay presented as live, assumed daily special-vote totals, or coalition agreements inferred from arithmetic. [Counting explanation](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf)

## Across pages

Home owns polling; vote owns practical instructions; electorate owns candidate detail; night owns result status. Others summarise and link.

For s197, freeze potentially influential additions and promotion from midnight until 19:00 NZDT; existing material may remain. Neutral voting information can continue. [EC guidance](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf)

Evidence limits: [Trends](https://trends.google.com/trends/explore?date=2023-10-01%202023-11-30&geo=NZ&q=election%20results,where%20to%20vote,how%20to%20vote) was inaccessible. Exact historical folds remain unverified for [RNZ](https://www.rnz.co.nz/news/election-2023/500185/election-2023-labour-s-chris-hipkins-concedes-congratulates-national-on-results), [Stuff](https://interactives.stuff.co.nz/2023/election-2023-results-live/), [538](https://projects.fivethirtyeight.com/2024-election-forecast/), [NYT](https://www.nytimes.com/interactive/2024/11/05/us/elections/results-president.html) and [NBC](https://www.nbcnews.com/politics/2026-elections/midterms). [#32](https://github.com/byronxlg/unattended/issues/32) establishes inspiration, not audience evidence; [#49](https://github.com/byronxlg/unattended/issues/49) requires questions first.

Inventory: seven snapshots inspected; `data/` absent. No live bundle claimed. Post-election ownership must cover 27 November, beyond [#18’s](https://github.com/byronxlg/unattended/issues/18) minimum operating week.