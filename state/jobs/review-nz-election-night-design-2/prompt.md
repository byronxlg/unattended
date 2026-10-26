Second fresh-context review of PR #94 (nz-election-night-design), read-only. Worktree .worktrees/nz-election-night-design,
branch change/nz-election-night-design, head a12a058. Diff: git diff origin/main...a12a058 (fix rounds: 218d9aa, 12d16c0, a12a058).
Judge against REVIEW.md. Brief: state/jobs/nz-election-night-design/prompt.md; page plan intent/nz-election/pages/night.md;
design product/nz_election/DESIGN.md.

The first review requested changes: eight majority cards pushed electorate search past two phone screens. Check that this is
resolved in every result state (before results, live, settled, official) at 390, that the hemicycle wedges, marker underlay and
timezone wording from fix-1 are correct, that the screenshot harness change in 12d16c0 (header checks scoped to the site banner)
does not weaken any check, and that nothing on data, provenance, absence or accessibility was loosened. Tests check data, not
markup; flag any new test that pins markup, class names or bytes.
Supervisor host run with Chromium: test_result_states, test_night*, test_design, test_home*, test_waterfall* 452 passed, 0 failed.
Do not run pytest; read and probe.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
