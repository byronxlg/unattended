Committed `29b2ff4`; not pushed. Working tree clean.
Changed `plists.py`, `tests/test_plists.py`, and root `pytest.ini`.

Root pytest, exit 5 (expected):
```text
no tests ran in 0.01s
```
Package pytest, exit 0:
```text
........................................................................ [ 37%]
........................................................................ [ 75%]
................................................                         [100%]
192 passed in 1.00s
```
Registry acceptance, exit 0:
```text
OK registry
```
Root `bin/lint`, exit 0:
```text
lint ok (101 text files)
```
Python 3.12.13 returned a self-referencing array without raising. Used the authorized monkeypatch fallback to verify the exact RecursionError message and exit 3. Nothing outstanding.