Committed `972ed1a` on `change/nz-election-look-a2`. No push; worktree clean; `last.md` untouched.

Changed averaging/export/build/social pipelines, seat-group config, coalition renderer, CSS, methods template, and tests:
- Government blue, Opposition coral; bar ordered Government, grey others, Opposition, including each party’s overhang.
- Persistent social proof-of-concept band with sample size and dates.
- Removed the section-current marker; anchors remain.
- Bounded Others derivation, published disclosures, and v1 bundle compatibility.

Current-fixture topline: **Government 67, Opposition 58, Opportunity 8; majority 67**, assumed House 133.

Moved assertions:
- Government/Opposition colour tokens swapped.
- Strip order and label offsets follow groups and overhang.
- Stale social notice retains sample size and dates.
- October coverage now yields seats; incomplete-state fixtures explicitly omit a named party.

Verification:
```text
uv run --with pytest pytest -q product/nz_election
587 passed in 239.72s (0:03:59)

uv run product/nz_election/pipeline/verify.py all
PASS all

bin/lint
lint ok (464 text files)
```

Remaining host verification: screenshots and `coalitions_browser.py`. Local Chromium launch failed with macOS MachPort permission denied; browser checks were not changed.