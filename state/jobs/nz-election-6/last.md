Committed `7241c10`; not pushed.

Built four daily families with six JSON/CSV datasets, candidate parsers, original 2023 baselines, enrolment, local polls, 71 detail pages, linked maps, validators and 28 new tests.

Verification:
```text
verify.py candidates: PASS candidates: 71 electorates
verify.py electorates: PASS electorates: 71 pages
verify.py all: PASS all
refresh.py --fixtures: PASS refresh: polls bundle
daily_refresh.py: PASS refresh: daily bundles
build.py: PASS build: 77 routes
uv run --with pytest pytest -q:
1 failed, 336 passed in 70.42s (0:01:10)
bin/lint: lint ok (281 text files)
```

Expected capture gates:
- `test_required_baseline_captures` fails: missing Māngere file 21.
- `test_reference_capture_required` passed; both references are present.

Screenshots remain host-only: Chromium failed with Mach port permission denied. No images inspected; `PASS screenshots: 77 routes, 154 baseline images` remains unverified.

Departures:
- Enrolment captures contain national totals only; electorate values remain null.
- Local Kāpiti/Mount Albert mappings remain unresolved; month-only fieldwork retains null day bounds.
- List identities remain separate and capacity unchecked.

Unmapped EC electorate strings: **none**.
Proposal: **0 rows**, at `artifacts/nz-election/candidate-proposals.json`; no exact NFC triples matched. Generated artifacts remain untracked.