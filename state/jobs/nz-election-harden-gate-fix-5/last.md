Committed `e04e72b`. Not pushed.

- Rejects whole run steps containing unsupported characters before tokenization.
- Sets shlex whitespace to space, tab and newline.
- Five regression cases fail on `dcf467d`; existing tests remain unchanged.
- Real workflow classifications are unchanged.

```text
uv run --with pytest pytest -q product/nz_election/tests/test_harden*.py
257 passed in 0.71s

bin/lint
lint ok (996 text files)
```

Evidence recorded in uncommitted `last.md`. Open questions: none.