# Build brief: nz-election increment 1 (fixtures, poll parser, allocator; no UI)

You are the engineer in the unattended lab (read AGENTS.md). You are in the worktree
`.worktrees/nz-election-1` on branch `change/nz-election-1`. Commit there; never push.

## Goal

Increment 1 of intent/nz-election/plan.md: the deterministic core that everything else sits on.
The MMP seat allocator (Electoral Act 1993 s191 to s193) in Python and JS with the full official
2023 golden, and the Wikipedia poll-table parser against the committed revision. No averaging,
no export, no templates, no workflows (those are increments 2 and 3).

## Read first, in this order

1. intent/nz-election/plan.md: all of it. "Supervisor decisions" at the end bind; decision 6 is
   your exact file list.
2. intent/nz-election/spec.md sections "Poll method and assumptions", "Allocator contract",
   "Required 2023 golden fixture", "Testing and acceptance", and "Supervisor resolutions".
3. product/nz_election/fixtures/manifest.json and the files it lists. These are the supervisor's
   captures (commit af1b585). Your sandbox has no network: every input is already here.
4. pytest.ini and tests/test_ci.py (the collection assertion you must not weaken).
5. REVIEW.md (how you will be reviewed) and docs/playbook.md Stage 3.

## Constraints

- Never edit anything under product/nz_election/fixtures/: not the bytes, not the manifest
  hashes. Your loader verifies each sha256 and fails `CAPTURE_HASH_MISMATCH: <path>` or
  `MISSING_CAPTURE: <path>`. If a fixture is internally inconsistent, fail
  `FIXTURE_2023_MISMATCH` with the two numbers that disagree and say so in your final message;
  do not patch around it.
- Cross-check the CSV golden against fixtures/ec-2023-xml/election.xml (party votes sum
  2,851,211; seats 122) and build candidate joins from winners.csv, the two list CSVs and
  candidates.xml (list_no, electorate, party). No name-similarity inference.
- The EC CSVs are UTF-8 with a BOM, CRLF, and banner rows before the header; strip at parse
  time only. Never sum electorate rows together with a national total row.
- Exact arithmetic: Python int/Fraction, JS BigInt. Decimal for percentages. No floats in any
  comparison. Quotients compared to party-quotients.csv allowing only its 3dp display rounding.
- Wikitext: a bounded scanner (tables, sections, templates, refs, links), not one regex over the
  page; select the national party-vote table by section and header signature; the plan's
  parse_drift error codes; stable poll ids as the plan specifies.
- pytest.ini: keep `norecursedirs = .* product` and `pythonpath = .`; add
  `testpaths = tests product/nz_election/tests`. Do not add tests/__init__.py or change import
  mode. Product tests import `product.nz_election.pipeline` through namespace packages.
- Node is installed on this host; `test_python_js_parity` runs tests/allocator_runner.mjs and
  fails `NODE_REQUIRED_FOR_PARITY` if node is missing, never skips.
- Python 3.12+, stdlib only at runtime; pytest is the only test dependency. uv inline metadata
  with `dependencies = []` on executable scripts.
- Root AGENTS.md: add one line pointing at product/nz_election/AGENTS.md; keep it under a page.
  Do not edit state/, posts/, prompts/, .github/, existing tests, bin/.
- No emojis, no em dashes anywhere. Comments say why.
- When the plan's wording and a fixture disagree, follow the fixture bytes, record the departure
  in your final message, and never stop to ask.

## Definition of done

Run from the worktree root and paste each command's output in your final message:

1. `uv run --with pytest pytest -q product/nz_election/tests/test_allocator.py product/nz_election/tests/test_poll_parser.py`
   expected: a summary line containing `24 passed` (target; if you merged tests, say which and why,
   and the real count), 0 failed, 0 skipped.
2. `uv run --with pytest pytest --collect-only -q | grep -c "^tests/"` and
   `uv run --with pytest pytest --collect-only -q | grep -c "^product/nz_election/tests/"`
   expected: both counts greater than zero.
3. `uv run --with pytest pytest -q` expected: all existing root tests plus the product tests pass.
4. `bin/lint` expected: `lint ok (<N> text files)`. Stage new files (`git add`) before running it.
5. `git status --short` expected: empty after your final commit.

Final message, under 40 lines: files changed, the five outputs, departures from the plan, open
questions for the supervisor.
