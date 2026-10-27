# Design backlog

Newest first. The supervisor adds the three weakest things on the site once a day ("Design loop" in
`prompts/supervisor.md`) and Byron's design feedback verbatim; the top item is the next UI change.

## 2026-10-27 09:10Z (supervisor, PR #109 host screenshots)

- funding/ at 390 is about 21,000 px: every return listed in one column; group by party behind jump links or a per-party disclosure (data stays on the page).

## 2026-10-27 08:30Z (PR #105 fresh review 2 nits)

- funding/ at 1280: the timeline (pace of arrival) begins below the first screen (styles.css:533).
- funding/ at 390: tables scroll sideways to compare donor, amount and date (styles.css:529-530).
- funding/ at 390: the party ranking fills the first screen; the biggest-donor answer gets little invitation.

## 2026-10-27 08:20Z (supervisor, PR #105 fix-1 host screenshots)

- Home "Where do the parties stand?" cards at 390: share wraps ("28.5" then "%"), change wraps ("-0." then "4").
  In nz-election-parties-credit with backlog item 2.
- funding/: "Te Tai Tokerau" appears as a party row; check what the return is.

## 2026-10-27 07:55Z (PR #104 fresh review nits, PR #105 supervisor look)

- night/ at 390: intro spacing pushes the seat answer low; majority threshold stated in answer, graphic and caption;
  electorate navigation below the first phone screen (night_page.py:78, :85, :88).
- Sitewide 390 nav still two rows after funding/ (Overview Polls Parties Funding / Electorates Vote Night); item 1
  below stays open.
- funding/: party totals shown with cents in the top line; whole dollars read better.

## 2026-10-26 20:15Z (supervisor, design-loop critique, deployed site 1280 and 390)

1. Sitewide at 390: the masthead nav wraps to two rows (Night and Methods alone on the second), so the header
   takes about 160 px of the first screen on every page. The funding page adds an eighth link and would make it
   worse. Next UI change: rides with nz-election-funding-page (note added to its brief); options are a shorter
   label set or Methods moved to the footer, not smaller type (16 px floor) or links pushed off screen.
2. parties/ at 390: the portrait credit block ("New Zealand Labour Party. CC BY-SA 4.0. Square crop, resized to 320
   pixels and converted to WebP.") sits between the leader and the polling number, ahead of the party's answer.
   Credit belongs in a small line under the card or on Methods; the processing note is not reader copy.
3. night/ replay at 390: "updated 00:00" reads as midnight, not a replay frame; the bloc label "Labour, Green and
   Maori" wraps to three lines beside 55. Short bloc names (as home uses: Opposition, Government) and a frame
   label that says it is the 2023 final count.

Also seen, a data question not a design one: home seats sum to 133 (59 + 67 + TOP 7) with 67 for a majority;
check the overhang arithmetic in the seat projection before election night.

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
