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

## 2026-10-17 00:47Z run (reasons: job_done fix-2, fix-3, fix-4, design, social research, fresh review)

- Read the fresh review of PR #21 (review-nz-election-design, read-only on bed5452, 149 s,
  window 53 percent). Eight Important findings and two nits. I accept all eight: build.py:251
  raises ValueError when the 30-day window holds no polls (the reviewer's read-only comparison:
  73378ab renders 22521 characters, HEAD raises), which can block a daily build; the link line
  boxes I carried into the review are confirmed merge-blocking; two existing assertions
  (test_coalitions.py:149, test_increment_two_regressions.py:184) became weaker, which the
  protected loop forbids; client and server coalition strips differ in names, captions,
  columns and precision; electorate source links take the dataset's publisher instead of their
  own; the seats explainer link went inside the disclosure; the OG headline computes
  availability separately from the page.
- Judgement: one fix round rather than merge-with-follow-ups, because two findings are
  blocking on their own and a fix round costs about one window point. Alternative rejected:
  splitting into product fix now and test-strength fix later, because a merge with weakened
  assertions would be the lab's first breach of the protected loop. Finding 8 (per-route OG
  cards and og:image) deferred to the feed-home change; the OG card's empty lower half deferred.
- The one allowed test edit: the two assertions return to full strength against the new
  markup, at least as strong as at 73378ab. Nothing else in tests changes; new tests welcome.
- 00:50Z both reviews logged as comments on PR #21 (fresh review verbatim, supervisor verdict).
  Fix-5 nz-election-design-fix-5 dispatched on the build thread (resume
  01a146c7-3dd0-79a2-963c-948425b2a9d3) with the eight decisions and the full review text.
  Reviewed markers set for the seven finished jobs.
- Judgement call to Byron (00:40Z, feed home plus X pilot) still open; proceeds at 12:30Z
  absent a reply. No new line sent this run.
- Codex: window 53 percent, fix-5 is about one point; today's spend so far about 2 points of
  the 9-point allowance before this dispatch. Disk 18.4 GiB.
- Next run: review fix-5 on the host, second fresh review, merge, then increment 7.

## 2026-10-17 00:52Z operator entry (fleet operator, not a supervisor run)

- Byron, Telegram 2026-10-17 00:34Z, verbatim: "Why did the sentiment dash get rejected? I feel
  like we should poc every him thing early and refine". It answers the 00:27Z judgement call
  (feed home plus unpublished X pilot, sentiment dashboard not now) by reply: the 12:30Z proceed
  time is void. Relayed as issue #22 with the memo's reasons and the operator's reading (every
  new thing gets a proof of concept early, refined from what it shows; the found constraints
  bind the POC rather than defer it).
- New "Proof of concept first" section in prompts/supervisor.md, this PR, in the shape of the
  "Byron in the loop" section. No product code.
- The operator answered his question on Telegram: the research memo's four reasons and that the
  rule is now in the prompt.


## 2026-10-17 01:00Z run (reasons: job_done fix-5, issue #22)

- Byron, Telegram 2026-10-17 00:34Z, relayed as issue #22 by the operator, verbatim: "Why did
  the sentiment dash get rejected? I feel like we should poc every him thing early and refine".
  Taken as an instruction: the 00:40Z judgement call is answered by reply, not silence. The feed
  home half stands (no objection); the "unpublished seven-day pilot first" half is overturned.
  The sentiment idea is built as a proof of concept, visible on its own route, labelled with
  sample size and date range, then refined from what it shows. The research memo's constraints
  (aggregates only, no raw posts, handles or keys in the tree, a daily credit cap of 7,800, the
  s197 freeze on 7 November) shape the build and no longer defer it. Quotations of individual
  posts stay out until he has seen the POC. The rule is in prompts/supervisor.md ("Proof of
  concept first", PR #23 by the operator, merged before this run).
- Order after PR #21 merges: the sentiment POC is the next build (route, daily workflow using the
  Actions secrets X_UPSTREAM_KEY and TYPESAFE_API_KEY set 00:09Z, credit ledger, aggregates only).
  Increment 7 (markets) runs alongside only if its files are disjoint from the POC's; otherwise
  after. The feed-home change follows, no longer waiting for 12:30Z.
- Fix-5 (nz-election-design-fix-5, 532 s, window 53 to 55 percent) landed as 0108d71. Checked
  the two test files against 73378ab: test_coalitions.py passes the home source into strip (a
  signature change, same assertion); the renamed strip test now verifies lane order, segment
  widths, majority marker and every connector numerically for phone and wide layouts, stronger
  than the version it replaced. The sandbox could not launch Chromium, so the engineer listed
  the screenshot passes as claims. On the host from 0108d71: refresh, build, verify PASS;
  screenshots PASS 77 routes, 204 images; OG pass 2 images; source_note_bottom 516.78 at 360
  and 390. Looked at home 360, home 1280 and og-home.png: the source note is compact prose with
  a wrapped action row, "Retrieved" stays with its date, the OG card no longer triple-spaces.
  Branch pushed (bed5452..0108d71).
- Dispatched review-nz-election-design-2 (read-only, same brief plus the second-pass addendum
  and the engineer's reply verbatim, twelve screenshots attached) at 01:10Z. It must say fixed,
  not fixed or fixed-with-new-defect for each of the eight, and confirm the Node parity cases
  compare client markup with server markup.
- PR #21 CI was pending at 01:08Z on 0108d71.
- Next run: read the second review; if clean and CI green, log both reviews on the PR, squash
  merge, remove the worktree, record merged; then brief the sentiment POC.

## 2026-10-17 01:19Z run (reasons: job_done:review-nz-election-design-2, issue #22 at 01:08Z)

- Context: Codex window 56 percent, resets in 5.3 days, allowance about 8 points per day (4
  spent today: fix-4, review, fix-5, review-2). Disk 19.7 GiB. PR #21 CI green on 0108d71.
- Issue #22 carries the operator's 01:00Z acknowledgement of the POC-first instruction; nothing
  new from Byron this run.
- Second fresh review (review-nz-election-design-2, 124 s): seven of eight prior findings
  fixed, the eighth (per-route og:image) deferred as decided. Fix-5's strip test confirmed
  stronger than the one it replaced. One new Important: web/templates/source-note.html now says
  "Seats calculated by this site" in every note, including the poll table, the averages note
  and the threshold note beneath a headline that withholds seats; and the averages and seats
  notes show retrieval time without the fieldwork date of their contributing polls because
  source_note reads fieldwork_end only from poll rows. The reviewer could not run pytest in the
  sandbox (uv cache); host evidence stands for that.
- Judgement, small: checked main, where the sentence was "Parsed and averaged by this project",
  true everywhere. So the PR introduces a false provenance line; the lab's rule is no number
  without a true provenance chip, and this would deploy on merge. Alternatives: merge and fold
  the wording into the feed-home change (days away, false line live meanwhile), or fix now.
  Chose fix-6 on the build thread, scoped to that one finding, invariant named (each note states
  only what is true of the thing it sits under; each note's dates describe its contributing
  data), shape left to the engineer, tests per note kind, no existing test edited. Cost about
  two window points; the sentiment POC build still fits today's allowance if fix-6 is cheap,
  otherwise it is tomorrow's first dispatch.
- Both reviews logged on PR #21 (second pass plus the supervisor verdict at 01:2xZ).
- Dispatched nz-election-design-fix-6 at 01:24Z (resume of the build thread, workspace-write).
- Next run: read fix-6; run the host harness (refresh, build, verify, screenshots, OG); spot
  check the four note sentences in the built home page; then log the check on the PR, squash
  merge, remove the worktree, record merged; then brief the sentiment POC.

## 2026-10-17 01:31Z run (reasons: job_done:nz-election-design-fix-6)

- Context: Codex window 56 percent, resets in 5.3 days, allowance about 8 points per day (five
  jobs today before this run: fix-4, review, fix-5, review-2, fix-6). Disk 19.1 GiB. No new
  words from Byron; issues #22, #20, #18, #15, #7 unchanged.
- fix-6 7f2af43 (225 s, rc 0): source-note.html takes a per-note calculation sentence, the
  averages and thresholds notes take the selected polls' fieldwork dates, one new test file
  (test_source_note_meaning.py, four cases), no existing test edited; sandbox 298 passed, PASS
  all, lint ok; Chromium blocked in the sandbox as before.
- Host harness on 7f2af43 (01:33Z to 01:37Z, /tmp/ds-harness-6.log): PASS all, screenshots PASS
  77 routes 204 images, OG PASS 2 images. Spot check of the built home page: the four notes
  read "Polls parsed by this site", "Available poll shares averaged with equal weight by this
  site", "Threshold shares averaged with equal weight by this site" and, under the withholding
  headline, "Seats withheld; see the headline"; every note carries "Fieldwork ended 12 Oct
  2026" from its contributing polls; no "Seats calculated" sentence in a withheld build. CI
  green on 7f2af43.
- Supervisor check logged on PR #21 (comment 6228043566); squash merged 01:38Z as 5c1fd99;
  worktree and branch removed. Pages deploy of 5c1fd99 started 01:38Z; the live site is to be
  confirmed next run. Design track: one build, six fix rounds, two fresh reviews, two supervisor
  reviews. Lesson already recorded on 00:34Z stands: the host harness before the first review.
- Judgement, within the POC-first rule (no board line, Byron's instruction in issue #22 is the
  decision): the sentiment POC is the next dispatch, ahead of increment 7 (markets), because the
  Gamma captures increment 7 needs are not in the tree yet and the POC is Byron's own ask. Brief
  at state/jobs/nz-election-social-poc/prompt.md: smallest real thing, real posts through
  twitterapi.io and classification through Jev, aggregates only (no post id, text, handle or
  URL anywhere), credit ledger with the 7,800 cap and worst-case reservation, data/social family
  validated like the others, a daily workflow at 13:40Z with the two Actions secrets in the
  step environment only, the s197 freeze on 7 November before 19:00 NZDT in both the workflow
  and the code, route social/poc/ labelled Proof of concept with sample size and date range,
  attitude rows withheld under 30 posts, cells under 5 shown as "under 5", runbook section,
  tests with injected transport and synthetic fixtures. The shape of the records and the charts
  is left to the engineer; the invariants are named with where they are enforced (export.py
  validator, the ledger, the freeze check). The first real day runs by workflow_dispatch after
  the PR merges; that day's page is what we refine against.
- Dispatched nz-election-social-poc at 01:39Z (build, workspace-write, worktree
  .worktrees/nz-election-social-poc from 5c1fd99). About three to five window points; today's
  allowance is then spent, so increment 7 waits for tomorrow unless the window shows otherwise.
- Next run: read the POC job; host harness; supervisor review; push, PR, fresh review. Confirm
  the live design at byronxlg.com/unattended/nz-election/. Capture the five Gamma events for
  increment 7 (read-only curl, committed in its worktree).

## 2026-10-17 01:49Z run (reasons: job_done:nz-election-social-poc)

- Codex window 57 percent at 01:46Z (resets in 5.3 days, allowance about 8 points per day);
  disk 18.4 GiB. The POC build nz-election-social-poc ran 462 s, 1.5M input tokens, rc 0.
- The job stopped itself, correctly, under the AGENTS.md rule "if a test is wrong, say so and
  stop": one local commit 5705910 (social.py, social_page.py, daily workflow, export and publish
  changes, runbook section, 33 tests of its own) and 5 failures out of 298 in the suite. Three
  existing tests plus the screenshot harness pin the route count at 77 and the new route makes
  78; test_contracts.py::test_hourly_daily_race_preserves_union assumes the hourly and daily
  workflows together produce every registered family, which the separately scheduled social
  family breaks; its own build test used an output path build.py rejects. No live Jev or X
  request was made. The five questions sent to the classifier are recorded verbatim in last.md.
- Supervisor mistake: my brief said "do not edit existing tests" for a change that adds a route
  and a family, so the route-count and family-set contracts could not move. Decision: those
  contracts move with the registered set in the same build commit and nothing gets weaker (77 to
  78 keeps uniqueness; the family union is asserted over the set each workflow owns, with status
  listing every family). Logged in CLAUDE.md Known agent mistakes.
- Dispatched nz-election-social-poc-r1 at 01:52Z on the build thread (resume, workspace-write)
  with state/jobs/nz-election-social-poc/followup-1.md: the invariant for each contract, the
  engineer picks the shape, re-run the definition of done, stop again if anything else blocks.
- Live site: byronxlg.com/unattended/nz-election/ answers 200; pages.yml for 5c1fd99 and eb731d0
  both completed success at 01:39Z and 01:40Z. The design merge is live.
- Next run: read r1 last.md and test output, host screenshot harness (78 routes), supervisor
  review, push, PR, fresh review. Gamma captures for increment 7 still pending.

## 2026-10-17 02:01Z run (reasons: job_done:nz-election-social-poc-r1)

- Codex window 58 percent at 01:55Z (resets in 5.3 days, allowance about 8 points per day);
  disk 19.0 GiB. r1 ran 250 s, 4.0M input tokens (3.9M cached), rc 0, commit 8faba3e on
  change/nz-election-social-poc: route tests now derive the expected set from routes.json and
  electorates.json and assert uniqueness; the family union test publishes all three owned
  families then checks the full union; test_geography's 77 is boundary records, untouched;
  verify.py gained a `social` check.
- Host harness from the worktree: 331 passed in 154 s; refresh, social (fixtures, day
  2026-10-16), build (78 routes) and verify all PASS; bin/lint ok (347 files); key-name grep
  clean outside runbook, workflow and social.py; the built social page contains "Proof of
  concept" three times and no "@". The screenshot harness failed at the social route with
  SMALL_TARGET: the four links in the social source note (twitterapi.io, Inputs, method, data
  run) are inline in a single p.source-note and measure 16 px; styles.css line 23 restores the
  44 px target only inside p.source-actions, which is the shape every other route uses
  (build.source_note, electorate_pages). Also 8faba3e tracks the worktree's last.md, which no
  prior PR carried.
- Supervisor review of the rest from last.md, the diff stat and spot checks: workflow has
  permissions {} at the top, secrets only in the collect step's env, the two names match the
  repository secrets set 00:09Z, reservation ledger published under the existing
  nz-election-data-publication group before any paid request, freeze check in all three jobs
  (frozen() is 7 November NZ before 19:00); runbook section names secrets by name only, the
  7,800 cap, the 315 reservation unit, how to run by hand; page copy states sample size, date
  range, convenience-sample caveats, withholding thresholds (20 for shares, 30 for attitude
  rows), X terms. Nothing Important beyond the target check; the fresh review reads the diff.
- Dispatched nz-election-social-poc-r2 at 02:06:48Z on the build thread (resume, workspace-write)
  with followup-2.md: move the source-note links into the shared p.source-actions shape in both
  copies, no CSS change, remove last.md from the branch, re-run the definition of done. Codex
  mistake, first occurrence (not logged in mistakes.jsonl): a new page's source note did not
  follow the design system's shared shape; the harness caught it.
- Next run: r2 last.md, host harness again (must reach the end: 78 routes, 390 and 1280
  captures), look at the social screenshots, push, PR with the harness output, fresh review
  with screenshots. Gamma captures for increment 7 still pending; the 12:30Z deadline on the
  00:40Z feed-home judgement call stands.

## 2026-10-17 02:18Z run (day 3, job_done:nz-election-social-poc-r2)

- Context: Codex window 59 percent, resets in 5.3 days, allowance about 8 points per day;
  disk 17.5 GiB; no jobs running. No new words from Byron since issue #22.
- r2 landed 1271c0e on change/nz-election-social-poc: both social source notes use
  div.source-note with link-free prose and links in p.source-actions, CSS and tests unchanged,
  last.md untracked. Codex reported 331 passed, PASS all on 78 routes, lint ok, secret-name
  scan clean, Chromium blocked in its sandbox.
- Host harness from the worktree: refresh fixtures, build (PASS build: 78 routes), verify all
  (PASS social, PASS all), screenshots PASS 78 routes 206 images. Looked at social/poc/ at
  1280x800 and 390x844: the empty state ("no sample is available yet") renders in the design
  grammar; the fixture has no social sample so the populated page is not shown.
- Spot checks: workflow secrets X_UPSTREAM_KEY and TYPESAFE_API_KEY in the collect step env
  only, s197 freeze check before reservation, collection and publication; social.py CAP 7800,
  RESERVATION 315, SOCIAL_CREDIT_CAP raised on overrun; twelve tests in test_social.py cover
  cap, pacing, dedup, withholding, freeze, durable reservation, identifier rejection, publish
  retention.
- Pushed the branch; PR #24 opened 02:24Z (body links intent, spec, plan-m2 and the briefs,
  names the host verification). Supervisor review logged on the PR. Fresh review
  review-nz-election-social-poc dispatched 02:26Z read-only with the two screenshots and a
  brief that puts leaks first, then the workflow, the cap, the contracts, the page copy.
- Not done: no live X or Jev request yet; the first real day is a workflow_dispatch after
  merge, then look at the real numbers with Byron (judgement call line then, per issue #22).
- Next: fresh review verdict, CI, merge, dispatch the workflow by hand, then Gamma captures for
  increment 7; the 12:30Z deadline on the 00:40Z feed-home judgement call stands.
- 02:33Z addendum. Fresh review review-nz-election-social-poc (read-only, 144 s, window 60
  percent) returned five Important: (1) the Jev model field is persisted and rendered after a
  permissive regex, so echoed upstream text can reach data and the page; (2) the s197 freeze
  stops the social publication but not pages.yml, which can deploy a pre-midnight update after
  midnight or rebuild inside the window; (3) a retried collection reuses the downloaded unused
  reservation and publication merges counters with max (replay spent 14,400, ledger said
  7,200); (4) the budget day is fixed at collection start, so a run crossing NZ midnight plus
  a fresh run can exceed the cap; (5) str(Decimal) can emit 1E-8 which the validator rejects
  after paid collection. Logged on PR #24. Judgement: all five are real and each is cheaper to
  fix now than after the first paid day, so a fix round before merge rather than merge and
  patch.
- Host found a sixth: with the social fixture collected (`social.py --fixtures --day
  2026-10-16`) the populated page fails the harness with MISSING_SOURCE: figure {} (a figure
  without aria-describedby). Neither the engineer's sandbox nor the supervisor's first harness
  run captured the populated state. Looked at an unstyled capture of the populated page: the
  copy states 240 posts, 16 October, one page per hour, withholding under 5 and under 30, the
  method and X terms; honest. Codex mistake, second occurrence (shared design shapes on a new
  page): logged in state/mistakes.jsonl, one line added to AGENTS.md Design.
- Dispatched nz-election-social-poc-fix-1 at 02:38Z on the build thread (resume, workspace-write)
  with followup-3.md: six items, each as an invariant and where it is enforced, engineer chooses
  the shape; existing tests untouched, a failing-then-passing test per item; definition of done
  includes the social fixture step before the harness.
- Next run: fix-1 last.md, host harness with the social fixture to the end, look at the
  populated screenshots at 390 and 1280, push, second fresh review, CI, merge.

## 2026-10-17 02:41Z run (day 3, job_done:nz-election-social-poc-fix-1, job_done:review-nz-election-social-poc)

- Codex window 61 percent at 02:38Z, resets in 5.2 days, even spread about 7 points per day;
  six jobs today (POC, r1, r2, review, fix-1, now review-2). Disk 18.2 GiB. No new issues.
- fix-1 landed 0642382 (517 s): closed model registry (jev-1.13.0 plus the two repo-owned
  synthetic versions, anything else rejected and recorded as a sanitized error); build.py
  refuses publication inside the s197 window via deployment_guard.require_publication_allowed,
  with --now for deterministic tests; pages.yml gained an inline clock guard 2026-11-06T10:30Z
  to 2026-11-07T06:00Z (23:30 NZDT 6 Nov to 19:00 NZDT 7 Nov, a 30 min buffer on the 10 min
  deploy timeout); reservation claimed durably through publish.py before any paid request,
  publication additive, a merge that would hide a spend refused; NZ budget date checked before
  and after pacing with a 31 s margin before midnight; fixed-point Decimal bounded at 1,000
  places; both populated figures carry aria-describedby. Eight new tests in
  test_social_fix_round1.py, each failing on 1271c0e per the job report; existing tests unchanged.
- Host verification on 0642382: 339 passed in 159.69s; fixture pipeline with the social fixture
  PASS social, PASS build: 78 routes, PASS all; screenshot harness PASS 78 routes 206 images;
  lint ok (348 text files). Looked at social/poc/ populated at 390 and 1280: title says Proof
  of concept, lede gives 240 posts over 1 day, 16 October, one page per hour; withheld rows
  for parties under 30; both figures with source notes. Nits for the refinement round, not
  this PR: "over 1 days" grammar; primary-party bars scale to a small fraction of the row
  width; attitude bars on the fixture show only two grey segments. Pushed; supervisor review
  logged on PR #24.
- Judgement noted on the PR: the freeze guard pauses the whole build and the whole Pages
  deployment inside the window, not just the social route. Accepted as conservative under
  s197: the election-night route updates only from 19:00 NZDT, so the night is not blocked.
  The brief offered rendering the social route from the last pre-freeze state as the
  alternative; the engineer chose the whole-site pause. Reversible, one change, no line to Byron.
- Dispatched review-nz-election-social-poc-2 at 02:52Z (read-only, fresh context, both
  populated screenshots attached) with the six items, the freeze arithmetic, the retry replay
  walk-through and the leak paths as the checklist.
- The 00:40Z judgement call (feed-home direction) still open to 12:30Z.
- review-nz-election-social-poc-2 (118 s) found three Important and one nit: (1) publish.py
  rejects an identical publication retry (the stored row holds the conservative 7,560 for a
  7,200 report) and a zero-request handled stop; (2) the midnight check precedes checkpoint(),
  so a slow checkpoint can cross NZ midnight before send(); (3) the pages.yml guard is
  check-before-action, a delayed deploy step could land inside the window; nit "over 1 days".
  Replay walk-through now gives ledger 7,560 and actual spend 7,200 instead of 14,400; the
  freeze arithmetic confirmed; no remaining upstream-string path found; existing tests
  unchanged. Could not run the tests in its sandbox; the host run stands. Logged on PR #24.
- Judgement: items 1 and 2 confirmed and cheap, fix-2 dispatched 02:58Z on the build thread
  (followup-4.md: idempotent identical publication, zero-request handled stop publishes,
  lowering or hiding a spend still refused; recheck the budget date immediately before
  transport; singular day; existing tests untouched, failing-then-passing test per item,
  pages.yml untouched). Item 3 accepted as is with the reasoning on the PR: guard and deploy
  run sequentially on one runner, the deploy step has a 10 min timeout, so a guard passing at
  10:29Z is done by 10:40Z, 20 min before the 11:00Z freeze start; the 30 min buffer is the
  bound. Not a weakening: nothing changed to pass.
- CI on 0642382 (PR #24) still pending at run end.
- Next run: fix-2 last.md, host run (tests, fixture pipeline with the social fixture, lint),
  push, supervisor review on the PR; a third fresh review only if the diff reaches beyond
  publish.py, social.py and social_page.py; CI green then squash merge, remove the worktree,
  dispatch the daily workflow by hand (workflow_dispatch, day input) for the first real day.

## 2026-10-17 03:04Z run (day 3, job_done:nz-election-social-poc-fix-2)

- Context: Codex window 62 percent, resets in 5.2 days, allowance about 7 points per day;
  disk 18.3 GiB; no Byron words since issue #22. CI on 0642382 (PR #24) green.
- fix-2 (51 s) stopped correctly: the "over 1 days" nit is asserted verbatim in
  test_social.py:179 and followup-4.md said existing assertions stay exactly as they are. The
  conflict is the supervisor's: the brief did not grep the tests for the string it changed.
  Logged in state/mistakes.jsonl (supervisor, new entry) and CLAUDE.md Known agent mistakes.
- Judgement: drop the nit from the fix round; the wording and its assertion move together in
  the refinement round after the first real day. fix-3 dispatched 03:08Z on the build thread
  (followup-5.md: items 1 and 2 of followup-4.md unchanged, same definition of done).
  Reversible, one change, no line to Byron.
- Increment 7 inputs: the five Gamma event captures from plan-m2.md "Before increment 7"
  fetched at 03:05Z (all 200, one event each, 34/6/7/7/6 markets, 26 to 127 KB, closed false,
  endDate 2026-11-08T04:59Z) into .worktrees/nz-election-7 on change/nz-election-7 from main,
  with manifest entries (sha256, bytes, upstream updatedAt as revision distinct from
  captured_at, the plan's licence text, turnout exclusion reason) as 96ea89b. The capture
  count pin test_capture_manifest (111) moves to 116 in the increment 7 build; the brief says
  so. Not pushed; the increment 7 PR carries it.
- The 00:40Z judgement call (feed-home direction) still open to 12:30Z.
- fix-3 (a794765, 560 s): publish.py keeps a receipt hash per accepted completed report under
  social-report/<run id> in the ledger envelope's input_hashes, taken only from the leased
  remote ledger; identical retries leave the ledger byte-for-byte unchanged, zero-request
  handled stops publish, lower or hidden spend still refused. social.py rechecks the NZ budget
  date and the freeze immediately before send(). Three new tests fail on 0642382, pass after.
  Host run: 342 passed in 162.08s; fixture pipeline PASS social, PASS build: 78 routes, PASS
  all; lint ok (364 text files). Pushed 03:13Z; supervisor review logged on PR #24; no third
  fresh review (diff inside the files the second review walked). CI pass 4m45s.
- PR #24 squash merged 03:19Z as 79af3d6; worktree and branch removed; Pages deploy of
  79af3d6 in progress at run end.
- First real day: NZ election social daily dispatched by hand 03:21Z, day 2026-10-16, run
  https://github.com/byronxlg/unattended/actions/runs/38998322076 (both Actions secrets
  present: X_UPSTREAM_KEY, TYPESAFE_API_KEY). Read next run.
- change/nz-election-7 rebased onto 79af3d6 cleanly (captures now 06f34fb); increment 7 brief
  finalised at state/jobs/nz-election-7/prompt.md with the base. Not dispatched: the Codex
  window is at 62 percent with 5.2 days left (about 5 points per day remaining), and today's
  share went to the POC's three fix rounds. Dispatch on the next day's share.
- Deferred to the social refinement round: the "over 1 days" wording with its assertion, Gamma
  unit evidence for volume and liquidity (the brief labels the unit unavailable until then).

## 2026-10-17T03:30Z run (reason: job_done nz-election-social-poc-fix-3, marker missing)

- fix-3 was reviewed and merged last run (PR #24, 79af3d6); only `state/jobs/.../reviewed` was
  missing, so the tick re-fired. Touched it. Pages deploy of 79af3d6 and bf36447 both success;
  social/poc/ answers 200 live.
- Incident, first real social day: run 38998322076 (sample day 2026-10-16) reserve success,
  collect failed in under a second at the first paid request, publish wrote the handled failure
  status row to the data branch (dc78294: social state unavailable, error SOCIAL_UPSTREAM_FAILED,
  credits row day 2026-10-17 reserved 7560 spent 7560 requests 1 closed) and exited 1 by design.
  The log said nothing more than `FAIL social: SOCIAL_UPSTREAM_FAILED`.
- Diagnosis on the host (keys through chamber from SSM /unattended/prd, values never printed):
  X key valid (my/info 200, 783,103 credits), Typesafe key valid (422 on an empty body, so past
  auth). One reproduction of the first hourly window: api.twitterapi.io 400 "query is too long
  (522 characters). The maximum length is 512 characters". QUERY is 477 characters plus the 45
  character epoch suffix. A 296 character variant returned 200 with 4 tweets and has_next_page,
  so the endpoint, epoch operators and key are fine. Cost of the diagnosis: one successful
  search call, about 60 credits, outside the Actions ledger.
- Root cause is the supervisor's: the query shipped verbatim from intent/nz-election/social.md,
  written without checking the provider's documented 512 character limit. Second defect accepted
  in review: refresh_social folds every exception into SOCIAL_UPSTREAM_FAILED and transport
  discards the HTTP status, so the log cannot distinguish a rejected query from a bad key.
- Eval added for the incident: evals/social-query-length (task.md, check.sh; FAIL on main today,
  committed as 3b5c077 on change/nz-election-social-fix so main CI stays green).
- Dispatch: nz-election-social-fix-1 (kind fix, change nz-election) at 03:47Z in
  .worktrees/nz-election-social-fix from bf36447, brief state/jobs/nz-election-social-fix-1/prompt.md:
  item 1 shorten QUERY under the 512 bound with a pinning test and the intent updated, the
  engineer chooses which terms give way; item 2 a stderr line with the inner code, HTTP status,
  window and attempt, never a body; existing assertions untouched. Judgement: today's Codex share
  was spent (63 percent, 5.2 days left), but the daily workflow fails every day until this lands
  and the fix is small; the spend comes off tomorrow's share. Reversible, no line to Byron; the
  day's post will carry it.
- Side effect to note for the refinement round: the failed run left spent 7560 on budget day
  2026-10-17 (NZ), so a by-hand rerun today would stop on SOCIAL_CREDIT_CAP. The proving run is
  the scheduled 13:40Z run (NZ 18 October), sample day 2026-10-17.
- The 00:40Z judgement call (feed-home direction) still open to 12:30Z. No new words from Byron
  since the last run (issues #22, #20, #18, #15, #7 unchanged).

## 2026-10-17T03:47Z run (reason: job_done nz-election-social-fix-1)

- Context: Codex window 64 percent at 03:47Z, resets in 5.2 days, even spread about 7 points
  per day; disk 19.0 GiB; no jobs running at the start. No new words from Byron (issues #22,
  #20, #18, #15, #7 unchanged).
- Job nz-election-social-fix-1 (fix, 439 s, rc 0) committed bc917a6 on
  change/nz-election-social-fix: QUERY shortened by dropping "New Zealand First" and "The
  Opportunities Party" (470 characters with the hourly suffix on the sample day), a
  diagnostic dict threaded through collect and classify, one stderr line on failure with an
  allowlisted inner code, HTTP status, window index and attempt (DIAGNOSTIC_CODES guards the
  message so an exception string can never leak), public codes and exit text unchanged, 25
  offline tests in test_social_diagnostics.py, intent/nz-election/social.md query block
  updated. Codex reports 367 passed, both evals PASS, lint ok.
- Verified on the host: evals/social-query-length/check.sh "PASS query length 470 of 512",
  test_social_diagnostics.py 25 passed, bin/lint ok. The full suite was not rerun here (three
  minutes); it runs in CI on the PR.
- Review verdict: diagnostics item accepted. One correction on the query: Codex kept the phrase
  "Opportunity Party" and dropped "The Opportunities Party", the party's actual name, so the
  surviving quoted phrase is the one that would not match tweets. Follow-up asks for
  "Opportunities Party" (matches the full name, four characters shorter than with "The"), the
  same edit in social.md, and the one term moved in the test Codex added in this job (no
  pre-existing test changes). Expected length 472 of 512. Dispatched 03:54Z as followup-1.md on
  the build thread (resume 01a147ee).
- Pages: social/poc/ returns 200 on the live site with the proof of concept label; pages.yml
  succeeded on 19c5e0c and ea21f02 after 79af3d6.
- Codex spend today: this fix round plus the follow-up come off tomorrow's share, as noted last
  run. No build dispatched.
- Next run: verify the follow-up commit, push, open the PR (body links intent, the incident
  run and the eval), fresh review, merge; the proving run is the scheduled 13:40Z social daily.

## 2026-10-17T03:59Z run (reason: job_done nz-election-social-fix-1, follow-up)

- Byron's words: none new this run. Open issues unchanged (#22, #20, #18, #15, #7).
- Follow-up e22221e on nz-election-social-fix-1 (209 s, thread 01a147ee): the phrase is now
  "Opportunities Party" in social.py, intent/nz-election/social.md and the named test. Codex
  reports 367 passed, eval PASS 472 of 512, pages-verify-polls-only PASS all, lint ok.
- Host verification at e22221e: evals/social-query-length/check.sh "PASS query length 472 of
  512"; test_social.py plus test_social_diagnostics.py 58 passed; bin/lint ok (375 text files).
  Diff against main: 5 files, 169 insertions, 12 deletions (social.py, the new diagnostics
  test, the eval, social.md). No pre-existing test edited beyond the phrase pin.
- Pushed change/nz-election-social-fix, PR #25 opened 04:02Z (body links intent, spec, plan,
  the incident run 38998322076 and the eval). Supervisor review logged on the PR: accept pending
  the fresh review and CI. Fresh review review-nz-election-social-fix dispatched 04:03Z
  (read-only, brief at state/jobs/review-nz-election-social-fix/prompt.md: length guard bound and
  placement, leak surface of the diagnostics, eval fidelity, no weakened checks, phrase effect on
  matching).
- Codex window 64 percent at 03:59Z, 5.2 days to reset, about 7 points per day even spread.
  This run spent one short follow-up and one review; no build dispatched today.
- Judgement calls: none this run. The 00:40Z line (feed-home change) still has its 12:30Z deadline.
- Next: CI and fresh review on PR #25, fix round if Important, squash merge, remove the worktree;
  proving run is the scheduled 13:40Z social daily.
- 04:08Z: fresh review (61 s) verdict request changes, two Important: (1) no runtime length
  guard, an oversized query still reaches the injected transport; (2) dropping "New Zealand
  First" and "Opportunity Party" changes coverage and the caption does not say so. It confirmed
  the eval arithmetic (522 on main, 472 on HEAD), no weakened checks, no diagnostic leak path;
  it could not run tests in the read-only sandbox. Both accepted: fix-2 dispatched 04:09Z on the
  build thread (followup-2.md): guard before reservation and transport with an allowlisted
  SOCIAL_QUERY_TOO_LONG code and boundary tests; restore "New Zealand First" (every other party
  keeps its full name), keep "Opportunities Party", one caption sentence on how phrases are
  chosen and where the list is recorded. Pre-existing tests stay untouched; a pinned phrase
  list stops the job. CI on PR #25 still running at 04:08Z.

## 2026-10-17T04:13Z run (reason: job_done:review-nz-election-social-fix)

- Byron's words: none new this run. Open issues unchanged (#22, #20, #18, #15, #7).
- fix-2 on nz-election-social-fix-1 (41 s, thread 01a147ee, 0 files changed) stopped as
  instructed: restoring "New Zealand First" measures 495 to 499 characters per hourly window,
  which fits the upstream 512 but fails the 490 headroom assertion in
  test_social_diagnostics.py. That assertion was added by this branch in bc917a6; the brief
  said "pre-existing tests" when it meant tests on main. Supervisor mistake, logged in
  state/mistakes.jsonl and CLAUDE.md (name the protected set by ref, not "pre-existing").
- followup-3 dispatched 04:16Z on the build thread (followup-3.md): the invariant is every
  composed query within the upstream limit for every producible date, the guard constant from
  item 1 is the bound, the headroom assertion is rewritten against that constant with a stated
  margin that admits 499 and rejects 513; items 1 and 2 otherwise as in followup-2.
- PR #25 CI: check passed (run 39000920812) on e22221e. Review job marker touched.
- Codex window 65 percent at 04:13Z, 5.2 days to reset, about 7 points per day even spread.
  Two short follow-ups today on the fix thread; no build dispatched.
- Judgement calls: none this run. The 00:40Z line (feed-home change) still has its 12:30Z deadline.
- Next: verify followup-3 on the host (guard boundary tests, eval number, full product tests,
  lint), push, second fresh review, CI, squash merge PR #25, remove the worktree; proving run
  is the scheduled 13:40Z social daily.

## 2026-10-17T05:15Z run (reason: idle)

- Byron's words: none new this run. Open issues unchanged (#22, #20, #18, #15, #7).
- followup-3 on nz-election-social-fix-1 (291 s, thread 01a147ee) landed 8742598: `hourly_queries`
  preflights every window of the day against `MAX_QUERY_LENGTH` 512 and raises
  `SOCIAL_QUERY_TOO_LONG` before any reservation or transport call; `refresh_social` runs the
  guard on the reserve step as well as the collect step, so a too-long query spends nothing on
  either path and takes the common closing path (run closed, diagnostic line with the code only).
  "New Zealand First" restored to the query and the intent; caption sentence on the phrase list;
  provenance records the phrases, pinned by a test. Boundary tests at 512 (sent) and 513
  (rejected, zero calls, zero reserved). The 490 headroom pin from bc917a6 moved to the constant.
- Host verification on 8742598: `evals/social-query-length/check.sh` PASS query length 495 of
  512; `test_social.py` 33 passed; full product suite 372 passed in 162.58 s; `bin/lint` ok
  (375 text files). Branch pushed 05:17Z, supervisor review round 2 logged on PR #25.
- Second fresh review (review-nz-election-social-fix-2, read-only, 46 s): accept with nits. One
  nit: the caption overstates query coverage (National, Labour, Greens are unquoted contextual
  terms; not every party has a short form); suggested wording given. The reviewer's sandbox could
  not run uv or the here-document eval, so it probed in memory: 495 actual, 512 sent with 24 calls
  and 7560 reserved, 513 rejected with 0 calls and 0 reserved. Decision: accept the wording, defer
  it to the social refinement round with the "over 1 days" nit (fix job, copy change, nothing pins
  it); logged on the PR.
- PR #25 CI check passed (run 39005622776, 4 m 34 s). Squash merged 05:21Z as b101e8b; worktree
  and local branch removed; Pages deploy of b101e8b completed success (pages.yml) and social/poc/ returned 200 at 05:23Z.
- Codex window 65 percent at 05:20Z, 5.1 days to reset, about 7 points per day even spread. Today
  so far: five build or fix jobs plus the POC thread and four reviews; today's share is spent, so
  no build dispatch (increment 7 waits for tomorrow's share).
- Judgement calls: none this run. The 00:40Z line (feed-home change) keeps its 12:30Z deadline;
  next-run-after set to 12:30Z. Issues and the 3 h heartbeat still wake the tick before then.
- Proving run for PR #25 is the scheduled 13:40Z social daily on 2026-10-17 (budget day rolled,
  so the credit cap from the failed run no longer blocks it). Read its status row, the credit
  ledger and the live social/poc/ page in the run after; an eval under evals/ if it fails.
- Next: at 12:30Z, if no reply from Byron, start the feed-home change (intent, spec with the
  frontend-design skill, read-only plan job); then the day-to-day verification milestone and the
  re-planned milestones in spec.md. Increment 7 dispatch on the next even-spread day.

## 2026-10-17T06:03Z run (reason: post_due:2026-10-17)

- Byron's words: none new this run. Open issues unchanged (#22, #20, #18, #15, #7).
- Wrote `posts/2026-10-17.md` (day 2 in the posts' numbering, where 2026-10-15 is day 0; the
  journal's earlier "day 3 NZ" labels counted from 1). It covers the window since the day 1 post:
  the product change (issue #7), PRs #6 and #8 to #25, the Pages verifier incident and hotfix,
  issues #18, #20 and #22, both judgement calls and their replies, the design track, the social
  POC and its first-run failure on the 512 character query limit, PR #25.
- Numbers in the post come from `bin/metrics` (site/data/metrics.json: weekly_merges 16,
  first_pass_ci 93.75, rework_cycles 18.33, repeated_mistakes 4, restore_time 0.3675 h,
  weekly_window 65) plus jq over state/ledger.jsonl (72 jobs since 2026-10-16T06:00Z: 19 build,
  19 fix, 27 review, 4 research, 2 plan, 1 docs; 5.35 h; 1.65M output tokens; 0 killed, 0 rc
  nonzero) and state/ticks.jsonl (98 ticks, 51 ran, 112.70 USD). `bin/lint` ok (384 text files).
- Live checks: social/poc/ returned 200; pages.yml latest run success on 5619bf3.
- Judgement calls: none this run. The 00:40Z feed-home call keeps its 12:30Z deadline;
  state/next-run-after stays at 2026-10-17T12:30Z.
- Codex window 65 percent (unchanged, no jobs this run). No dispatch: today's share is spent.
- Next: 12:30Z deadline, feed-home change if silent; 13:40Z social daily is the proving run for
  PR #25; increment 7 on tomorrow's share.

## 2026-10-17T08:46Z run (reason: issue #26)

- Byron's words, issue #26 (said in a Claude Code session on the host about 07:00Z, relayed
  verbatim by the operator): "Yea i want the home page to use this style:
  https://www.nbcnews.com/politics/2026-elections/midterms". Taken as the answer to the 00:40Z
  judgement call (feed home): yes, with NBC's midterms hub as the model, not a loose
  inspiration. The 12:30Z proceed time is void; the change starts now. The operator's fetch of
  the NBC page (eleven modules, top to bottom) is in the issue and is the shape the spec
  translates.
- Wrote intent/nz-election/home.md: intent, the NBC-to-MMP translation table, requirements H1
  to H12, design, constraints, verification, out of scope. Loaded the frontend-design skill
  first per the guardrail. Decisions in it, mine:
  - "Nothing is a card" (design.md, accepted in PR #21) meets a page whose model is a feed of
    cards. Resolution: NBC's structure (hero with countdown, battle-for-control strip, stat
    figures, race rows, directory grid, explainer) is adopted; its costume is not. A module is a
    rule-separated region in the existing ledger; race cards are rows with a rule between them.
    Alternative rejected: rounded shadowed cards, which would make the home a different design
    system from the other 78 routes a week before v1.
  - No rating labels (Solid, Lean, Toss-up). There is no electorate polling base, and a rating
    from one 2023 margin would read as a forecast on a site that says "calculated, not
    predicted". The electorates-to-watch module ranks the six smallest 2023 winning margins on
    unchanged boundaries and says so; changed-boundary electorates are excluded and the module
    says why. Alternative rejected: margins without a selection rule (unexplainable) and
    ratings with an invented method.
  - No headshots (licensing, per the issue); party mark beside the candidate name.
  - The countdown is rendered by the build in Pacific/Auckland time, never by a script, so a
    stale deploy shows a stale number with its updated time rather than a live-looking one.
  - /polls/ keeps every fragment id today's home has; the home keeps #seats and #polls. The
    plan must inventory the ids before anything moves (the route-count pin mistake from the
    social POC, generalised).
  These are inside the change Byron chose; no new judgement line sent. The electorate ranking
  rule is the one he might want otherwise: the day's post names it under Decisions.
- Dispatched plan-nz-election-home (read-only, cwd ., kind plan) at about 09:12Z, brief at
  state/jobs/plan-nz-election-home/prompt.md: fragment and route inventory, partials, data
  joins with empty states, CSS within the tokens, navigation, test inventory, at most three
  increments, concerns. The plan job is not a build; today's build share is spent (window 65
  percent, about 7 points per day, 5 days left), so the first home build goes out on
  tomorrow's share, ahead of increment 7 (Byron asked for the home; both are due by 26 Oct).
- Codex: 65 percent at run start. Disk 18.0 GiB. No other jobs running.
- Next: job_done for the plan; read it, interrogate it against H1 to H12, commit it as
  intent/nz-election/plan-home.md; 13:40Z social daily is the proving run for PR #25 (status
  row, credits ledger, social/poc/ live; eval if it fails); increment 7 and the home build on
  tomorrow's share, home first.
- 09:30Z addendum: plan-nz-election-home returned in 221 s (rc 0, window 65 percent after). Read
  against H1 to H12: 242 lines, a pin table with file and line for every route and image count
  (78 to 79 routes, 215 to 296 populated images, two OG specimens replaced by 79), partials for
  the strip, data joins with unavailable states, two increments, eight concerns. Accepted with
  five decisions appended to intent/nz-election/plan-home.md: two increments; pages.yml OG step
  with Playwright authorized for H-b (the plan found deployment never ran the harness, so H8 as
  specified would not survive a fresh Actions build); H5 loses the incumbent marker (published
  data cannot support it without name inference) and East Cape stays eligible; fold pressure
  comes back as measured geometry, never a weakened check; social module policy separate from
  the POC's. home.md amended to match (H5, H8). Worktree .worktrees/nz-election-home on
  change/nz-election-home created at 6687041; H-a brief at state/jobs/nz-election-home-a/prompt.md,
  dispatch on the 18 October share (first run after 00:00Z), before increment 7.
- Next run at 13:50Z: the 13:40Z social daily (proving run for PR #25), then next-run-after
  00:05Z 18 Oct for the H-a dispatch.
- 09:02Z addendum: a tick fired on issue:08:46:43Z. That event was the supervisor's own 08:46Z
  comment on issue #26 (read receipt and the spec summary), not a reply from Byron; open issues
  unchanged, no Byron words. Idle run: committed the plan job's last.md and the tick log, nothing
  dispatched, Codex 66 percent, disk 18.0 GiB. next-run-after stays 13:50Z. Note for bin/tick:
  the supervisor's own issue comments retrigger a run; one idle run cost about 0.8 USD. A one-line
  filter on the comment author (skip when the latest event is byronxlg from the lab's gh session
  within the last run) is a tooling fix for a later run, not this one.

## 2026-10-17 12:04Z run (heartbeat: 3 h since the last run)

- No Byron words since issue #26; open issues unchanged; next-run-after was 13:50Z and the tick's
  3 h heartbeat rule fired anyway.
- Incident, found by the run-list check: "NZ election hourly" failed at 07:00Z (run 39011994985)
  and 11:39Z (run 39029509938), both `FAIL refresh: parse_drift`; the publish step then exits 1
  on the handled failure. The polls status row on the live site: state stale, error parse_drift,
  last good 01:20Z (run 38990427608), message "Refresh failed; retained last-good data." The
  08:42Z and 09:30Z runs did not look at the hourly workflow and missed the 07:00Z failure; the
  day-to-day verification milestone (issue #18) needs the run list in every run, not only when a
  job finishes. Social daily by-hand run status row still SOCIAL_UPSTREAM_FAILED from 03:19Z,
  expected until the 13:40Z proving run.
- Reproduction on the host (fetch.acquire plus parse_polls, revision 1380694545 fetched 12:06Z):
  ParseDrift invalid_dates, locator "8–11 Aug 2026 / 2026-08-12", the 1 News–Verian row. The
  row has a documented exception in config/party-map.json but keyed to revision 1380524613 (the
  fixture); Wikipedia moved to 1380694545 at 08:21Z (an edit elsewhere on the page), the
  exception stopped matching, and a row the lab had already accepted failed the whole refresh.
  Neither the log nor the status row named the reason or locator; same shape as the social
  incident (03:19Z), where the status and inner error were swallowed.
- Judgement: this is a fix to a production incident, allowed on a spent share ("nothing else
  today but fixes"); the polls are the core of the site and the workflow stays red every hour
  until fixed. Alternatives rejected: pin a new revision in the exception (breaks again on the
  next edit); wait for tomorrow's share (another 12 h stale). No board line: a reversible single
  change.
- Eval evals/polls-date-exception-revision (task.md, check.sh) committed as b00ae94 on
  change/nz-election-polls-fix in .worktrees/nz-election-polls-fix from main 8a5392d; the check
  parses the pinned fixture under revision 9999999999 and failed on the host today with the
  incident's exact reason and locator. Brief state/jobs/nz-election-polls-fix-1/prompt.md: two
  invariants (an exception describes a row, not a revision, with source and reason kept and
  undocumented mismatches still drifting; parse_drift names reason and locator in the log and
  step summary), protected set named by ref (tests on main at 8a5392d; test_pinned_wikitext's
  date_exceptions pin stays true), shape left to the engineer. Dispatched 12:13Z, kind fix,
  workspace-write. Codex window 66 percent at 08:49Z.
- Next run on job_done: review per REVIEW.md, host verification (eval, pytest, lint, plus the
  live revision through the probe: python with fetch.acquire and parse_polls), PR, fresh review,
  merge; the proving run is the next scheduled hourly after the merge (status row fresh, run
  green). 13:50Z: the 13:40Z social daily as planned. Add to the daily post under incidents.

## 2026-10-17T12:20Z run (job_done: nz-election-polls-fix-1)

- Codex window 67 percent at 12:13Z, resets in 4.8 days, about 7 points per day. Disk 18.0 GiB.
- nz-election-polls-fix-1 landed beb364c (285 s, 1.1M input tokens, 4.3k output). The engineer
  chose: a date exception matches a row by visible text, data-sort-value and pollster, on any
  revision, and only when the entry carries `source` and `reason`; `party-map.json`'s entry
  swaps `revision` for an explicit `source` oldid URL; `dates()` validates the sort value as an
  ISO date before the mismatch check (tighter than before); `refresh.py` appends the reason and
  locator JSON to the status message on ParseDrift, and the `FAIL refresh: parse_drift` log line
  carries it; 29 new tests in test_date_exception_revision.py; no test on main at 8a5392d edited;
  last.md not committed (the earlier mistake did not repeat).
- Host verification: eval PASS on revision 9999999999; 401 passed in 164 s (372 on main plus
  29); lint ok (393 files); live probe (fetch.acquire plus parse_polls) on the current revision
  1380694545 parsed 43 rows with the exception applied at table:15/row:19.
- Pushed, PR #27 opened 12:30Z with the intent, spec, plan-m2, eval and brief links and the four
  command outputs. Supervisor review logged on the PR: accept pending fresh review and CI, both
  invariants checked against the diff.
- Fresh review review-nz-election-polls-fix dispatched 12:32Z read-only on the worktree. Brief
  mistake: it names product/nz_election/tests/test_refresh.py, which does not exist; the
  reviewer has the other two files and the eval.
- Hourly run list at 12:2xZ: 11:39Z and 07:00Z failed, 01:20Z last success; the proving run is
  the first scheduled hourly after the merge.
- Next: merge PR #27 when the fresh review accepts and CI is green, confirm Pages, watch the
  next hourly; 13:50Z the 13:40Z social daily (proving run for PR #25); first run of 18 Oct UTC
  dispatches nz-election-home-a, increment 7 after it.
- 12:3xZ addendum: fresh review (46 s class, read-only; its sandbox blocked uv and the eval's
  here-document, so it probed in memory: 28 rejection probes pass, incident reproduced on main
  and parsed on HEAD) returned request changes with one Important: refresh.py publishes
  exc.locator, and for invalid_attributes, unknown_template, unknown_pollster,
  unknown_party_mapping and the dates() path that locator is page text (reproduced a status
  message carrying a data-sort-value attribute string). Supervisor accepted: the brief said
  "nothing but the row's locator" and the diff checked only the invalid_dates case. Logged on
  PR #27. Fix round followup-1.md dispatched 12:40Z on the build thread: public outputs carry
  the reason and a structural locator (table:N/row:M or line) and nothing from the source
  body; marker-string regression test through refresh() and main(); tests on main at 8a5392d
  untouched (they match ParseDrift on reason only, checked by git grep). CI on beb364c still
  pending at 12:40Z. Social daily 13:40Z not yet run.
- 12:3xZ to 12:38Z addendum: fix-1 landed 05d9b0a (the engineer's shape: ParseDrift gains
  public_locator, empty by default, set by a parse_polls wrapper from scanner positions only,
  line:N or table:N/row:M; refresh.py publishes that; 7 marker tests through refresh(), main(),
  persisted status and the summary file). Host: 408 passed in 165 s, eval PASS, lint ok, live
  probe revision 1380694545 43 rows with the exception at table:15/row:19. Pushed, supervisor
  review logged. Second fresh review (review-nz-election-polls-fix-2): accept, no findings;
  its sandbox again blocked uv and the here-document, in-memory eval PASS. CI green on 05d9b0a
  (3m02s). PR #27 squash merged 12:38Z as 433b653, worktree and branch removed. Proving run:
  "NZ election hourly" dispatched by hand on 433b653, run 39033294991, completed success at
  12:38Z with "PASS refresh: polls bundle"; the status row should read fresh once Pages
  redeploys, to be confirmed at 13:50Z with the scheduled hourly after it. The incident ran
  11 h 18 min from the last good refresh (01:20Z) to the passing run; its eval is
  evals/polls-date-exception-revision. Attempts on the nz-election change now 25.
- Brief mistake, this run: the first fresh review brief named a test file that does not exist
  (test_refresh.py); harmless, the reviewer ran the other two. Not a repeated Codex mistake,
  so no AGENTS.md line.
- next-run-after set to 2026-10-17T13:50Z (1792245000) for the social daily and hourly checks.

## 2026-10-17T12:49Z run (job_done re-fire)

- Reasons: job_done for nz-election-polls-fix-1, review-nz-election-polls-fix and
  review-nz-election-polls-fix-2. All three were handled in the 12:20Z run (PR #27 merged as
  433b653) but their `reviewed` markers were never touched, so the tick re-fired. Supervisor
  mistake: step 2 ends with `touch state/jobs/<id>/reviewed`; done now for all three.
- Pages for 433b653 confirmed: pages.yml run 39033354842 success, nz-election/ returns 200.
- No dispatch (today's Codex share spent, window 68 percent). next-run-after stays 13:50Z.

## 2026-10-17T13:50Z run (idle)

- Reasons: idle, the 13:50Z marker for the social daily and hourly checks. Codex window 68
  percent, 4.8 days left, about 7 points per day; nothing dispatched (today's share spent).
- Live status.json on code_sha 433b653: polls fresh, last success 12:38Z (run 39033294991,
  revision 1380694545); social still the 03:19Z SOCIAL_UPSTREAM_FAILED row from run
  38998322076, as expected until the daily runs again.
- Scheduled runs late: the hourly cron is :17 and no run exists for 12:17Z or 13:17Z (the last
  scheduled one fired 11:39Z for the 11:17Z slot); the social daily cron 13:40Z had not fired
  by 13:50Z. Both read as GitHub schedule drift, not a failure, nothing in the repo changed
  the triggers. No action; recheck at 14:35Z. If the social daily still has not run by then,
  dispatch it by hand (it is the proving run for PR #25) and note the drift in the day 3 post;
  if the hourly misses two slots in a row, the same.
- next-run-after set to 2026-10-17T14:35Z (1792247700). Then 00:05Z 18 Oct for the home-a
  dispatch as planned.

## 2026-10-17T14:51Z run (idle)

- Reasons: idle, the 14:35Z recheck of the late scheduled runs. Codex window 68 percent,
  4.7 days left, about 7 points per day; nothing dispatched to Codex (today's share spent).
- Scheduled runs still missing at 14:51Z: the hourly cron (:17) has no run for the 12:17Z,
  13:17Z or 14:17Z slots (last scheduled run 11:39Z), and the social daily cron (13:40Z) had
  not fired. githubstatus.com reported Actions operational and no open incident; the merge
  433b653 did not touch a workflow file; all four workflows are active. Cause unknown, read as
  GitHub scheduler drift; the lab's safety net is the tick's 3 h heartbeat plus by-hand
  dispatches. Logged as an operational incident for the day 3 post; no eval, since nothing in
  the repo failed.
- The budget day is the NZ date (social.py, Pacific/Auckland), so at 14:52Z (03:52 NZDT on
  18 Oct) a by-hand social run reserves against 2026-10-18 and is not blocked by the failed
  run's 7560 on 2026-10-17; it samples yesterday NZ (2026-10-17), the same day the 13:40Z cron
  would have. Both runs dispatched by hand at 14:52Z, as the 13:50Z entry said:
  - NZ election hourly run 39042615962: completed success at 14:53Z; live status.json polls
    row fresh, last_success_at 14:52:52Z (polls had been stale since 12:38Z).
  - NZ election social daily run 39042618322 (the proving run for PR #25): reserve job
    success (credits.json on the data branch gained a 2026-10-18 row, reserved 7560, requests
    0), collect job step "Sample X and classify in memory" running from 14:53Z and still
    running at 15:03Z. Result recorded by the next run (status row, credit ledger, the
    social/poc/ page; an eval if it fails).
- next-run-after set to 2026-10-17T15:45Z for the social daily result; then 00:05Z 18 Oct for
  the home-a dispatch.

## 2026-10-17T15:53Z run (idle)

- Reasons: idle, the 15:45Z check on the social daily proving run. Codex window 68 percent,
  4.7 days left, about 7 points per day; nothing dispatched (today's share spent).
- Scheduler drift over: the hourly cron fired at 15:39Z (run 39046005942, schedule, success),
  the first scheduled run since 11:39Z. No by-hand hourly needed this run.
- Social daily run 39042618322 (proving run for PR #25): reserve success, collect step "Sample
  X and classify in memory" still running at 15:53Z, one hour in. Expected: social.py sleeps
  330 s between pages (at most 12 pages per rolling hour) and the 7,800 cap allows about 24
  pages, so a full collect takes about 130 min against the job's 180 min timeout; finish
  expected 17:05Z to 17:15Z, then publish. Not a failure signal yet. Live social/poc/ 200.
- next-run-after set to 2026-10-17T17:20Z to read the result (status row, credits ledger,
  social/poc/ page; an eval if it fails); then 00:05Z 18 Oct for the home-a dispatch.

## 2026-10-17T17:32Z run (idle)

- Reasons: idle, the 17:20Z read of the social daily proving run. Codex window 68 percent,
  4.6 days left, about 7 points per day.
- Incident: social daily run 39042618322 (proving run for PR #25, by hand 14:52Z) failed.
  Reserve and collect succeeded (24 requests, 7,560 credits spent on budget day 2026-10-18 NZ),
  then the first classification response failed: `social diagnostic:
  SOCIAL_CLASSIFICATION_FAILED http_status=200 window_index=0 attempt=1`. The publish step
  published the handled failure row (data 999b4af, state unavailable, SOCIAL_UPSTREAM_FAILED)
  and exited 1 by design. The late scheduled run 39050256510 (cron fired 16:37Z) stopped at
  reserve on SOCIAL_CREDIT_CAP (data 55b2c0a): expected, the by-hand run had spent the day.
- Diagnosis on the host: 24 probes against api.typesafe.ai with the real key (one post through
  classify(), then twelve varied texts, then twelve tweet-shaped texts: emoji only, URL only,
  mentions, te reo, 3000 characters, all caps, ambiguous party lists) all returned 200 with
  model jev-1.13.0 and passed every check in classify(). Cause unknown: every structural check
  raises a bare ValueError, so the log cannot name it, and the sample is never stored. Lesson,
  same shape as the 03:19Z incident: a handled failure must name its check; and one bad post
  must not throw away a day of credits after the collect spend.
- Eval `evals/social-classify-exclusion` (task.md, check.sh) committed as 5071194 on
  change/nz-election-social-fix2 in .worktrees/nz-election-social-fix2 from 433b653; it fails on
  main today (raises SOCIAL_CLASSIFICATION_FAILED, no check name).
- Judgement: dispatched nz-election-social-fix2 at 17:52Z as a build round (not a fix), because
  main's tests pin the exclusion dict (test_social.py:89) and the diagnostic line
  (test_social_diagnostics.py) and must move with the registered set; brief at
  state/jobs/nz-election-social-fix2/prompt.md: per-post exclusion counted and shown in the
  caption, run still fails above a 10 percent unclassified share, diagnostic carries a fixed
  structural `check` name, ties valid, nothing weaker. Spent on today's share despite the
  ration because every scheduled run until the fix lands burns 7,800 X credits for nothing; the
  next scheduled social daily is 13:40Z 18 Oct (budget day 2026-10-19 NZ) and the fix should be
  merged before it. Alternative rejected: disabling the social cron until the refinement round
  (a workflow edit for a day's gain, and the POC would show nothing to Byron).
- Hourly: on schedule (15:39Z success). Pages unchanged since b101e8b.
- Next: on job_done review social-fix2 (eval PASS, pytest, lint, caption screenshot), PR, fresh
  review, merge before 13:40Z; then home-a dispatch at the first run of 18 Oct UTC (next-run-after
  set to 00:05Z 18 Oct).

## 2026-10-17 17:49Z (job_done: nz-election-social-fix2)

- Codex job nz-election-social-fix2 (build, 511 s, thread 01a14af1-fc0d-7911-846e-baadd421997d)
  committed 983f112 on change/nz-election-social-fix2: per-post exclusion `classification`
  (EXCLUSIONS tuple shared by aggregate, validator and caption), 10 percent bound on posts sent,
  `check` names from a local frozenset printed per excluded post and on the fatal line, ties
  valid, tolerance .001 kept (observed responses sum to exactly 1.00). Window 69 percent.
- Host verification at 983f112: evals/social-classify-exclusion PASS (2 classified, 1 excluded,
  check named); evals/social-query-length PASS 495 of 512; pytest 475 passed in 168.93 s;
  bin/lint ok (401 text files); fixture build PASS social, PASS build 78 routes; rendered
  caption "Excluded: duplicates under 5, unsupported language or length under 5, relevance below
  0.8 under 5, invalid classification under 5." Codex could not run the screenshot harness
  (Chromium sandbox); caption-only page change, no host screenshot run.
- Branch pushed, PR #28 opened, supervisor review logged (accept pending, two nits: bound judged
  after the whole sample; stale code in the diagnostic after a good batch). CI green on 983f112.
- Fresh review review-nz-election-social-fix2 (138 s, read-only; gh and uv unavailable in its
  sandbox, probed in-memory): request changes, four Important. (1) decode failures (oversize,
  invalid JSON, non-object) became exclusions where main failed with SOCIAL_RESPONSE_LIMIT or
  SOCIAL_INVALID_RESPONSE: weaker than main. (2) The stale code after a good batch misreports a
  later aggregate failure. (3) An all-invalid sample makes 480 Jev calls before the bound trips.
  (4) Rows with the old three-key exclusions would fail the strict validator.
- Judgement: items 1 to 3 to fix round 1 on the build thread (followup-1.md: decode failures
  fatal again with original code plus check=decode, since the incident printed
  SOCIAL_CLASSIFICATION_FAILED and so was post-decode; exclusion context kept apart from the
  live failure state; stop sending once classification exclusions exceed 10 percent of posts
  sent, at most 49 calls for 480 invalid). Item 4 accepted with reasoning on the PR: the data
  branch holds only social/credits.csv and credits.json, no daily rows were ever published (both
  real runs failed before aggregate), the validator stays strict. Both nits I had deferred were
  the reviewer's items 2 and 3: the fresh review was right to rank them Important, a daily run
  that wastes Jev calls or misnames its failure is the incident shape again.
- Cost: this is the fourth job on today's share (window 56 at 01:31Z, 69 at 17:53Z, about 13
  points against an allowance of 7); spent because every scheduled social run until the fix
  lands burns a day of X credits. Nothing else is dispatched today; home-a goes out on 18 Oct UTC.
- Next: on job_done host-verify fix-1 (eval, pytest, lint, fixture), push, second fresh review,
  merge before the 13:40Z 18 Oct social daily, confirm Pages; home-a first run of 18 Oct UTC.
- Correction: bin/codex-run copies the --prompt file to state/jobs/<id>/prompt.md, so the fix
  dispatch overwrote the build brief with followup-1.md (same for every earlier follow-up on a
  build id). Restored the build brief at that path from e1db21e; follow-ups live in their own
  files. The second fresh review brief should cite the build brief by ref if this repeats.

## 2026-10-17T18:16Z run (job_done: social-fix2 fix-1, review re-fire)

- Context: window 70.0 percent at 18:16Z, resets in 4.6 days, allowance about 7 points per day;
  disk 20.0 GiB; no Codex job running. No new words from Byron.
- Fix round 1 on change/nz-election-social-fix2 landed as 58cc131 (284 s). Host verification:
  eval social-classify-exclusion PASS (2 classified, 1 excluded, check named), eval
  social-query-length PASS 495 of 512, lint ok (403 files), pytest 477 passed in 166 s, fixture
  build PASS social on a fresh out directory (the reused /tmp/social-fixture from the 983f112
  check stopped on SOCIAL_CREDIT_CAP: the earlier run's credit ledger was still in it; not a
  defect, noted on the PR). Protected set unchanged: 58cc131 touches social.py and the branch's
  own test_social_exclusions.py only.
- Diff read: decode runs in classify under check=decode and re-raises with the original code;
  the last exclusion lives apart from the live failure fields and completion sets
  check='complete'; candidates are collected before the first Jev call and the loop raises as
  soon as exclusions exceed 10 percent of the sent count (enforce_bound, on in refresh_social,
  off for the eval path). Pushed, supervisor review logged on PR #28.
- Fresh review 2 (review-nz-election-social-fix2-2, read-only): accept, no findings; its probes
  pinned 49 of 480 calls, eight fatal decode cases, window index by original post index,
  protected tests identical to 983f112. Logged on the PR with the host pytest line.
- Scheduled hourly missed 16:17Z and 17:17Z (last cron fire 15:39Z, itself 22 min late); the
  18:17Z one had not appeared by 18:18Z. Dispatched by hand 18:18Z: run 39057520372 success.
  Second day of GitHub scheduler drift; the hourly cron and the social daily cron (13:40Z) need
  checking every run until it steadies. A watchdog in the tick (dispatch the hourly when the
  last success is older than 90 min) is a one-line tooling change worth making tomorrow.
- Cost: two more jobs on today's share (fix 284 s, review); window 70 at 18:16Z. Nothing else
  dispatched today. Home-a goes out first run of 18 Oct UTC, increment 7 after it.

## 2026-10-17T21:25Z run (heartbeat) (3 h since the last run; next-run-after was 00:05Z 18 Oct)

- Pages for 28a4a08 confirmed: pages.yml success on 28a4a08 and d27cf7b, social/poc/ live 200.
- Scheduled hourly missed 19:17Z, 20:17Z and 21:17Z (last cron fire 18:31Z). Third drift episode
  today. Dispatched by hand 21:25Z: run 39070913572 success. Polls status had last_success_at
  18:32Z before it.
- Watchdog added to bin/tick (one tooling change, reversible, journalled here rather than a
  board line): when no hourly run is queued or running and the newest run of any conclusion
  started over 90 min ago, the tick dispatches nz-election-hourly.yml and logs it. Age of the
  newest attempt, not the newest success, so a failing hourly is not redispatched every ten
  minutes; failures stay with the supervisor. Verified: bash -n ok, the jq expression returned
  44 s against the live run list; the block itself runs on the next tick where no supervisor
  holds the pid file. The social daily cron (13:40Z) has no watchdog; the 13:50Z run checks it.
- Live status row for social reads "Collection limit reached; showing data through no previous
  data" while there is no good run yet: a wording defect for the social refinement round (third
  caption item, with the "over 1 days" nit and the fresh review's caption wording).
- No Codex dispatched: window 70 percent at 21:25Z, resets in 4.5 days, about 7 points per day;
  today spent 14 (56 at 01:31Z). Home-a goes out first run of 18 Oct UTC as planned, increment 7
  after it on the same or next share.

## 2026-10-18T06:40Z run (post_due:2026-10-18) (first successful run since 21:25Z 17 Oct)

- Claude usage limit: ticks from 00:08Z to 06:30Z woke ten runs, each rc 1 "You've reached your
  Fable limit". Nothing reviewed or dispatched for 6.5 h; the planned 00:05Z home-a dispatch slipped.
  This run is on a different model.
- Hourly watchdog in bin/tick verified by the run list: workflow_dispatch runs at 01:38Z, 03:09Z,
  04:39Z, 06:10Z, scheduled fires only at 00:04Z and 04:39Z, all success. At 04:39Z the watchdog
  and the late cron fired 2 s apart (two runs that hour, harmless); a tighter check is a later
  tooling item.
- Dispatched nz-election-home-a 06:42Z as written (bin/codex-run ... --cwd .worktrees/nz-election-home
  --kind build --background), worktree at 6687041. Window 70 percent, 4.1 days to reset, about 7
  points per day; today's share covers home-a and its review; increment 7 next share.
- bin/metrics: first_pass_ci and restore_time now null (n 0); yesterday 93.75 percent and 0.3675 h.
  Not diagnosed this run; flagged in the post, to check before quoting again.
- Day 3 post written (posts/2026-10-18.md). No judgement calls sent; none pending.
- Next: review home-a on job_done (host build PASS 79 routes, screenshots looked at, fresh review,
  PR); read the 13:40Z social daily, proving run for PR #28.

## 2026-10-18 07:02Z (job_done nz-election-home-a)

- home-a landed 9950c56 (972 s; Codex window 2 percent after the weekly reset). Branch was based on 6687041; rebased onto bb0690d as 7e27c97. Conflicts only in intent/nz-election/home.md and plan-home.md; kept main's (the supervisor's accepted versions; Codex's home.md edit said the same "no incumbent marker" decision in other words, and plan-home.md was a recovered copy).
- Host: 578 passed, verify PASS all, lint ok. Screenshot harness failed at screenshots.py:341: `.electorate-directory li` counts 78 on the populated artifacts because the "Local polls not matched" list (7 items) sits in the same section. Same assertion on main; latent until real electorate polls arrived. Goes into fix-1 as a scoped count, not a weaker one.
- Home screenshots taken by hand (390x844, 1280x800, full page) and looked at: modules as home.md describes; at 390 the seat strip outlines cross the legend ("GRN 1|5"). Candidate lists are long run-on lines at 390 (nit, H-b).
- PR #29 opened, supervisor review request changes (two items) logged on the PR; fresh review review-nz-election-home-a dispatched read-only.
- Next: read the fresh review, send its findings plus the two supervisor items as fix-1 on the build thread 01a14dbe-32bb-7a50-90bc-720111662c5a; 13:40Z social daily is the proving run for PR #28; increment 7 on the next share.

## 2026-10-18 07:22Z (job_done review-nz-election-home-a)

- Fresh review review-nz-election-home-a (138 s, window 3 percent): request changes, one Important: test_design.py:112 measures home only, so the transfer-byte and reserved-font budgets no longer cover the explorer on /polls/. Accepted: moving the page must not weaken main's checks. Its probes passed (provenance, absent families, ties and missing results excluded, East Cape eligible, 92 old root ids preserved on /polls/); it could not run pytest (uv cache sandbox) or reach gh. Logged on PR #29.
- fix-1 nz-election-home-a-fix-1 dispatched 07:25Z on the build thread 01a14dbe (resume, workspace-write, own job dir so the build brief is not overwritten): legend overlap at 360/390, harness count of li[id^=electorate-] == 71, budgets on both home and polls with page-named messages. Protected tests named by ref (main at bb0690d).
- Next: host-verify fix-1, push, second fresh review, merge when CI green; 13:40Z social daily is the proving run for PR #28.

## 2026-10-18 07:33Z (job_done nz-election-home-a-fix-1)

- fix-1 ca77770 (322 s, window 4 percent): legend connectors capped at 6 px plus a legend_check in the harness; directory count scoped to li[id^="electorate-"] == 71; transfer-byte and font budgets measured on home and /polls/ with page-named messages and negative tests. Codex could not launch Chromium (sandbox) and claimed no harness PASS.
- Host: 580 passed, lint ok. Live data branch build PASS all, harness PASS 79 routes 210 images, but seats are withheld on live data ("Incomplete party coverage; seats withheld.", same on production since at least 17 Oct), so the legend check passed vacuously there. Rebuilt from the test_home populated fixture (refresh end_date 2026-07-18): PASS all, harness PASS 79 routes 219 images; home at 360 and 390 looked at, labels clear of every rule.
- Codex committed its round report as last.md at the repo root; removed in 085ffbd (copy at state/jobs/nz-election-home-a-fix-1/report.md). Second time a report reached a branch (social POC r1).
- Pushed 085ffbd, supervisor review accept logged on PR #29, second fresh review review-nz-election-home-a-2 dispatched read-only.
- Open question for a later run: production has shown no seat estimate for days on "Incomplete party coverage"; check whether that is the intended rule for the current polls or a defect before quoting the home headline anywhere.
- Next: on job_done merge PR #29 if accept and CI green, confirm Pages; 13:40Z social daily is the proving run for PR #28; increment 7 on the next share.

## 2026-10-18 08:12Z (job_done review-nz-election-home-a-2)

- Second fresh review of PR #29 (read-only, 128 s): accept, no Important or Nit findings; budgets home 11,833 and polls 31,362 gzip bytes; it noted a local artifacts bundle failing INVALID_SOCIAL_FIELDS, against a site dir whose manifest names ca77770 (its own words), not the head. Logged on the PR with the supervisor accept.
- CI pass on 085ffbd; PR #29 squash merged 08:14Z as 29bf079; worktree .worktrees/nz-election-home removed (force: only an untracked artifacts/ build dir). Pages deploy of 29bf079 queued at run end, not yet confirmed.
- Increment 7 (markets, daily workflow): branch change/nz-election-7 rebased onto 29bf079 (captures now 37e3b9d); brief updated for the new base (route count 79, markets module under #polls on the home hub per home.md line 49, polls template moved); dispatched nz-election-7 08:2xZ in .worktrees/nz-election-7. Codex window 5 percent, allowance about 14 points per day.
- Live site still shows seats withheld ("Incomplete party coverage"); not yet looked into whether that is the latest poll's coverage or a defect. Hourly 08:12Z success.

## 2026-10-18 08:34Z (job_done nz-election-7)

- nz-election-7 176944f (833 s, window 7 percent): normalized Polymarket rows from the five Gamma captures, markets module on the home, nz-election-daily.yml, Pages trigger, runbook section. Stray last.md in the worktree removed.
- Host on 176944f: 531 passed; fixture refresh, daily_refresh, build, verify all: PASS refresh: daily bundles, PASS build: 79 routes, PASS markets, PASS all; lint ok (433 text files); screenshot harness PASS 79 routes 219 images.
- Markets module screenshotted on its own by hand (fixture build, 390 and 1280) and looked at: about 16,000 px tall at 390 and 10,600 px at 1280; 29 "Not available" rows (Polymarket placeholder contracts "Person A" and so on), 54 per-row "Resolution criteria" disclosures, volume and liquidity as raw floats ("13118.4606556"). The harness passed because nothing measures module height or unpriced rows.
- Pushed, PR #30 opened, supervisor review request changes logged (three Important: height, placeholder rows, raw floats; one Nit: one rules link per event); the fix must add a check that would have failed here. Fresh review review-nz-election-7 dispatched read-only with the brief's success_order requirement, the daily workflow's freeze, concurrency and transport, and the moved tests as its checklist.
- Pages for 29bf079 confirmed (pages.yml success; /polls/ 200). Hourly last success 08:12Z.
- Next: on the review's job_done, one combined fix-1 on the build thread 01a14e12 with both lists.

## 2026-10-18 08:53Z (job_done review-nz-election-7)

- Fresh review review-nz-election-7 (108 s, window 7 percent) on 176944f: request changes, two Important: (1) daily_sources.py:58 falls back to committed captures on a Gamma failure, so daily_refresh records fresh and exits 0; (2) malformed market observed_at gets INVALID_TIMESTAMP in export but INVALID_MARKET in the parser. Its pytest was blocked by the sandbox. Logged on PR #30.
- Combined fix-1 nz-election-7-fix-1 dispatched about 08:56Z on the build thread 01a14e12 (state/jobs/nz-election-7/followup-1.md): the four supervisor items, the two fresh-review items, and a harness check that must fail on 176944f. Protected tests named by ref: main at 29bf079.
- Next: on job_done, host-verify (pytest, lint, harness, module height at 390 and 1280 looked at), push, second fresh review, merge when CI green.

## 2026-10-18 09:14Z (job_done nz-election-7-fix-1)

- fix-1 5e3ef85 (753 s, window 9 percent): Codex reported 639 passed and lint ok; its Chromium was blocked by the sandbox, so no screenshot claims.
- Host verification: pytest 639 passed, bin/lint ok, verify.py all PASS (incl. markets, home), screenshot harness PASS 79 routes 219 images on the populated build plus two market closeups. Module 358x733 at 390 (bound 844), 1072x644 at 1280; looked at: priced contracts only, percentages rounded, one rules link per event, licence line exact. The harness on the 176944f build fails with UNPRICED_OR_PLACEHOLDER_CONTRACT gamma-2116547, so the new check would have caught the original defect.
- Supervisor review logged on PR #30; branch pushed; second fresh review review-nz-election-7-2 dispatched (read-only). CI pending at write time.
- Next: merge if accept and CI green, confirm Pages; seats withheld on the live home to look into; H-b brief; 13:40Z social daily is the proving run for PR #28.
