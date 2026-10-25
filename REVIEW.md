# REVIEW.md

How changes in this repo are reviewed, by the supervisor (Claude, approves) and by a fresh-context
Codex review (second opinion, cannot approve). Three passes, in this order:

1. Bugs and logic errors: wrong behaviour, unhandled failure paths, off-by-ones, race conditions
   in the tick and the job wrapper, shell quoting, Python exceptions swallowed.
2. Security: secrets in diffs or logs, writes outside the worktree, network calls the spec did
   not ask for, commands that could delete data, anything that weakens the sandbox.
3. Compliance: does the diff do what `intent/<slug>/spec.md` and `plan.md` say, and nothing
   else; did `plan.md` get updated in the same change when the implementation departed from it;
   tests present and meaningful; `AGENTS.md`/`CLAUDE.md` conventions; no emojis or em dashes.

4. Design (any change touching `product/*/web` or page markup): judged by eye from screenshots,
   not from measures. Take 1280x900 and 390x844 full-page screenshots of every changed page (light
   mode, plus one dark-mode check) and look at them beside the previous version and the reference
   (538 2024 forecast, NBC midterms hub) at the same width. Important: the page looks worse than
   before or plainly weaker than the reference; text overlapping marks or other text; a graphic
   whose labels are below 12 px on the phone; horizontal page scroll; "not available" or similar
   text on a public page; a number with no source line; hard-coded colours instead of the tokens
   in `product/nz_election/DESIGN.md`; a new graphic built outside `home_graphics.py` patterns
   without reason. Then the page plan (`intent/<slug>/pages/<page>.md`, when one exists): can the
   top questions be answered from the phone screenshot in five seconds. Write the three weakest
   things on each page in the review, fixed or filed in `state/design-backlog.md`.

Severity: Important is anything that would be wrong in production or violates the spec; Nit is
style. At most five nits per review; CI already enforces lint, so do not report what `bin/lint`
reports. Generated paths (`site/`, `state/jobs/*/events.jsonl`) are out of scope.

Findings do not merge or block by themselves: the supervisor decides, and records the decision in
the PR. The agent that wrote the code never approves it.
