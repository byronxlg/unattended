---
project: unattended
reviewed: 2026-10-15
deploy_path: push-to-main
rollback_minutes: 10
---

# Updates

How change reaches the lab and the blog.

- Lab tooling (`bin/`, `prompts/`, `docs/`, `posts/`, `state/`): commit to `main`; `bin/lint` first; the Pages workflow republishes the blog on every push to `main`; CI runs lint and tests.
- Product code (`product/`): only by PR from a `change/<slug>` branch built in `.worktrees/<slug>`; CI green, supervisor review, fresh review (a read-only `bin/codex-run --kind review` until the Codex cut on 7 Nov, then an `Agent` run that reads only the PR diff and `REVIEW.md`, logged in the PR), squash merge.
- The tick: `bin/tick` is read from a private copy at start, so replacing the file while a tick runs is safe. Changing the interval means editing `infra/host/com.unattended.tick.plist`, copying it to `~/Library/LaunchAgents/`, and `launchctl bootout` then `bootstrap`.
- Smoke test after any tooling change: `bin/tick --dry` (prints the reasons it would run for; it suppresses only the supervisor: the workflow watchdogs still dispatch and tick state is still appended) and `bin/codex-run --id smoke-<n> --prompt <file with 'Reply with exactly: ok'> --sandbox read-only --kind research --timeout 300` (until the Codex cut on 7 Nov; after it, `bin/tick --dry` alone).
- Rollback: `git revert` on `main`; the next push republishes the previous code with current data. During the publication freeze pages.yml does not deploy; for a paired rollback dispatch pages.yml with reviewed code and data SHA inputs.
