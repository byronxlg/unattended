Verdict: **accept**.

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

Reviewed both diffs against `REVIEW.md` and “Deployed acceptance.” Required-family checks cover every supplied location before manifest validation; CLI preserves `MISSING_NIGHT_FAMILY`.

Read-only `python3 -B -c` probes:
```text
PASS 108 required preflight cases: MISSING_NIGHT_FAMILY, nonzero SystemExit, no stdout
PASS optional aggregate dispatch: both SKIP lines, neither night validator invoked, exit 0
PASS 11 malformed requirement strings: rejected without echoing input
PASS real CLI absent-directory probe: exit 1; FAIL all: MISSING_NIGHT_FAMILY
```

Matrix and optional-dispatch probes used in-memory mocks; full validation was not rerun. No existing main tests changed. No pytest run or files modified. Open questions: none.