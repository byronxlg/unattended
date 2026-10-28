# Fix 1 for PR #117 (settlement capture prep)

Fresh review finding, confirmed by the supervisor: `settlement_capture.py:30-36` runs `LABEL`
(`synthetic|demo|replay|rehearsal|offline fixture`, unanchored, case-insensitive) over the whole row,
including `raw_xml`. Genuine EC XML names parties such as `DemocracyNZ`
(`product/nz_election/fixtures/ec-2023-xml/parties.xml`), so a real 2026 preliminary capture would be
rejected as `NIGHT_CAPTURE_NOT_REAL` on settlement day.

Invariant: the synthetic guard judges provenance, never election content. Labels are looked for only
in provenance fields (envelope provenance, acquisition_source, the actions-xml sources, row metadata
keys other than `raw_xml` and other parsed election content); the known-synthetic XML comparison
stays. You choose the shape.

Done when:
- a regression test builds a genuine-provenance capture whose XML contains `DemocracyNZ` and
  prepares it successfully (it fails on ce85ff3), and the existing synthetic/demo rejection tests
  still pass;
- `uv run --with pytest pytest -q product/nz_election/tests/test_result_import.py` passes except
  Chromium sandbox denials, which you name;
- `bin/lint` ok; commit in this worktree, do not push.

Tests on main at the base sha are not edited; this branch's own tests may move with the fix.
