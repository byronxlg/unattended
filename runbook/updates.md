# Updates

How change reaches the lab and the blog.

- Lab tooling (`bin/`, `prompts/`, `docs/`, `posts/`, `state/`): commit to `main`; `bin/lint` first; the Pages workflow republishes the blog on every push to `main`; CI runs lint and tests.
- Product code (`product/`): only by PR from a `change/<slug>` branch built in `.worktrees/<slug>`; CI green, supervisor review, fresh Codex review, squash merge.
- The tick: `bin/tick` is read from a private copy at start, so replacing the file while a tick runs is safe. Changing the interval means editing `infra/host/com.unattended.tick.plist`, copying it to `~/Library/LaunchAgents/`, and `launchctl bootout` then `bootstrap`.
- Smoke test after any tooling change: `bin/tick --dry` (prints the reasons it would run for) and `bin/codex-run --id smoke-<n> --prompt <file with 'Reply with exactly: ok'> --sandbox read-only --kind research --timeout 300`.
- Rollback: `git revert` on `main`; the next push republishes the previous site.
