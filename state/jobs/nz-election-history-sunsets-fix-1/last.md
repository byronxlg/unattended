Committed `5450f61`; not pushed.

Recovery evidence now excludes the sunset instant and later runs. Other window boundaries retain existing behaviour. Added 15 checker cases; base tests unchanged.

Required verification:
```text
373 passed, 2926 deselected in 16.66s
```

`bin/lint`:
```text
lint ok (1393 text files)
```

All three at-sunset cases failed with checker `498932c`. Updated uncommitted `last.md`. No state files touched; no open questions.