Fresh-context review of PR #68 (nz-election-home-bytes), read-only. Worktree .worktrees/nz-election-home-bytes, branch
change/nz-election-home-bytes, head 637a173. Whole change: git diff origin/main...637a173. Judge against REVIEW.md
(question test first) and intent/nz-election/pages/home.md (accepted page plan). Context: the live home was 68,868 bytes,
over the budget verify.py all enforces, and Pages failed; this change reduces markup to 59,724 bytes.

Check: (1) no byte, transfer or font budget raised or loosened anywhere (verify.py, measure_home, tests, screenshots.py),
(2) every answer on home still renders in the plan's question order with the same values (seat bar, hex/margins, polls,
markets); the markup reduction drops no text, label, aria attribute, provenance chip or link target a reader or the
harness relies on, (3) the eval evals/pages-home-bytes-live fails on the base and is not weakened, (4) the new byte
regression tests measure a populated build, not an empty one, (5) shared renderers changed here do not alter other routes
in a way their checks would miss.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
