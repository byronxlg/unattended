# Fix 2: vote/ source credits from the records actually drawn

The fresh review of PR #101 (review-nz-election-vote-nits) requests changes. One Important item:

`product/nz_election/pipeline/vote_page.py:44-47`: the source credits filter records on `source_url`,
while the graphics (countdown, timeline) draw any record with a `date`. So:

- an election-day record without `source_url` still draws the countdown, which carries
  `aria-describedby="source-countdown"`, but no element with that id is emitted (dangling reference);
- timeline records without URLs lose their description the same way;
- a drawn record without a URL is left out of the retrieval-date choice, so the credit can show an
  older retrieved date (20 October) than a drawn record has (26 October).

Invariant: provenance (credit text, retrieved date) is selected from the records the graphic actually
draws, and every `aria-describedby` id the page emits resolves to an element on the same page. A
record without a URL is credited as plain text (no link), not dropped. Where this is enforced: the
page's own output; the accessibility checks in the screenshot harness and test_design.

Keep 8eac454's contract: before `#help` the first screen allows only snapshot action urls as links
(test_vote_page.py:44), so date credits there stay plain text.

Constraints: fix job. Tests on main at the base sha are not edited. Add regression tests on this
branch: (a) election-day record without `source_url` gives no dangling `aria-describedby`; (b) all
timeline records without URLs, same; (c) the retrieved date credited is the newest among drawn
records. Each fails on 8eac454 and passes on your commit. Test the reference resolution and the date,
not markup or class names. The missing `retrieved_at` KeyError is pre-existing; handle it only if it
falls out of the same change.

Nits from the review (deadline paragraphs repetitive on phone, label column whitespace, repeated
source wording) are not in scope.

Done when: `uv run --with pytest pytest -q product/nz_election/tests -k vote` passes (Chromium cases
may be sandbox-denied; say which), the three new tests fail on 8eac454, `bin/lint` ok. Commit in the
worktree, do not push. Write last.md with the commands and their output.
