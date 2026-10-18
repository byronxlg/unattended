Committed `390ac75`. Not pushed; no `last.md` committed.

Changed:
- `config/seat-groups.json`: explicit membership, arrangement date and Wikipedia source.
- `pipeline/build.py`: coloured group totals, historical caption, source chip and plain withheld-data message.
- `web/styles.css`: group headline styling; other parties remain grey below.
- `tests/test_design.py`, `tests/test_seat_groups.py`: exact sums, excluded parties and reader-copy checks.

Verification:

```text
uv run --with pytest pytest -q product/nz_election
576 passed in 235.25s (0:03:55)

uv run product/nz_election/pipeline/verify.py all
PASS all

bin/lint
lint ok (456 text files)
```

Populated site rebuilt: `PASS build: 79 routes`. Host screenshots remain supervisor-run. Known coalition-browser failure left untouched.