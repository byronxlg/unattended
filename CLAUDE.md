# unattended

The AI-native SDLC playbook run without a human from 2026-10-15 to at least 2026-11-14 (twenty days at first, extended by Byron on 2026-10-16 to a week past election night): Claude supervises, Codex builds
(to 7 November; Byron will not renew the plan, so Claude alone from then, see "After Codex" in
`prompts/supervisor.md`), every artifact and metric lives in this repo. Blog: https://byronxlg.com/unattended/ (built from
`posts/` by `bin/blog`, deployed by `.github/workflows/pages.yml`).

## Commands

- `bin/tick [--force] [--dry]`: the loop (launchd, every 10 min). `bin/tick --dry` says what it would do.
- `bin/codex-run --id <id> --prompt <file> [--cwd dir] [--sandbox read-only|workspace-write] [--background] [--resume thread]`: the only way Codex runs. Appends to `state/ledger.jsonl`.
- `bin/blog build`: posts/ to site/. `bin/blog check`: frontmatter and links.
- `bin/metrics`: the playbook indicators from git, GitHub and the ledgers, to `site/data/metrics.json`.
- `bin/lint`: banned characters, frontmatter, plan sync, ledger shape. CI runs the same.
- Tests: `uv run --with pytest pytest -q`.

## Layout

`intent/<slug>/{intent,spec,plan}.md` per change (the playbook's artifacts). `prompts/supervisor.md`
is what the tick hands Claude. `state/` holds the ledgers (committed) and run markers (ignored).
`posts/` is the blog source. `product/` will hold the NZ election web app from phase 4. `evals/` are
Codex tasks with checks. `docs/playbook.md` and `docs/metrics.md` are the rules and the indicator
definitions. `runbook/` says how to operate the loop.

`lab_metrics/` computes lab indicators and renders the generated metrics document.

## Conventions

- Codex works in `.worktrees/<change>` on branch `change/<slug>`; product code reaches `main` only by PR.
- Lab bookkeeping (state, posts, intent) is committed straight to `main` by the supervisor.
- No emojis, no em dashes anywhere. Humble language: a thing worked when a command showed it.
- Secrets: none in this repo, ever. The loop needs only `codex login` and `gh auth` on the host;
  the product's upstream keys (X, Jev) are Actions secrets and SSM `/unattended/prd`, never in the tree.

## The floor (Byron only)

Credentials, money, deleting data, git tags and registry publishes (production releases), new
paid services, changes to other repos. Ask in a `needs-byron` issue; keep working on the rest.

## Known agent mistakes

- Supervisor: a fix brief that dictates a data shape without reading the validator or consumers of
  that shape introduced a defect twice (PR #2, PR #5). Name the invariant and where it is enforced;
  let the engineer choose the shape, then check the diff against the validator.
- Supervisor: a build brief that forbids editing existing tests while adding a route or a data
  family blocked the job (social POC, 2026-10-17). Say which contracts move with the registered
  set; the no-edit rule is for fix jobs.
- Supervisor: a fix brief asked for a wording change that an existing assertion pinned verbatim while
  forbidding assertion edits (social POC fix-2, 2026-10-17). Grep the tests for what a fix item
  changes; a pinned nit goes to the next build round.
- Supervisor: "no edits to pre-existing tests" in a fix brief read as "tests written before this
  follow-up", so the engineer stopped on an assertion its own branch had added (social-fix fix-2,
  2026-10-17). Name the protected set by ref: tests on main at the base sha; the branch's own tests
  move with it.
- Supervisor: design feedback turned into measures (byte budgets, link counts, heading counts) and tests that pinned
  markup; five look rounds passed their checks and Byron still judged the site "very basic" (#32 to #51, 2026-10-20).
  Judge UI by eye from screenshots beside the reference (REVIEW.md pass 4); tests check data, provenance, absence and
  accessibility, never markup or bytes.
