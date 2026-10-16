Design-system change for the NZ election site, from the design track Byron asked for on issue #15.

- Intent: intent/nz-election/intent.md
- Spec: intent/nz-election/spec.md
- Design (accepted draft 2): intent/nz-election/design.md
- Plan: intent/nz-election/plan-m2.md (design track)
- Engineer's report: product/nz_election/DESIGN_REPORT.md

What changed: every route restyled to draft 2 (home sentence in four forms, one label row stripped, source-note grammar, twelve states), favicon, OG template, web manifest, night tokens; design checks (CSS budget, first-view budget, source-note bottom edge at 360 and 390, contrast, axe, viewport) under product/nz_election/tests. No change to data captures, routes, workflows or verify.py.

Verification on the host (this branch):

```text
uv run product/nz_election/pipeline/refresh.py --fixtures ... && build.py ... && verify.py all   -> PASS all
uv run --with pytest pytest -q product/nz_election/tests                                        -> see CI
uv run product/nz_election/tests/screenshots.py --site /tmp/ds-site --out /tmp/ds-shots         -> see review log below
```

The first host screenshot run failed on the harness's own axe check (aria-label on a presentational segment inside the role="img" seats strip); fixed on this branch by the follow-up job nz-election-design-fix. Reviews: supervisor review and a fresh-context Codex review (review-nz-election-design) are logged below with the screenshots judged.
