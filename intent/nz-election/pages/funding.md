# funding: page plan

status: accepted 2026-10-27T07:14Z (Byron silent since the 26 Oct 18:07Z NOTE)
route: `/unattended/nz-election/funding/`
research job: `state/jobs/research-nz-election-page-questions-2/last.md` (parties Q5); Byron's ask in issue #103

## Readers and their questions

Journalists and engaged readers following the parties/ "Who funds it?" block or the home link,
and readers who saw a donation story in the news (returns over NZD 20,000 are published by the EC
within ten working days of receipt, so new rows arrive through the campaign). Ranks are
hypotheses from Byron's ask (#103) and the parties research; no search data was reachable.

1. Which party has declared the most in large donations this cycle, and how do they compare? - journalists, engaged readers - evidence: https://github.com/byronxlg/unattended/issues/103, https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-over-20000/
2. Who are the biggest donors, and to whom? - journalists, readers after a news story - evidence: https://github.com/byronxlg/unattended/issues/103
3. Is the money arriving faster as election day nears? - journalists - evidence: https://github.com/byronxlg/unattended/issues/103
4. How many returns has each party declared? - engaged readers - evidence: https://github.com/byronxlg/unattended/issues/103
5. Can I see every return and the EC document behind it? - journalists checking a figure - evidence: https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-over-20000/

## Answers

1. "ACT has declared NZD <x> across <n> donations over NZD 20,000 this year, the most of any party": one ranked bar chart of declared totals by party, with the caveat "returns over NZD 20,000, not total party funding" beside the headline.
2. "The largest single donation is NZD <x> from <donor> to <party> on <date>": a table of the ten largest donations, donor, party chip, amount, received date.
3. "<n> of <m> declared donations were received since <date>": a cumulative declared total by received date, one line per party with three or more returns.
4. "<party>: <n> returns": the count printed on each bar of chart 1, no separate graphic.
5. The full list, newest first, each row linking its EC document, grouped by party with an anchor per party (`#<party_id>`) so parties/ can link straight to its group.

## Graphics

1. Declared totals - horizontal ranked bar chart, party colour, amount and return count labelled at the bar end - reference: https://projects.fivethirtyeight.com/2024-election-forecast/ (bar modules, direct labels in the text face) - keeps: thick bars, direct labels, no axis box, dated caption - changes: NZ party colours from DESIGN.md, NZD amounts.
2. Over time - cumulative step line per party by received date - reference: https://projects.fivethirtyeight.com/2024-election-forecast/ (polling averages module) - keeps: thick line, end labels in the text face, dated caption - changes: steps not smoothing, parties with fewer than three returns omitted and named in the caption.
3. Top ten - a table, not a graphic.

## Data, worked back

1 to 5. Have: `product/nz_election/snapshots/donations.json` (PR #55, 146 of 146 EC index rows at 2026-10-20T08:46Z, party_id, amount, received, document_url), EC copyright, no open licence stated; credit line on the page. Refresh: fetch once again in the build if the EC index lists more returns, else the page states the retrieval date. `document_checked` false rows are listed, never excluded.

## Page order

At 390: heading and one-sentence answer to 1 with the caveat and retrieval date; chart 1 (answers 1 and 4); then the top ten table (2); then chart 2 (3); then the full list by party (5); then the EC credit and licence line. Above the fold: the headline sentence and chart 1. Linked from the home feed and from each party's "Who funds it?" block on parties/ (to `funding/#<party_id>`).

## Not shown

Donations under NZD 20,000 and candidate donations (not in the EC index); totals from annual
returns (published after the election); any per-voter or per-seat ratio (no method, invites a
misleading reading); commentary on donors.

## Question test

Each graphic is screenshotted beside its reference at the same width and does not read weaker.
From 390x844 alone a reviewer answers 1 and 4 within five seconds, and 2 after one scroll; from
1280x800 questions 1 to 4 are answered without passing an unrelated section. The fresh review
logs the answers it read off.
