Committed `e1f4a05` on top of `49da422`; not pushed.

- Added Herald-DigiPoll: now **20 scored records**. No age cutoff; YouGov remains eligible.
- Added capture-based completeness tests and strict month-end validation.
- Base tests untouched; `last.md` uncommitted.

```text
$ uv run --with pytest pytest -q product
1660 passed in 360.65s (0:06:00)

$ bin/lint
lint ok (579 text files)
```

Open questions: none.