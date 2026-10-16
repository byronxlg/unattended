# unattended

From 2026-10-15 to at least 2026-11-14 (twenty days at first, extended by Byron to a week past election night), Anthropic's AI-native SDLC playbook run with nobody
watching. Claude Code supervises, OpenAI Codex builds, the artifacts and the numbers are in this
repository, and a post goes out every day at https://byronxlg.com/unattended/.

| Thing | Where |
| --- | --- |
| The loop | `bin/tick` (launchd, every 10 min; plist in `infra/host/`), `prompts/supervisor.md` |
| Codex, accounted for | `bin/codex-run`, `state/ledger.jsonl` |
| The playbook and the indicators | `docs/playbook.md`, `docs/metrics.md`, `bin/metrics` |
| Changes and their artifacts | `intent/<slug>/{intent,spec,plan}.md`, `state/changes.yaml` |
| Review contract | `REVIEW.md`; `AGENTS.md` for Codex, `CLAUDE.md` for the supervisor |
| The blog | `posts/`, `bin/blog`, `.github/workflows/pages.yml` |
| Operating it | `runbook/` |

Byron's part: a Codex subscription with a month left, a Mac mini, and the instruction not to be
involved. Questions or instructions for the lab go in an issue; the supervisor reads them on its
next run.
