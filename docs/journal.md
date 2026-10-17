# Journal

The complete record of the lab, kept so it can be read back at the end (Byron, 2026-10-16
22:58Z). Append-only, one dated entry per supervisor run, UTC; rules in `prompts/supervisor.md`
"Journal". The daily posts are the public digest of this. Entries before 2026-10-17 are a
backfill written by the fleet operator from `state/phase.md`, `state/changes.yaml`, the issues
and the posts; the supervisor should add anything those left out on its next runs.

## 2026-10-15 (day 0, backfill)

- Byron's brief (a Claude Code session, recorded as management D61): spend the idle Codex
  subscription for about twenty days building something of the model's choosing, Claude as
  supervisor, Codex for the token-heavy work, Anthropic's AI-native SDLC playbook with its
  indicators measured, a daily public blog, do not involve him.
- Loop live (`com.unattended.tick`, 600 s), blog live, first post, Byron told on Telegram.
- Fleet Audit chosen and built as the warm-up change (PRs #1 to #5, 11 reviewed attempts); day 1
  hit the Claude usage limit 21 ticks in a row, which became the cost guardrail.

## 2026-10-16 (days 1 and 2, backfill)

- Byron, issue #7 (07:57Z): the product is a web app with a UI about the 2026 NZ election,
  pulling a ton of information together. Research, intent, spec and plan followed; M1 closed
  15:49Z with PRs #9 to #14 live at byronxlg.com/unattended/nz-election/.
- Byron, issue #15: sprinkle UI work and marketing into the plan (design track, name and
  subdomain, launch kit, analytics). Design track started: design.md draft 2, design-system build
  dispatched 22:25Z.
- Byron, Telegram 21:55Z (relayed to issue #15 by the operator): the lab posts the earned
  channels itself from election@byronxlg.com; the operator made the address (pdw#563, #564).
- Incident 21:55Z to 22:35Z: Pages verify demanded unpublished daily families; hotfix PR #16;
  eval `evals/pages-verify-polls-only`. The live site never regressed.
- Codex weekly window at 47 percent after two days; the even-spread allowance became about ten
  points a day.

## 2026-10-16T23:08Z (operator relay, Telegram)

Byron, four messages, relayed verbatim as issue #18 by the fleet operator:

- 22:56Z: "For the election site. I agree that because we have time we should use it to verify
  things work over a day to day time frame. I think you should do some more research on what
  people want to see and make some pages targeting different audiences and tailor the ui to
  them."
- 22:57Z: "At this stage I think you need to bring me in the loop a little bit more often to
  test your judgements."
- 22:58Z: "Make sure you capture everything that happens in repo notes or something so we can
  look back at it at the end."
- 22:59Z: "Also check when the codex subscription actually runs out. We should push this
  project out to at least one week post election night."

Operator actions: this journal and the "Byron in the loop" and "Journal" sections of
`prompts/supervisor.md`; the lab's end date moved to at least 2026-11-14 in the prompt, README,
CLAUDE.md and about page. Codex: OpenAI's email of 2026-10-08 05:54Z says the ChatGPT Pro plan
will not renew and is available until the end of the billing period on 2026-11-07 (the cycle
anchor in the Codex auth token is 03:14Z, so the afternoon of election day NZ); Byron has been
asked on Telegram whether he will renew. The audience research and pages are the supervisor's
to plan: first judgement call to send him under the new rule.

## 2026-10-16T23:40Z (operator relay, Telegram)

Byron, 2026-10-16 23:17Z, relayed verbatim on issue #18 by the fleet operator: "I will not renew
codex. Claude will have to take the reins when the codex subscription actually ends."

Operator actions: the decision in the first paragraph of `prompts/supervisor.md` and a new "After
Codex" section (last build dispatched by 5 November, nothing new from the 6th, Claude writes
product code itself from the cut in the same PR shape, a fresh-context Agent review in place of the
Codex review, `state/codex.ended` marks the cut, the retrospective compares the two regimes);
README and CLAUDE.md say the plan is not renewed. The fleet records it as D63; its operator checks
the handover on 2026-11-08.

## 2026-10-16T23:37Z (supervisor run, day 3 NZ)

- Byron's words this run: issue #18 (relayed Telegram, 22:56Z to 22:59Z), quoted in the entry
  above. Acted on in order: audience research dispatched (item 1); the audience judgement call
  goes to him when the memo is in (item 2); items 3 and 4 (day-to-day verification as a
  milestone, re-planned milestones in spec.md) are next after the design PR.
- Design-system build `nz-election-design` finished 22:39Z: commit 91ebf33, 31 files, 287
  tests passing in its sandbox, refresh/build/verify PASS all; screenshots not run there
  (no Chromium). Host run: refresh/build/verify PASS all; the screenshot harness failed on its
  own axe check before judging a route: `aria-prohibited-attr`, an `aria-label` on the overhang
  segment div inside the role="img" seats strip, rendered both by build.py and by
  coalitions.mjs. Sent back on the build thread as `nz-election-design-fix` (23:43Z) with the
  invariant (segments are presentational, the overhang is described by the strip or the table)
  and the shape left to Codex. Not a repeated mistake: the sandbox could not run axe.
- Two observations from the partial screenshots, for the fresh review to judge: every route
  image carries a 3 px blue outline around main because the harness activates the skip link
  (main has tabindex -1, focus-visible fires); and at 1280 the source-note paragraph has line
  boxes inflated by the 44 px inline-link tap target, so "Retrieved" and the date split across
  a wide gap. Phone routes at 360 and 390 read cleanly: header, one-line brand, menu, H1,
  copy, source line, rule, footer.
- Dispatched `research-nz-election-audiences` (read-only, 23:44Z): audiences, the question
  each arrives with, evidence from Electoral Commission pages, 2023 coverage, Trends, existing
  dashboards; a page plan with build-by dates (26 Oct, 7 Nov, after); what not to build.
- Codex window at the start of the run: 50 percent, resets in 5.4 days, even spread about 9
  points a day. Spent today so far: the design build (47 to 50), this fix, this research.
- Judgement calls this run: none sent. Resuming Codex for a two-attribute fix rather than
  editing product code myself follows the rule that the supervisor writes no product code;
  the alternative (hand edit, note in the PR) was cheaper by one job and rejected for the rule.
- 23:48Z: fix 980d06e landed (aria-label removed from both renderers, overhang count moved into
  the seats-table caption). Host rerun: refresh/build/verify PASS all; the harness passed axe
  and then failed on the invalid-link state: the assertion on the warning text (new on this
  branch) reads [data-warning] the moment the page check returns, before the explorer writes
  it. A host probe of the same fixture with a one-second wait shows the exact text and a clean
  console, so the state renders and the race is in the harness. Second follow-up
  `nz-election-design-fix-2` (23:54Z): product fix if the branch delayed the hash handling,
  otherwise an auto-waiting read in the harness with the asserted text unchanged, explicitly
  authorised by the supervisor as a harness strengthening, not a test weakening. The PR, the
  fresh review (brief at state/jobs/review-nz-election-design/prompt.md, screenshots via
  --image) and the screenshot judgement move to the next run.
- Research memo `research-nz-election-audiences` landed (2,447 words) and is committed verbatim
  at intent/nz-election/audiences.md. Kept audiences: voting-help seekers (young and first-time
  voters inside it), policy comparers (link out), local-contest readers, poll followers,
  overseas voters, night watchers, post-election checkers, data users. Its surprise: the Herald
  published its 2023 polling model and code, so "nobody publishes methods" is not a
  differentiator. Three one-word questions for Byron; two of them (daily link review, result
  updates after 4 Nov) the lab owns through the day-to-day verification milestone.
- JUDGEMENT CALL sent 23:55Z (board line, tg send): build a /vote/ gateway before 26 Oct,
  candidates-first electorate pages, a results-first /night/ that becomes "Results so far";
  rejected separate demographic pages and an in-house policy comparison. Proceed at
  2026-10-17 12:00Z if he says nothing. Asked one word: success measure usefulness or reach.
- Mistake (supervisor, not Codex): ran `tg send --help` to learn the usage; it sent the text
  "--help" to Byron's Telegram. Read the script header next time.
- Codex window at end of run: 51 percent after the first fix; the research job and fix-2 are
  not in the ledger yet.
- 23:57Z: fix-2 33eb475 landed: the race was latent (start() and module startup match main
  byte for byte); only tests/screenshots.py changed, three states now read the warning with an
  auto-waiting expectation and the asserted strings unchanged. Host rerun 23:58Z to 00:03Z:
  the state images (181 files) and the OG captures passed; the harness then failed further on
  with an assertion that dumps the page's accessibility tree, and the tail I kept did not
  include the assertion line. Rerunning with the output logged to /tmp/ds-shots.log; the
  triage, PR and fresh review go to the next run if the log lands after this run's kill time.
- 00:09Z: the logged rerun shows the invalid-link warning element stays empty under the
  harness. Cause read from the harness: check_page presses Tab and Enter on the skip link
  (href "#main"), which replaces "#coalition=invalid" while the explorer awaits its data, so
  restore() sees "#main". The product is right; the new harness clobbers its own input. Third
  follow-up `nz-election-design-fix-3` dispatched 00:10Z (harness only, assertions unchanged).
  Three fix rounds on one build: the sandbox cannot run Chromium, so every harness defect
  surfaces one host run at a time. Lesson for the next UI brief: ask Codex to keep state
  assertions independent of check_page's keyboard sequence, and to list every host-only check
  as a claim. OG card observation for the review: the source note's inline links carry the
  44 px tap-target line boxes onto the OG image too ("Retrieved" split from the date,
  "Downloads." alone on a line); on a static card that padding is a defect.

## 2026-10-17 00:20Z run (job_done fix-3, issue #20)

- Byron, Telegram 2026-10-16 23:49Z to 23:57Z, relayed as issue #20, verbatim:
  "I have another idea. Tweet sentiment classification and party categorisation analysis. A
  potential structure for the app could be to have a feed like home page with charts and
  description which opens into a page that goes into mor detail. Don't strictly go off what I
  say, that is an idea for making it interesting for users, validate it" / "This could be a good
  inspiration: https://www.nbcnews.com/politics/2026-elections/midterms" / "You should have
  access to jev and tweets. We have api keys in the x402 repo you can use" / "Reach. But we
  don't need to help people vote if that's what you were getting at. We're more displaying info
  and analysis" / "The demographics would be more like, general users / power users /
  journalists etc" / "Just going off how you provide downloads, that would not be useful to
  general users but general users would want to see graphics".
- JUDGEMENT CALL of 23:55Z closed by reply, not silence: success measure is reach; the /vote/
  gateway is dropped; audiences are general users (graphics), power users and journalists (data,
  downloads). The 12:00Z proceed time is void. Candidates-first electorate pages and the
  results-first night view survive as they serve display and analysis; they are re-planned
  with the feed-shaped home, not built on the old call.
- Keys: the operator copied X_UPSTREAM_KEY and TYPESAFE_API_KEY to SSM /unattended/prd and to
  this repo's Actions secrets (00:09Z). CLAUDE.md's secrets line gains the one-line exception.
  Rule carried into every brief and review: no key in the tree, a page, data/, a screenshot or a
  PR body; a workflow that echoes its environment is a reject. Runbook entry due in the
  increment that first uses them.
- 00:2xZ dispatched research-nz-election-social (read-only, brief at
  state/jobs/research-nz-election-social/prompt.md): what the sentiment feature would show,
  whether X volume on NZ politics supports it, credits and Jev cost per day, Electoral Act
  section 197 and X terms, what existed in 2023, NBC's hub shape, a feed-of-cards home proposal,
  and a verdict with the alternative for the judgement-call line. The judgement call goes to
  Byron after the memo lands, not before: "validate it" asks for evidence first.
- fix-3 9b593cd (harness only, 3 insertions in tests/screenshots.py: invalid-link and
  changed-inputs re-navigate to their fixture URLs after check_page's skip-link sequence).
  Sandbox: 287 passed, PASS all, lint ok. Host run of refresh/build/verify and the full
  screenshot harness started 00:21Z, logged to /tmp/ds-verify.log.
- 00:34Z host harness on 9b593cd: fix-3 held (all state images passed the hash-carried checks),
  then axe landmark-unique failed on an electorate state fixture: electorate_pages.py line 88
  labels every local poll table "Reported local shares", so an electorate with two local polls
  has two regions with one accessible name. Product defect, found by the harness the sandbox
  cannot run. fix-4 nz-election-design-fix-4 dispatched 00:38Z on the same thread; brief names
  the invariant (unique landmark names, enforced by check_page's axe assertion) and leaves the
  label shape to Codex; tests untouched. Four fix rounds on one build is the lesson recorded
  for the next UI brief: the first host harness run should happen before any review, and the
  brief should ask for a fixture with two local polls.
- 00:26Z research-nz-election-social landed (276 s, rc 0, 2,309 words), committed verbatim to
  intent/nz-election/social.md. Verdict: build a smaller version. Reasons: no measured X volume
  for NZ politics (planning range 500 to 5,000 posts a day, low confidence; small parties too
  thin for daily sentiment), classification unvalidated on NZ text, X developer terms and
  twitterapi.io supply chain unconfirmed for transmitting posts to Jev, defamation on
  quotations, and Electoral Act s197: nothing new published on 7 November before 19:00 NZDT.
  Cost of the proposed plan: 480 posts a day, about 7,200 credits (0.92 percent of the balance)
  and USD 0.02 of Jev a day; USD 2.56 of upstream to 14 November. NBC's hub could not be
  fetched (no browser in the job); its shape is unverified. Home feed proposal: seats, trend,
  thresholds, markets, electorates, candidates, then a weekly topics card only after gates.
- JUDGEMENT CALL sent 00:40Z (board line, tg send): reach-first home as a feed of chart cards
  each opening a /polls/ detail route before 26 Oct, plus a seven-day unpublished X pilot
  (7,800 credits a day cap, raw posts never in git) to test whether a weekly party-topics chart
  has enough sample; per-party sentiment and tweet quotations not built now. Rejected: the full
  sentiment dashboard now (Byron's idea taken literally), and doing nothing social (he asked for
  it to be validated, and the pilot is the validation). Proceed at 2026-10-17 12:30Z if silent.
  Why the pilot is a judgement call and not a reversible change: it spends prepaid credits
  shared with the x402 gateway's buyers.
- Carried into phase 5: the s197 publication freeze (no rebuild or new political analysis on
  7 November before 19:00 NZDT, 06:00Z) goes into spec.md's rehearsal milestone and the
  workflows' schedule; a Commission opinion on the concrete pages is Byron's to seek
  (needs-byron when the pages exist).
- 00:46Z fix-4 bed5452 landed (187 s class, same thread): electorate_pages.py builds the local
  poll caption from pollster, measure and fieldwork label, with a "(report n)" suffix if two
  polls still collide; one new regression test (288 passed), audited every table() caller
  across the 77 routes; tests otherwise untouched. Spot-checked the 10-line diff on the host:
  the invariant holds by construction. Host rerun of refresh/build/verify and the full harness
  started 00:48Z, logged to /tmp/ds-verify.log; the next run reads it, looks at the
  screenshots, opens the PR and dispatches the fresh review. Codex window 53 percent after
  the research job and fix-4 (about 2 points this run, under the 9-point allowance).
- Correction (clock): the host harness takes about three minutes, not twelve; `date -u` read
  00:36Z when the bed5452 rerun finished. The times 00:34Z, 00:38Z, 00:46Z and 00:48Z in the
  entries above are my estimates and run about ten minutes late; the ledger's started and
  ended fields are authoritative (research job 00:21:35Z to 00:26:11Z).
- 00:36Z host harness on bed5452: PASS all, PASS screenshots: 77 routes, 202 images, OG 2
  images, RC=0. Looked at home 360 and 1280 (polls-only fixture, so the unavailable form of the
  home sentence), night 390, Wellington North 390, og-home. Five-second test: the sentence,
  source and retrieval time are above the fold at 360, the navigation and menu read, the
  unavailable copy is honest. Defects I carry to the review rather than decide: the source
  note's inline links keep their 44 px line boxes, so the note is triple-spaced at every width
  and on the OG card ("Downloads." alone on a line); the OG card is blank below the note.
- 00:41Z branch pushed, PR #21 opened (body: intent, spec, design, plan, DESIGN_REPORT.md, the
  host verification tails, the two known concerns). Fresh review review-nz-election-design
  dispatched read-only on the worktree with six screenshots attached (home 360, 390, 1280,
  night 390, Wellington North 390, og-home) and an addendum asking whether each concern blocks
  the merge and how to fix the line boxes without losing the tap target. design_rounds set to 2
  in state/changes.yaml (draft 1 critiqued, draft 2 accepted). Next run: read the review, log
  it in the PR, decide merge or one fix round carrying every finding, then increment 7.
