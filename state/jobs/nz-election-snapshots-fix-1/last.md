Committed `281e7d8`. Added `RECORD_LICENCES` validation and two regression cases. Unknown licences now raise `ValueError` naming the file and record.

Verification:
- `uv run --with pytest pytest -q product/nz_election`: **732 passed in 287.72s**
- `bin/lint`: **lint ok (504 text files)**
- Overlaid new tests on unchanged `c737231` loader: **2 failed**, both `DID NOT RAISE`.
- Same tests on committed HEAD: **2 passed**.

Base tests untouched. `last.md` contains the report and remains uncommitted. No push.