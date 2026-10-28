**Verdict: request changes.**

- **Important** - [advance_acceptance.py:22](product/nz_election/pipeline/advance_acceptance.py#L22): `VisibleText` ignores CSS visibility. Wrapping the correct sentence in `<p style="display:none">` still passes acceptance, although readers cannot see the count/date. Check rendered visibility and add a behavioral regression test for CSS-hidden content on both routes.

Read-only probe using `.venv/bin/python -B -c …`, with in-memory page and bundle inputs:

```text
matching: ACCEPTED
CSS-hidden: ACCEPTED
```

No files changed. Pytest was not rerun: the sandbox blocks temporary-file creation. The reported 492 passing tests remain supervisor-provided evidence.