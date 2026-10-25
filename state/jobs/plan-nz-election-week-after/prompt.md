# Plan: what election night and the week after still need (read-only)

Goal: a gap list, so every build the night and 8 to 14 Nov need is dispatched before Codex stops
(last build dispatch 5 Nov; Codex ends 2026-11-07 03:14Z; after that Claude alone keeps the site).

Read first: intent/nz-election/schedule.md, intent/nz-election/plan-m3.md, intent/nz-election/pages/night.md,
product/nz_election/runbook.md and runbook/, docs/codex-notes.md, product/nz_election/pipeline/ (night*.py,
verify.py), .github/workflows/nz-election-*.yml.

Answer, each with file:line evidence from main:
1. Election night 7 Nov: what is built and proven (verify checks, tests, the #76 deployed probe and
   fault harness), and what is missing or untested (s197 freeze across every workflow, night-live
   start and stop, fallback when the EC feed is unreachable, the home and night pages switching to results).
2. The week after (8 to 14 Nov): preliminary-to-official transition (EC official results 27 Nov is after
   the lab: what the site should say until then), special votes notes, the social daily after the freeze,
   which scheduled workflows should stop or change, and the copy that goes stale on 8 Nov.
3. A ranked list of increments (at most five), each: goal, files, proving test or verify command, size
   (small/medium), and whether it must be Codex (before 5 Nov) or can be Claude-only after the cut.

Constraints: read-only; no web needed beyond checking an EC URL if a gap depends on it. Output in last.md,
under 150 lines.
