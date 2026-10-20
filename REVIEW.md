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

4. Design (any change touching `product/*/web`): first the question test from the page plan
   (`intent/<slug>/pages/<page>.md`): from the 390x844 screenshot alone, write down the answer to
   each of the top three questions as read off the page; a question not answerable in five
   seconds, or anything above the fold that answers no ranked question, is Important. A UI change
   with no accepted page plan is Important. Then judged on the phone and desktop screenshots
   against `intent/<slug>/design.md`: hierarchy (the five-second test on
   the home page), legibility at 360 px, contrast and colour never the only encoding, macrons
   rendering, touch targets, loading, empty, stale and error states present, provenance chip on
   every number, no generic-template look. Two review-iterate rounds minimum per view before a
   milestone closes; rounds and Important findings go in `state/changes.yaml` `design_rounds`.

Severity: Important is anything that would be wrong in production or violates the spec; Nit is
style. At most five nits per review; CI already enforces lint, so do not report what `bin/lint`
reports. Generated paths (`site/`, `state/jobs/*/events.jsonl`) are out of scope.

Findings do not merge or block by themselves: the supervisor decides, and records the decision in
the PR. The agent that wrote the code never approves it.
