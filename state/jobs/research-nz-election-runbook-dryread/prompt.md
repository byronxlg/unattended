# Research: dry-read the election-night runbooks against the tree (read-only)

Goal: from 7 Nov 16:14 NZDT Claude operates the site alone from the runbooks. Find every step that
would fail or mislead before that happens.

Read: `product/nz_election/runbook/night.md`, `product/nz_election/runbook.md`,
`product/nz_election/runbook/advance.md`, `runbook/nz-election.md`, `runbook/updates.md`,
`intent/nz-election/plan-week-after.md`, `.github/workflows/nz-election-*.yml`.

For each command or file path the runbooks name: does the script, flag, workflow input, path or
constant exist on this tree with that spelling and meaning? Check flags against argparse and
workflow `inputs:`. Where you can run a command read-only without network (e.g. `--help`, a
verify on a fixture dir), do; say which you ran and their exact output line.

Output (`last.md`): a table of findings, each with runbook file:line, what it says, what the tree
has (file:line), severity (blocks election night / misleads / cosmetic), and the one-line
correction. Then the steps you could not check and why. No edits; no recommendations beyond the
corrections.
