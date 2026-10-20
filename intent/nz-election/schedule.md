# NZ election: dated schedule to 14 November

Operator re-plan, 2026-10-20 (Byron, Telegram 00:23Z: "fixed up the schedule ... to have it run
autonomously"). Supersedes the M1 to M4 dates in `spec.md` (written when the lab ended 4 Nov) and
the 20-day plan sent on 16 Oct. The lab now runs to at least 14 Nov (issue #18) and Codex stops
about 2026-11-07 03:14Z (D63, "After Codex" in `prompts/supervisor.md`). Where the lab stood on
20 Oct: M1 live; M2 increments 4 to 7 merged, deployment acceptance open; the 538 look rounds
(#32, #34, #40) in flight as PR #45; M3 not started (no replay, waterfall, advance or campaign
pipeline in `product/`).

This file is the "milestone due" that `prompts/supervisor.md` step 4 plans from. Each line is a
date the item is live on Pages and verified, not dispatched. The supervisor moves a date only
with a journal line saying why, and tells Byron (issue) when a milestone slips more than a day.
Order inside a milestone is the supervisor's call; two jobs at a time when files are disjoint.

| Due (NZ) | Milestone | Done when |
|---|---|---|
| Wed 21 Oct | Page plans: home, vote, electorate | reader-question research job per page, `pages/<page>.md` committed and lint-clean, top questions sent to Byron ("Reader first, then UI" in `prompts/supervisor.md`); vote first if advance and overseas voting help is still missing (`audiences.md` page plan) |
| Sat 24 Oct | Look: #40 closed | moved from Thu 22 Oct by the reader-first gate (Byron, Telegram 2026-10-20 01:41Z); remaining look work rebuilt from the accepted page plans, question test logged in the PR; PR #45 merged, absent data never rendered (build check), hero graphic, electorate map, reference-weight charts, side-by-side review against 538 logged, link to Byron |
| Sun 25 Oct | M2 accepted | plan-m2 "M2 deployment acceptance" ticked: daily and hourly proven on real runs, screenshots on phone and desktop accepted |
| Mon 26 Oct | Advance voting (req 11) | daily capture of the EC advance-voting count runs from the first published day; chart shows only days that exist |
| Fri 30 Oct | M3 night client (req 9, 10) | `verify.py night` and `verify.py waterfall` PASS; replay of the demo and 2017/2020/2023 archives on `/night/`; live-feed probe from the deployed origin recorded (CORS/WAF), dated fallback if it fails |
| Mon 2 Nov | Campaign (req 12) | donations over $20k and the pollster record PASS `verify.py campaign`; if it cannot land by 2 Nov, drop it from the election-night scope with a journal line, do not let it eat the rehearsal |
| Wed 4 Nov | Harden | evals green, `verify.py all` PASS, every scheduled workflow green 3 days running, s197 freeze for the social daily before 19:00 NZDT 7 Nov in place and tested |
| Thu 5 Nov | Last Codex build dispatched | after this only fixes to in-flight work; `docs/codex-notes.md` entry written (what Codex was doing, every worktree) |
| Fri 6 Nov | Rehearsal | full election-night replay at 60x against the deployed site, timed, with the runbook; defects fixed or written into the runbook |
| Sat 7 Nov | Election night | live mode on the 2026 feed from 19:00 NZDT, the lab operates it Claude-only (Codex gone mid-afternoon); journal through the night |
| 8 to 13 Nov | Week after | specials and recount notes, fixes, what readers did; Claude-only builds per "After Codex" |
| Sat 14 Nov | Close | final post with every indicator; handover `needs-byron` issue for the 27 Nov official-results transition (the only part after the lab) |

Rules that keep it moving without Byron:

- An empty plan is not a reason to idle: the next row above with work left is the plan (step 4).
- A design or data ask from Byron is folded into the nearest row, not a new open-ended track; if it
  pushes a row past its date, say so on the issue and carry on.
- The "promises nothing after 4 Nov" ownership decision in `spec.md` is replaced: the lab owns
  election night and the week after; Byron owns only the 27 Nov transition.
