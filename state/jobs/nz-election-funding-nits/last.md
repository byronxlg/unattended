Committed `bf2d78d`; not pushed.

Changed `funding_page.py`, funding CSS and its tests: full party name, whole-dollar summaries, stacked mobile donor rows and tighter layout.

Te Tai Tokerau Party is registered, not a candidate return. All 146 returns and provenance remain. [EC register](https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/register-of-political-parties)

Verification:
```text
uv run --with pytest pytest -q product/nz_election/tests -k "funding or design"
4 failed, 71 passed, 3006 deselected in 85.96s

bin/lint
lint ok (1175 text files)
```

All four failures are Chromium launch denials: phone type/targets `[map]`, `[trend]`, `[header]`, and night design browser. Screenshots were likewise blocked; host visual review remains.

Both new regressions fail against `fa33005`. Details in uncommitted `last.md`.