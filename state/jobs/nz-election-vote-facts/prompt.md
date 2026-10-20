# Vote page data: EC key dates and official links as a sourced snapshot (no page)

Data half of the vote page (`intent/nz-election/pages/vote.md`, draft until 14:30Z 20 Oct). The page itself is the next job, built from the accepted plan; this job adds no route and no rendering code.

Read first: `AGENTS.md`, `intent/nz-election/pages/vote.md` (questions 1 to 5, Answers, Data), `product/nz_election/snapshots/` and its loader and tests (follow the same record shape: source URL, retrieved_at, licence or terms note, per-record provenance), `intent/nz-election/design-principles.md` principle on provenance.

Goal: `product/nz_election/snapshots/voting.json`, fetched by you from the live Electoral Commission pages (vote.nz, elections.nz), holding:
- key dates for the 2026 general election in NZ time with the source URL of each: enrolment deadline for the advance period, overseas voting opens, advance voting opens and closes, election day, the s197 cutoff if the EC states one;
- the official link for each action in the plan: check or update enrolment, find where to vote, what to bring and the two votes, overseas voting, accessible formats, assisted or takeaway voting, with each one's deadline where the EC gives one;
- the EC copyright or reuse terms as stated, and an independent one-line summary per item in our words (no copied paragraphs).
A loader function next to the existing snapshot loaders that validates the file (dates parse, all in order, every record has a source URL on an EC domain and retrieved_at) and fails loudly otherwise. Anything the EC does not publish is omitted from the file and listed in your last.md, never filled with a placeholder.

Constraints: no change to routes, page rendering, client code or the site harness; tests on main at the base sha are untouched except contracts that enumerate the snapshot set, which move with it. No secrets. Web access is for the EC pages only.

Done when:
- `uv run --with pytest pytest -q product` passes, with new tests for the loader (valid file loads; a reordered date, a missing source and a non-EC source each fail with a named error).
- `bin/lint` prints ok.
- last.md lists every date and link with its source URL, what was omitted and why, and `git diff --stat main` shows only snapshots, the loader and tests.
Commit in the worktree; do not push.
