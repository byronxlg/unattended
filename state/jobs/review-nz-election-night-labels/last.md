Verdict: **accept** as a review recommendation, not approval. No Important findings.

The diff meets the brief: replay/archive reporting identifies the final count, live preliminary reporting retains its clock, bloc labels share one source, and the legend retains party names. Added tests check rendered text behaviour without pinning markup.

Non-blocking findings, including the three weakest visual points required by REVIEW.md:

- **Nit** - `product/nz_election/tests/test_night_page.py:261`: Add a positive live-clock assertion alongside the replay checks to protect both branches.
- **Nit, pre-existing** - `product/nz_election/pipeline/night_page.py:78`: Introductory spacing pushes the phone’s seat answer low in the viewport.
- **Nit, pre-existing** - `product/nz_election/pipeline/night_page.py:85`: The majority threshold repeats in the answer, graphic and caption.
- **Nit, pre-existing** - `product/nz_election/pipeline/night_page.py:88`: Electorate navigation follows the entire hero and falls outside the supplied phone screenshot.

Inspected both supplied screenshots. No visible label collisions. Full-page, dark-mode and previous-version comparisons remain unverified.

Attempted:
```text
uv run --with pytest --with playwright pytest -q product/nz_election/tests -k night
bin/lint
```
Both stopped with:
```text
error: Failed to initialize cache at `/Users/byron/.cache/uv`
Caused by: failed to open file `/Users/byron/.cache/uv/sdists-v9/.git`:
Operation not permitted (os error 1)
```

Relied on the supplied supervisor evidence for 364 passing tests, lint and the 81-route build. No files changed.