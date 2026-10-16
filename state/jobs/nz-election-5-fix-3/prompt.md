# Follow-up 3: nz-election increment 5, second fresh review findings

Same worktree `.worktrees/nz-election-5`, HEAD ba8914b, on PR #13 (CI green on ba8914b). A
second fresh-context review of the fix diff found two items; the supervisor confirmed both as
Important. Each names the invariant and where it is enforced today. Choose the shape yourself,
then check your diff against every consumer of the shape you touch. Read first: `AGENTS.md`,
`intent/nz-election/plan-m2.md` lines 36 to 42 and 160 to 175, `pipeline/export.py`
`validate_bundle` (lines 255 to 320), `pipeline/daily_refresh.py` where geography input hashes
are recorded, `pipeline/geography.py` `validate`, `tests/svg_budget.py`,
`tests/test_geography.py`, `tests/test_geojson.py`.

## 1. Important: a retained geography bundle is bound to its own recorded inputs

Invariant (plan-m2 line 40, spec requirement 15): a bundle on the data branch verifies against
the inputs it records, with no reference to the current checkout. The poll family enforces this
snapshot-locally: `validate_bundle` raises `INPUT_HASH_MISMATCH` when `averages.input_hashes`
does not match the bytes of the bundle's own `polls.json`. The geography family has no such
binding since fix 2: the inventory verifies output bytes, `geography.validate` compares only
IDs and names against `electorates.data`, and nothing ties the registry contents to the
`input_hashes` the geometry envelopes record. The reviewer's reproduction: change
`electorates.data[0].boundary_note`, regenerate its JSON, CSV and the inventory, leave
`input_hashes` unchanged: accepted. Fix 1 was right to stop consulting the checkout; the
missing half is a verifiable snapshot-local binding between the registry as published and the
hash the geometry records (the producer in `daily_refresh.py` already knows both). Regression
tests, additions only: the reviewer's reproduction is rejected with a named error; an
unmodified bundle still validates; a checkout registry change still does not invalidate a
retained bundle (the fix 2 test keeps passing).

## 2. Important: the page budget counts SVG referenced from CSS

Invariant (plan-m2 line 172, decision 7): `test_svg_page_budget` measures every SVG byte the
rendered electorates page needs. `tests/svg_budget.py` collects `href`, `src`, `data` and
`poster` attributes only, so `svg_page_bytes('<div style="background-image:url(../maps/general.svg)"></div>', site)`
returns 0. Collect CSS `url(...)` references as well: `style` attributes, `<style>` blocks and
linked stylesheets (`<link rel="stylesheet">` resolved against the page, `url()` inside a
stylesheet resolved against the stylesheet's own URL). Keep the existing checks (local only,
under the site prefix, file exists). Regression tests, additions only: the reviewer's probe
counts the file; a stylesheet-relative reference resolves correctly; the current built page's
total is unchanged by the new collection if the page has no CSS SVG references (say which in the
report).

## Constraints

- Tests: additions only. Existing assertions stay. Budget constants unchanged.
- Increment 4 files untouched. No fixture bytes change.
- Commit in the worktree; do not push.

## Definition of done

From the worktree:

    uv run --with pytest pytest -q product/nz_election/tests    # all pass, count up from 295
    git diff ba8914b --stat -- product/nz_election/tests        # no removed lines
    python3 product/nz_election/pipeline/verify.py all          # PASS

Report: commit hash, test count, which tests you added, where the registry binding now lives
and which error names it, and the electorates page byte total before and after item 2.
