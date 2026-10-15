Committed `e2f9e54`; not pushed. Working tree clean.
Added package, lockfile, fixtures, tests and documentation under `product/fleet_audit/`; updated `.github/workflows/ci.yml`.

```text
$ uv run python -m fleet_audit.acceptance registry --offline
OK registry
$ uv run --with pytest pytest -q
........................................................................ [ 37%]
........................................................................ [ 75%]
...............................................                          [100%]
191 passed in 0.96s
$ bin/lint
lint ok (101 text files)
$ uv run fleet-audit declared .venv/fleet-demo/registry-valid
example/tick gui/501/com.unattended.tick declared: joined plist /Users/byron/repos/unattended/.worktrees/fleet-audit-1/product/fleet_audit/.venv/fleet-demo/com.unattended.tick.plist; live state not observed
summary: 1 declared, 0 invalid-input errors
$ uv run fleet-audit declared .venv/fleet-demo/registry-schema-errors
.venv/fleet-demo/registry-schema-errors/fleet.md:uid: unknown field
.venv/fleet-demo/registry-schema-errors/fleet.md:jobs[0].scheduler: only launchd is supported
$ uv run fleet-audit --help
usage: fleet-audit [-h] {declared} ...

Validate declarations and join disk plists; no live observation.

positional arguments:
  {declared}
    declared  validate runbooks and their plist labels

options:
  -h, --help  show this help message and exit
$ du -sh product/fleet_audit/.venv
1.1M	product/fleet_audit/.venv
```

Exits: schema-errors 3; all other verification commands 0.
Plan limits: eight tests are named, so added a ninth for Value truth-testing. Source omits tick environment keys; documented and tested synthetically. Cache measured 2.0G before/after; precise delta unavailable.