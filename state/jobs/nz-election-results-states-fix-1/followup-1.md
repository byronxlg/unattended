# PR #79 fix-1, follow-up 1: revised invariant for item 1

Your stop was right: the tree holds no payload field that tells an official count from a complete
preliminary one, and my brief should not have assumed one. The invariant is revised to source
provenance, which the tree can enforce:

1. Official means fetched from the official-results source, not relabelled. A package is official
   only when its recorded source is a declared official-results URL that is distinct from the
   preliminary feed (the media.election.net.nz preliminary address is never official), and its
   retrieved_at is on or after the official-results date the page already states (27 November
   2026, as one named constant, reused by the copy). Record the source kind and URL in the package
   from the fetch, not from the operator label; the "Official results" label is derived from it.
   Check it where NIGHT_STATE is raised now. You choose the shape; read the validator and every
   consumer first. The official URL is configuration with a comment saying it is an inference to
   confirm against the EC once published (the research job could not confirm it), and the runbook
   says so in one line.
   Regression test: the manifest-checked preliminary fixture, relabelled official and retimestamped
   after 27 November, must raise; the same payload recorded as fetched from the official source
   after the date must pass. Show the first failing on 739f880 and passing on HEAD.
2. and 3. as in the original fix-1 brief (handover copy changes with the snapshot, tested in the
   real DOM; question three answered with a reported-leader fixture within one scroll at 390).

Tests: tests on main at c2ce1fc are protected; the branch's own tests from 739f880 move with the
shape, nothing weaker. Commit in the worktree, do not push, do not commit last.md.

Done when, from the worktree: `uv run --with pytest pytest -q product/nz_election/tests` passes
(browser tests use host Chromium if present; say which ran and which could not launch),
`bin/lint` prints ok, and last.md lists the commits, the shape chosen, and the test outputs.
