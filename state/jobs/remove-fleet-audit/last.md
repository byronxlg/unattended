Committed `d23db78` on `change/remove-fleet-audit`; not pushed.
Removed product and declaration, updated CI/docs, relabeled metrics fixtures without weakening checks. Protected history unchanged.

- `uv run --with pytest pytest -q`: `84 passed in 0.56s`
- `bin/lint`: `lint ok (144 text files)`
- `rg -n "fleet_audit|fleet-audit|runbook/fleet|Fleet Audit" --glob '!intent/**' --glob '!posts/**' --glob '!state/**' --glob '!docs/**' .`: no output (exit 1).
- `git status --short`: empty.
- `du -sh product`: `du: product: No such file or directory`

Search differs from expected only because Known agent mistakes already contained no matching terms; section preserved. No outstanding work.