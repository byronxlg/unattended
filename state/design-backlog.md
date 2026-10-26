# Design backlog

Newest first. The supervisor adds the three weakest things on the site once a day ("Design loop" in
`prompts/supervisor.md`) and Byron's design feedback verbatim; the top item is the next UI change.

## 2026-10-26 (Byron, issue #103, Telegram 17:47Z, verbatim)

"Let's make a dedicated funding page. That's interesting"
Page plan intent/nz-election/pages/funding.md; build nz-election-funding-page on the 27 Oct share.

## 2026-10-26 18:07Z (PR #102 second fresh review nits)

- vote/: closing sentence packs three voting methods before "7pm"; slow to scan at 390.
- vote/: deadlines sit after all five help options, apart from the actions they qualify.

## 2026-10-26 18:00Z (supervisor, PR #102 fix-1 host screenshots)

- vote/ deadlines block: "Voting in New Zealand; Uploads of completed overseas voting papers; Voting by registered
  telephone-dictation voters: 7pm NZ time, 7 November" reads as one joined label; give it a plain sentence.
- vote/ help section: "Overseas voting begins on 21 October" stays present tense after the date (phase copy).

## 2026-10-26 (PR #101 fresh review nits)

- vote/: deadline paragraphs repetitive and dominate the phone help section; label column leaves whitespace beside
  long answers at 1280; repeated source wording adds height on mobile. Next vote/ change after #101.

## 2026-10-27 (supervisor, from PR #99 host screenshots)

- vote/ "Am I enrolled, and is it too late?" still reads "Enrol or update your details by midnight at the end of
  25 October" on 27 Oct, after enrolment closed. Phase copy, on main before #99: past tense once the close has passed,
  and say what a reader who missed it can still do (only what the EC sources state). Next vote/ change. In PR #100.
- vote/ (PR #99 second fresh review nits): source credit sits far from the countdown and timeline; help rows
  leave large gaps under short answers at 1280; long deadline lines compete with the instructions. Next vote/ change
  after #99 and #100 merge.

## 2026-10-26 (Byron, issue #92, Telegram 02:35Z, verbatim)

"It's better. I feel like there is a lot of small text. And the party funding total is hidden in a
paragraph which I feel should be promoted"

In the next change: nz-election-type-scale (dispatched 02:5xZ 26 Oct): type-scale tokens with a 16 px
reading floor, funding total as a headline figure on parties/. Not turned into a gate or a measure
(Design loop); judged by eye from screenshots.

## 2026-10-26 (redesign, Claude)

1. Electorate pages (`electorates/<slug>/`) still use the pre-redesign layout: bring them onto
   DESIGN.md (hero with holder and margin, candidate cards with photos, the hex map with the seat
   highlighted).
2. Parties, vote and night pages: same, page anatomy and components from DESIGN.md.
3. Hex map shape: the square-tile snapshot drawn with offset rows looks ragged in the north; a
   hex-native layout (`snapshots/hexmap.json` with axial coordinates) would read as New Zealand.
