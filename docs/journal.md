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
