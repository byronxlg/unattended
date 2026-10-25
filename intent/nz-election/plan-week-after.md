---
status: accepted 2026-10-25T00:30Z
source: plan-nz-election-week-after (read-only Codex plan job, main bf9f86a)
---

# Plan: election night and the week after

Supervisor decisions (2026-10-25 00:30Z):

- Increment 1 is PR #78 plus a bounded stop; the stop half is dispatched after #78 merges, on its branch base.
- Increment 2 (result states) dispatched now, stacked on change/nz-election-night-start (night_live.py overlaps).
- Open decisions (preliminary loop stop time, post-election social scope, daily collection sunset) go to Byron as one NOTE line; proposed defaults: stop the five-minute loop at 8 Nov 06:00Z (already the night_start upper bound), social continues to 14 Nov with its sample period labelled, hourly polls stop 7 Nov 06:00Z, daily collection stops 14 Nov.
- Increment 3 dispatches after those close; 4 and 5 are supervisor work on 6 and 7 Nov and from the cut.

Reviewed `main` at `bf9f86a22fa4d590c1de0de2f5bfd8a2a43bff16`; inspected paths have no diff from main. Existing proof below is recorded evidence, not a fresh full-suite run.

**7 November readiness**

- **Built:** serial Actions acquisition, coherent references plus all 71 details, atomic publication, deployment recovery, five-minute cycles, browser polling and last-good retention. Evidence: `product/nz_election/pipeline/night_live.py:64`, `:129`, `:179`; `product/nz_election/web/night-live.mjs:18`.
- **Offline proof:** `verify.py night` exercises acquisition and package validation; `waterfall` checks leaders, golden seats and incomplete-input suppression. Recorded main runs passed both. However, `all` can skip absent night/waterfall families. Evidence: `product/nz_election/pipeline/verify.py:369`, `:389`, `:478`; `docs/journal.md:2392`.
- **#76 deployed proof:** initial probe, 60x replay and faults passed; subsequent fixes hardened provenance, CORS diagnosis and host-clock phase checks. Final suite: 96 tests passed, CI green, merged as `5864574`. Repeat all three modes on the final release: the earlier deployed PASS records precede those fixes. Evidence: `docs/journal.md:2431`, `:2487`, `:2510`, `:2521`.
- **Proof limits:** before-close probe correctly permits zero live-package requests; it cannot prove the real post-close publication chain. Faults intercept packaged JSON and simulate time, proving browser retention/staleness, not upstream acquisition. Demo Actions rehearsal passed but deliberately neither publishes nor chains. Evidence: `product/nz_election/runbook/night.md:218`, `:282`, `:303`; `docs/journal.md:2251`.
- **Freeze largely implemented:** 6 Nov 23:30 NZDT through 7 Nov 19:00; collection entry guards, publication recheck, queued-push test and rollback-independent Pages guard exist. Remaining acceptance is current-release end-to-end boundary evidence and the scheduled-workflow history gate, not a missing freeze implementation. Evidence: `product/nz_election/tests/test_night_operation.py:139`, `:173`; `.github/workflows/pages.yml:49`, `:170`; `product/nz_election/pipeline/publish.py:197`.
- **Startup missing on main:** manual dispatch only. PR #78 already addresses cron/watchdog startup, but review found timeout, duplicate-dispatch and boundary races; finish it rather than duplicate it. **Stop missing:** main chains indefinitely; only manual disable/cancel is documented. A starter cutoff alone does not stop an existing loop. Evidence: `.github/workflows/nz-election-night-live.yml:3`; `product/nz_election/pipeline/night_live.py:231`; `product/nz_election/runbook/night.md:234`; `docs/journal.md:2539`, `:2546`.
- **Feed failure handled, operationally unproven:** failed complete cycles preserve previous data; browser failures retain displayed content and official link, stale after 15 minutes. Need production-like publication/recovery rehearsal, including failure before the first live snapshot. Evidence: `product/nz_election/pipeline/night_live.py:195`; `product/nz_election/web/night-live.mjs:11`; `product/nz_election/runbook/night.md:189`.
- **Page switching partly proven:** home switches at build time only with eligible 2026 data; absent data retains the poll hero. Night removes pre-close actions client-side and loads live packages; no-JS requires a post-close deployment. Test overnight-open home, no data, captured zero state and first real live cycle. Evidence: `product/nz_election/pipeline/home.py:165`, `:382`; `product/nz_election/tests/test_home_plan.py:19`; `product/nz_election/web/night-live.mjs:47`.

**8 to 14 November**

- Keep **“Preliminary; official results due 27 November”**, dated last complete capture, provisional leaders and separate government-formation caveat. Add an explicit “live updates ended” state so intentionally retained results do not look like a broken feed. Current client accepts only `Live preliminary results` and continues polling indefinitely. Evidence: `product/nz_election/pipeline/night_page.py:131`; `product/nz_election/web/night-live.mjs:33`, `:76`.
- Official comparison logic exists, but no production compatible preliminary/official pair or complete official ingestion/display transition is established. Preserve a pinned preliminary baseline; prebuild and test the official import route before cutoff, leaving actual 27 Nov capture/publication to Byron. Evidence: `product/nz_election/pipeline/night_seats.py:16`; `product/nz_election/runbook/night.md:135`, `:244`; `intent/nz-election/schedule.md:29`.
- Specials/recount notes should be dated, sourced explanations of possible changes. Do not label final-minus-preliminary as special votes; show a specials component only with explicit evidence. Production comparison is currently absent. Evidence: `product/nz_election/runbook/night.md:135`; `product/nz_election/pipeline/night_seats.py:33`.
- Social automatically resumes after the freeze; the 8 Nov 02:40 NZDT run samples 7 Nov by default. Decide explicitly whether election-day/post-election discussion remains within the pilot, label its sample period, and set a shutdown by lab close. Existing cap and 36-hour hiding remain useful. Evidence: `.github/workflows/nz-election-social-daily.yml:5`, `:9`; `product/nz_election/runbook.md:174`, `:186`, `:216`.
- Recommended schedule: stop high-frequency night acquisition after the accepted preliminary capture; stop hourly poll acquisition after polling closes; retain a controlled daily post-election build for notes/social through 14 Nov. Restrict daily candidates/markets/advance work to supported updates, then stop scheduled collection at handover. Preserve manual Pages deployment for 27 Nov. These are proposed policies: current crons have no sunset. Evidence: `.github/workflows/nz-election-hourly.yml:5`; `.github/workflows/nz-election-daily.yml:4`, `:43`; `product/nz_election/pipeline/daily_sources.py:77`.
- Disabling hourly also removes social’s documented rebuild mechanism; retain daily publication or explicitly trigger Pages after social. Evidence: `product/nz_election/runbook.md:217`; `.github/workflows/pages.yml:21`.
- Stale copy: home/share title “New Zealand votes on 7 November”; “Who is standing”; night metadata describing replay rather than current results; voting-place/help actions still inviting voting. Vote countdown itself already says election day passed. Evidence: `product/nz_election/pipeline/route_cards.py:30`, `:36`, `:44`; `product/nz_election/pipeline/home.py:381`; `product/nz_election/pipeline/vote_page.py:38`, `:42`, `:51`.

**Ranked increments, maximum five**

1. **Finish autonomous start and bounded stop. Medium; must dispatch by 5 Nov to Codex.** Finish #78; add explicit operational stop policy, successor cutoff and recovery ownership. Files: night workflow, `pipeline/night_start.py`, `pipeline/night_live.py`, `bin/tick`, night runbook. Proof: startup/watchdog race tests, active-loop cutoff tests, `pytest -q product/nz_election/tests/test_night_operation.py`, controlled Actions rehearsal.
2. **Preliminary, settled and official result states. Medium; must dispatch by 5 Nov to Codex.** Pin preliminary baseline, implement official capture/package path, settled-state freshness and home/night handover, preserve evidence-only specials. Files: `pipeline/night*.py`, `web/night-live.mjs`, `pipeline/home.py`, feed configuration, night runbook. Proof: `verify.py night`, `verify.py waterfall`, dated preliminary/official fixtures, absent-feed tests, screenshots at both required sizes.
3. **Post-election schedules and copy. Medium; must dispatch by 5 Nov to Codex.** Implement agreed shutdown dates, social continuation and rebuild trigger; update home/vote/share copy by phase. Files: election workflows, daily loaders, `home.py`, `vote_page.py`, `route_cards.py`, runbooks. Proof: injected-clock tests for 7/8/14/27 Nov, no paid calls after sunset, social deployment test, `verify.py all --data <bundle> --site <site>`, phone/desktop screenshots.
4. **Final release acceptance and recovery drill. Small; prepare before cutoff, Claude-only execution on 6/7 Nov.** Files: night runbook, acceptance records, targeted operation tests if gaps emerge. Proof: `uv run product/nz_election/tools/harden.py --history`; deployed harness `--probe`, `--rehearse --speed 60`, `--faults`; real Actions rehearsal and post-close code/data SHA confirmation. Include queued freeze, first-feed failure, recovery and successor/stop evidence.
5. **Week-after editorial operation and handover. Small; Claude-only after cut.** Files: night runbook, schedule, `docs/codex-notes.md`, sourced notes/snapshots. Record daily specials/recount updates, final preliminary SHA, workflow states, rollback command and exact official import procedure; create the scheduled 14 Nov handover issue. Proof: explicit night/waterfall validation of retained bundle and link/copy review. Codex notes currently contain CLI research, not the required worktree handover (`docs/codex-notes.md:1`; `intent/nz-election/schedule.md:25`).

Fresh read-only verification: `python3 -B -c` invoked `require_publication_allowed` and `night_live.require_open` at six boundaries; exit 0:
```text
2026-11-06T10:29:59Z publication=allowed night=NIGHT_NOT_OPEN
2026-11-06T10:30:00Z publication=PUBLICATION_FROZEN night=PUBLICATION_FROZEN
2026-11-07T05:59:59Z publication=PUBLICATION_FROZEN night=PUBLICATION_FROZEN
2026-11-07T06:00:00Z publication=allowed night=allowed
2026-11-08T06:00:00Z publication=allowed night=allowed
2026-11-27T00:00:00Z publication=allowed night=allowed
```
Open decisions: exact preliminary-loop stop time, post-election social scope, and daily collection sunset. Resolve in increments 1 and 3 before dispatch closes.

Increment 2 fix-1: official status derives from acquisition source kind and exact declared URL,
with retrieval on or after the shared 27 November 2026 date. The official URL is inferred
pending EC confirmation, not a confirmed endpoint. A preliminary source never becomes official
through relabelling. The live DOM handover removes obsolete preliminary due-date copy.
Electorate search precedes the map and hides it while filtering so the named leader fits
within one mobile scroll; clearing the search restores the map above the table.
