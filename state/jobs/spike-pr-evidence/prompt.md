# Spike: pr-evidence join prototype

You are the engineer in the unattended lab (read AGENTS.md). This is a one-job throwaway spike in
phase 1 research: the branch you are on is never merged, so optimise for evidence, not polish.
Keep the whole job under 25 minutes of work.

Read first: intent/candidates/pr-evidence.md (the candidate; especially "Join contract and
squash survival", "Spike" and the fixture acceptance matrix), docs/metrics.md, bin/codex-run.

## Goal

Answer with evidence: can a small receipt (branch, HEAD before and after, working tree status
before and after) plus a PR commit snapshot give an exact session-to-commit join that survives
a squash merge, with zero false exact links on the negative fixtures?

## Do

1. Before anything else, capture your own receipt into spike/receipt-self.json with the
   literal outputs of: `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`,
   `git status --porcelain=v1`, `git rev-parse --show-toplevel`, plus a UTC timestamp. Repeat
   the capture at the end into the same file under an "after" key, after your last commit.
   This is the lab's first real build receipt; the supervisor needs it as is.
2. Write spike/pr_evidence_spike.py (stdlib only, Python 3.12): a `join(receipt, pr_snapshot)`
   function returning one of exact, suggested, ambiguous, unknown, with a list of reasons, and a
   `classify_review_rounds(reviews)` function implementing the draft's definition (one round per
   distinct reviewed head SHA). Keep it under 200 lines.
3. Write spike/fixtures/*.json, one per row of the draft's matrix (isolated-squash, resume-noop,
   reuse-fork, shared-dirty-rewrite, agent-comments, unknown-human, ci-pagination), with
   symbolic SHAs. Write spike/test_spike.py so each fixture asserts its required verdict.
4. Create a real squash scenario in a temporary git repo under /tmp (not this worktree): branch
   with three commits, squash merged into main, then show that the receipt plus a saved commit
   list still joins exactly while walking main alone does not. Put the commands and output in
   your final message.
5. Try one live GitHub read: `gh api graphql` with the query from the draft against
   byronxlg/unattended (it may have zero PRs; that is fine). Report whether the network was
   reachable from this sandbox and paste the first 10 lines of output or the error.

## Constraints

No dependencies. Do not edit bin/, state/, docs/ or anything outside spike/. Commit on this
branch with clear messages. No emojis, no em dashes.

## Definition of done

`uv run --with pytest pytest -q spike/` exits 0 with 7 or more tests passed. Final message under
60 lines: the answer to the goal question (yes or no, with the evidence), the squash scenario
output, the GitHub probe result, and anything that surprised you.
