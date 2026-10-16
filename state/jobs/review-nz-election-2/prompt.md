Fresh-context review of branch change/nz-election-2 against main (merge-base 5a93836), for
https://github.com/byronxlg/unattended/pull/10 (NZ election increment 2), HEAD 0e82e89. Worktree .worktrees/nz-election-2, read-only.
Follow REVIEW.md (bugs; security; compliance with intent/nz-election/spec.md sections "Site and
directory layout", "Design", "Provenance and downloads", "Accessibility and quality", "Testing
and acceptance", and intent/nz-election/plan.md "Averaging", "Published data contracts", "Hourly
refresh and publication", "Web build and design", "Build order: Increment 2", supervisor
decisions 3, 4, 7). Important or Nit, at most five nits, nothing bin/lint reports. Do not approve.

Scope: `git diff 5a93836..0e82e89` (27 files, product/ plus one pages.yml step). The engineer
could not launch Chromium in its sandbox; the supervisor ran screenshots.py on the host. The
20 PNGs and manifest.json are in artifacts/nz-election/screenshots/ in the worktree: open and
judge them against the spec Design section and the plan palette and type scale (hero strip,
120-seat base versus overhang, majority mark, 40 px seat counts, Arial, no cards, no shadows,
voter copy, 390 px with no page-wide overflow). Built HTML is in site/nz-election/ and the
no-data build in /tmp/nz-nodata/ (built from a nonexistent --data path, what pages.yml deploys).

Check the pattern, not the instance: exact arithmetic (no float in any published number or
comparison; Decimal rounding display-only); the window and equal-weight rule against the
fixture bytes; coherent=false with shares=null and seats withheld whenever any party in the
window is missing from any poll; JSON and CSV siblings carry identical rows and provenance;
the manifest hashes match the files; atomic publish (temp dir then rename, last-good retained
on any failure, older run cannot replace newer, concurrent publishers against tmp_path repos);
build.py never writes outside --out and never removes blog output; the six routes come from
config/routes.json; HTML escaping of every value that reaches a template (party names, poll
ids, URLs); no JS module loaded; pages.yml step runs with no data and cannot fail the deploy
for a data reason; new tests assert behaviour, not snapshots, and no existing test weakened.
The supervisor already noted as nits: inline links with min-height 44 px breaking prose line
boxes, focus outline on main in every baseline image, empty Immutable download column offline,
repeated source note. Do not repeat those; find what else is there.

Running checks: uv's cache may not be writable in this sandbox; review by reading plus
python3 and node reproductions. The supervisor's host run stands: 199 passed, verify all PASS,
12 baseline images, bin/lint ok.

Output: findings with severity, file:line, what is wrong, reproduction, one-line fix. End with
one line: the count of Important findings.
