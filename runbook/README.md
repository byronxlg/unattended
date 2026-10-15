# Runbook: unattended

What: a twenty-day experiment, 2026-10-15 to 2026-11-04. Runs on Byron's Mac mini as the
LaunchAgent `com.unattended.tick` (`infra/host/`), every 600 s, calling `bin/tick`. Healthy:
`state/ticks.jsonl` gets a line every 10 min; `~/Library/Logs/unattended-tick.log` has no
tracebacks; a post appears in `posts/` every NZ day; https://byronxlg.com/unattended/ shows it.

Who watches it: the management operator (fleet registry entry `unattended`, Tier 3). No off-host
monitor; the blog going stale is the signal.

Scheduled: the tick (launchd, 600 s); Pages publish on every push to `main` (Actions); CI on PRs.

## It stopped

- `launchctl print gui/$(id -u)/com.unattended.tick` shows the job; if absent, install per the
  comment in the plist. `tail -50 ~/Library/Logs/unattended-tick.log` says why a run died.
- A Claude usage limit leaves `state/model.limited`; the tick backs off 60 min on its own.
- A Codex job stuck: `ls state/jobs/*/running`; the pid inside is the wrapper; `kill` it and the
  wrapper records the kill in the ledger on its next pass (or remove the `running` file by hand).
- To stop everything: `launchctl bootout gui/$(id -u)/com.unattended.tick`.

## Updates

Edit on `main` for lab tooling (bash, prompts, posts); product code by PR from `change/*`
branches. `bin/lint` before every commit. The tick runs from a private copy of itself, so pulling
a new `bin/tick` is safe mid-run.
