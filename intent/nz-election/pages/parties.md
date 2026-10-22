# parties: page plan

status: accepted 2026-10-22T06:10Z
route: `/unattended/nz-election/parties/` (new; one section per party, anchored `#<party_id>`)
research job: `state/jobs/research-nz-election-page-questions-2/last.md`

## Readers and their questions

Undecided readers searching a party name before they vote (26 October to 7 November), and readers
following a home or polls link to a party. Ranks are hypotheses (search data was not reachable);
the EC survey found 22 percent of non-voters gave not knowing whom to vote for as a reason.

1. What does this party stand for on the issues I care about? - undecided voters, advance voting - evidence: https://thespinoff.co.nz/politics/13-10-2023/election-2023-how-were-covering-the-big-night
2. Who leads it, and who could become its MPs? - undecided voters - evidence: https://elections.nz/assets/2023-General-Election/voter-and-non-voter-survey-2023.pdf
3. Who could it govern with? - everyone near voting - evidence: https://www.1news.co.nz/2023/10/11/poll-labour-lifts-and-greens-strong-peters-has-decision-to-make/
4. How is it polling, and is it near the 5% threshold? - home and polls referrals - evidence: https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf
5. Who funds it? - journalists and engaged readers - evidence: https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-over-20000/

## Answers

1. "Compare its policies by issue at Policy.nz": one link out per party, no policy text copied.
2. "Led by <name>; <n> list candidates, top five: ...": portrait, leader name, the top of the list with ranks, a link to the EC party list.
3. "It has said <dated statement>": the dated positions with the source link; seat combinations stay on polls/.
4. "Polling <x> percent on the <date> average, <up|down> <y> since <date>": one number and a sparkline with the 5% rule.
5. "Declared <n> donations over NZD 20,000 this year totalling NZD <z>": one number, the largest three donors with dates, a link to the EC returns.

## Graphics

1. Polling - sparkline with the 5% threshold rule and the current value labelled at the line end - reference: https://projects.fivethirtyeight.com/2024-election-forecast/ (polling averages module, small-multiple form) - keeps: thick line, direct label in the text face, dated caption - changes: one per party, NZ party colour, threshold rule.
2. Leader - portrait at the reference's card weight - reference: https://www.nbcnews.com/politics/2026-elections/midterms (candidate cards) - keeps: square crop, name under the photo, party colour rule - changes: credit line for the licence.
Others: none: answers 1, 3 and 5 are a link, a dated quote and a number.

## Data, worked back

1. Fetch once: Policy.nz party URLs, link only, no reuse licence claimed.
2. Have: `snapshots/leaders.json` (portraits, CC BY-SA and credits), `snapshots/candidates-2026.json`; the EC party lists PDF for ranks, completeness checked against it before any count is shown.
3. Have: `snapshots/positions.json`, publisher copyright, quoted briefly with link.
4. Pipeline (have): `data/averages.json`, hourly, CC BY-SA 4.0.
5. Have: `snapshots/donations.json` (PR #55), EC copyright; `document_checked` false rows shown as listed, never excluded.

## Page order

At 390: party picker (one row of party colour chips linking to the anchors), then per party in
current-average order: name and leader portrait, 4 (polling number and sparkline), 3 (positions),
1 (Policy.nz link), 2 (top of list), 5 (donations number). Above the fold: picker and the first
party's polling number. Nothing else on the page.

## Not shown

Ideological scores, endorsements and policy matching (no validated method, Policy.nz does it);
full candidate rosters (electorate pages own candidates); seat scenarios (polls/ owns them);
party histories (Wikipedia does it better).

## Question test

Each graphic is screenshotted beside its reference at the same width and does not read weaker.
From 390x844 alone a reviewer finds a named party and answers 1 to 3 for it within five seconds
each after one tap on the picker; from 1280x800 every ranked question for the first party is
answered without passing an unrelated section. The fresh review logs the answers it read off.
