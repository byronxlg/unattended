# nz-election-night-design fix-2 (follow-up on the build thread)

Host run of 218d9aa (real Chromium, macOS host): `pytest -x` over test_design*, test_home*, test_night*, test_waterfall*
gave 321 passed, then 1 error:

test_night_page.py::test_xml_python_browser_parity -> night_browser.py:66 images() -> screenshots.py:163 check_page:
`page.locator('header')` strict mode violation, resolved to 2 elements: the site banner and the new
`<header class="module-head">` ("Who has enough seats?") that 218d9aa added on night/.

The harness check is about the site banner (HEADER_OVERFLOW, HEADER_TARGET_BOUNDS on line 164 too). Either make the
two header checks target the banner unambiguously (the banner element or role=banner, same assertions, same codes,
same pages), or drop the second <header> from night/ markup. Do not weaken either assertion. screenshots.py and
night_browser.py are test harness files that move with this branch; the assertions in them must stay as strong.

Definition of done: commit on change/nz-election-night-design. In your sandbox Chromium cannot launch; say which
browser tests you could not run. The supervisor reruns on the host:
`uv run --with pytest --with playwright pytest -q product/nz_election/tests/test_design*.py product/nz_election/tests/test_home*.py product/nz_election/tests/test_night*.py product/nz_election/tests/test_waterfall*.py`
expected: all pass, 0 errors. `bin/lint` prints `lint ok`. Do not commit last.md or artifacts/.
