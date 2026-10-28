# Follow-up 3: PR #118 third fresh review

Third fresh review (review-nz-election-advance-acceptance-3), one Important, confirmed by the supervisor:

`product/nz_election/pipeline/advance_acceptance.py:96` finds the publication sentence with
`re.findall(r'[\d,]+ advance votes ...')`, which has no left boundary, so a displayed
`-175,748 advance votes reported through 27 October.` or `0.175,748 ...` / `1175,748` style prefixes
match the suffix and pass against a registered count of 175748.

Invariant: acceptance passes only when the complete visible count token equals the registered
cumulative count; a sign, decimal or digit prefix attached to the number is a mismatch
(ADVANCE_RENDER_MISMATCH), on home and on vote/.

Do:
- Anchor the match so the count token is whole (no preceding digit, comma, period, plus, hyphen
  or minus sign, U+2212 included). Keep the error codes as they are.
- Add regressions on both routes (index.html and vote/index.html): negative sign, U+2212, decimal
  prefix, extra leading digit. Each fails on 20b6792 and passes after.

Constraints: tests on main at the base sha do not change; this branch's own tests may move. No
other behaviour changes.

Done when, from the worktree root:
`uv run --with pytest pytest -q product/nz_election/tests/test_advance*.py product/nz_election/tests/test_verify*.py`
passes, and the new cases fail with advance_acceptance.py at 20b6792. Commit; do not push.
