Goal: make product/nz_election/tests/coalitions_browser.py pass again on main without weakening it.

Failure (host, main 8a8d484): check_unassigned_after_unavailable_allocation (coalitions_browser.py:131) times out at
`root.locator('fieldset').wait_for(state='visible')`: the #coalition-explorer fieldset stays `disabled hidden` for the
synthetic unassigned inputs from coalition_unassigned_cases.unassigned_inputs. It has failed since about 18 Oct (first
noted on PR #31, before the derived-Others change PR #35). Decide from the code which side is wrong: the explorer's
client script now refusing these inputs (for example an input-hash or manifest check, derived Others, or a moved data
URL), or the synthetic fixture no longer matching the envelope shape build.explorer and the client expect. Read first:
coalitions_browser.py, coalition_unassigned_cases.py, build.py explorer(), the explorer's client JS, export.canonical/digest.

Constraints: if the product is wrong, fix the product and keep every assertion; if the fixture drifted, update the
fixture to the current envelope contract and keep every assertion (the 71/70 unassigned counts, the strip counts,
'Seats are unavailable'). Do not delete, skip or loosen a check. No page layout or style change. Commit in this
worktree, do not push. Write last.md: cause, the fix, and the commands below with their output.

Done when (Chromium may be denied in your sandbox; say so and the supervisor runs them on the host):
- uv run product/nz_election/pipeline/build.py ... a live or fixture build, then
  uv run --with playwright python product/nz_election/tests/coalitions_browser.py --site <parent of nz-election> -> PASS coalition browser
- uv run --with pytest pytest -q product -> no new failures beyond Chromium launch denials
- bin/lint -> lint ok
