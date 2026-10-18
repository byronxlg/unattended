# NZ election: the 538 look (issue #32)

Byron, Telegram 2026-10-18 20:35Z (issue #32): "https://web.archive.org/web/20250305135954/https://projects.fivethirtyeight.com/2024-election-forecast/
can you make the unattended nz election site look like this. Focus on ui today"

Accepted by the supervisor 2026-10-18T21:00Z. It supersedes the type, colour and heading rules of
`design.md` where they conflict; NBC's module order from `home.md` (#26) stays. Two increments:
L-a, the look (this brief); L-b, the seat simulation proof of concept that the 538 signature
graphics need (dot histogram, path to 61, scenarios as "N out of 100").

## L-a: the look, site-wide

Subject: a reader opening the site in the four weeks before 7 November wants to know who is
favoured to form the next government and how sure anyone can be. 538's form answers that with a
question per module, a quiet page and one big data graphic. We take the form, not the marks.

Tokens (replace the `design.md` tables; contrast test asserts every pairing, both modes):

| Token | Value | Use |
|---|---|---|
| paper | #FFFFFF | ground |
| ink | #222222 | text; thin rules between modules |
| grey | #6B6B6B | dek, attribution, axis ticks (check 4.5:1) |
| rule | #949494 | hairlines that carry a boundary (3:1); no decorative rules |
| left | #2F6DB5 muted blue, the left bloc (Labour, Green, Te Pāti Māori) in topline text and bloc graphics |
| right | near #D9534F | coral red, the right bloc (National, ACT); nearest coral passing 4.5:1 as text on paper |
| notice | #FFF6CC pale yellow band for status notices (stale data, proof of concept, freeze) |
| focus | keep #005EA8 ring |

Bloc colours are interface data colours for bloc-level text and graphics only; party colours
(`config/party-colours.json`) stay for party-level fills. NZ First and the Opportunity Party are
not assigned to a bloc in colour: grey, labelled, until a coalition statement assigns them (the
coalitions config already records statements; use it, do not invent).

Type: Libre Franklin (OFL) for headings and body, weights 400 and 700, and one OFL mono (IBM Plex
Mono or JetBrains Mono, 400) for timestamps, axis ticks, counters and table figures. Self-hosted
woff2, Latin plus Latin Extended-A subset (macrons), `font-display: swap`, licence files committed
next to the fonts. The fonts count against the 100 KB first-view budget (the 45 KB reserved in
`design.md` is now spent; raise nothing else). The timestamp line may be small caps in the mono
("Updated 19 Oct 2026, 9:40 am NZDT"), that is the one caps treatment; no tracked caps labels.
Scale: h1 40/44 bold desktop, 30 phone; module question h2 20 bold; dek 18; body 16; mono 13.

Layout:

- Hero centred in a narrow column (max about 640 px) on the home page only; modules below
  left-aligned in the 1120 px column. Thin ink rule above each module, generous whitespace, no
  cards, no shadows, radius zero.
- Hero order: mono timestamp; question headline "Who is favoured to form the next government?";
  one-line dek; the topline as two or three large sentences coloured by bloc stating what the poll
  average gives, e.g. "Left bloc: 58 seats" / "on the current poll average, 61 needed" / "Right
  bloc: 60 seats". No "N times out of 100" until L-b's simulation exists; the sentences use seats
  from the existing allocator, with the provenance note under them as now.
- Every home module heading becomes a question: "What are the latest polls?", "How have the
  polls moved?", "Which electorates are closest?", "Which parties are near the 5 percent
  threshold?", "What do prediction markets say?", "When is election night?". Pick wording for the
  rest in the same voice.
- A sticky section nav at the bottom on phone and top under the masthead on desktop: one short
  text label per home module (no icons needed), current module marked, 44 px targets, plain
  anchors, works without script (script may only add the current marker).
- Masthead: site name plus route tabs (Overview, Polls, Electorates, Night, Methods) as 538's race
  tabs.
- Tables (polls, closest races, threshold watch): mono figures, right-aligned, hairline rows, a
  "See all polls" link at the foot.
- Status notices (stale feed, proof of concept, freeze) use the notice band.
- Other routes take the tokens, type and question headings; no layout rework beyond that.

Not this: the 538 or ABC logo, the mascot, any 538 illustration, Franklin Gothic or bc-sklonar,
copied copy. Probabilities without a model.

Checks: all of `design.md` "Budgets and checks" still bind (first view under 100 KB with the
fonts, CSS under 12 KB raw (raise to 16 KB only if the build shows it is needed, and say so),
axe zero violations, contrast test, viewport budget: the topline and its provenance note above
780 px at 360 and 390). Screenshots of home, polls/, an electorate page and night/ at 360, 390
and 1280 are part of done; the fresh review judges them against the 538 page.

Contracts that move with this change: tests that pin the old font stack, old token values, old
heading text or the old CSS budget figure move to the new values in the same commit, never
weaker (a budget may move only by the stated amount). Byte, contrast, axe and viewport checks
keep their strength.

## L-b: seat simulation proof of concept (after L-a)

Monte Carlo over the poll average: per-party vote share with sampling error from the polls'
spread, the 5 percent threshold, electorate seats held from 2023 unless an electorate poll says
otherwise, Sainte-Laguë with overhang through the existing allocator, 10,000 draws seeded by the
data run. Output a seat distribution per bloc. Graphics: dot histogram of bloc seat totals with a
centre line at 61, "path to 61" snake, scenarios list as "N out of 100". Route labelled Proof of
concept with the method, the draw count and its limits (poll error is larger than sampling
error). Promoted to the hero only after a look at its numbers and a judgement line to Byron.
