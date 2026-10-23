# Eval: the home page fits its byte budget on live data, not only on fixtures

Origin: production incident 2026-10-23T11:10Z. PR #64 (home rebuilt around ranked voter
questions) merged as 205237c with CI green, then "Publish the blog" failed at "Verify election
pages": `measure_home.py:44` `AssertionError: {'details': 0, 'links': 110, 'source': 5,
'html_bytes': 68868, 'h2': 2}`. The budget is 65,000 bytes. CI builds from fixtures, which are
smaller than the data branch, so the over-budget home only appeared at deploy. Every deploy
fails until it is fixed; the live site keeps serving the previous build and its data goes stale.
Reproduced on the host: main at e32e60e built from data d7b8db903ba4e354f995afc9bd53d12f9d992139 fails the same way.

Invariant: the home page stays under its 65,000-byte budget on the real data branch; the budget
is not raised.

Check: `evals/pages-home-bytes-live/check.sh` builds from data commit d7b8db903ba4e354f995afc9bd53d12f9d992139 and runs
`verify.py all`. Expected last line: `PASS home under budget on data d7b8db903ba4e354f995afc9bd53d12f9d992139`.
