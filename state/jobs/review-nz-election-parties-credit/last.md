**Verdict: accept, with nits.** Review opinion only; no approval issued.

No Important regression found in `3dcc564...fa33005`.

- **Nit, `product/nz_election/tests/test_parties_credit.py:63`:** The whitespace test passes without the CSS fix. It checks text formatting, not whether shares and signed changes remain whole at 360/390. Add browser assertions for wrapping and containment.
- **Nit, `product/nz_election/tests/test_parties_credit.py:57`:** Credit ordering is checked only against polling, not the final party answer. Author/licence text is checked, but link destinations and reachable Methods change notices are not.

All nine portraits retain linked authors and licences, with credits emitted after the party answers and existing `aria-describedby` associations preserved. Modification notices remain in Methods, reachable through the footer. Both [CC BY-SA 4.0 §3](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en#s3) and [CC BY 4.0 §3](https://creativecommons.org/licenses/by/4.0/legalcode.en#s3) require modification disclosure and permit linked attribution. No licence regression found against the snapshots.

The two edited assertions follow the removed processing copy; punctuation, offline-label and attribution checks remain intact. The new tests inspect content and accessibility associations rather than prescribing markup, but have the coverage gaps above.

Three weakest visual points per changed page, from supplied screenshots; these appear inherited:

- **Parties:** large empty desktop area beneath the portrait; mobile policy/governing answers remain below the initial viewport; uppercase tracked governing label conflicts with sentence-case guidance.
- **Home cards:** repeated bordered boxes feel mechanical; narrow leader names create uneven density; change values lack a nearby unit/time label and depend on the introduction.

Verification: read all three requested screenshots. Values remain whole at 390; CSS supports the intended 360 behaviour, but I did not independently verify that viewport.

Read-only `python3 -B -c` probe output:
```text
PASS 9 portrait source/licence links and Methods change notices; 2 new test functions
```

`uv run --offline --with pytest pytest -q -p no:cacheprovider -k 'parties or home or design'` failed before collection: uv cache access denied. Supervisor evidence remains **230 passed; build PASS 82 routes**.

Limitations: brief file absent from this worktree; no before/reference comparison, dark-mode capture or full-page credit screenshots available in the supplied set. No files changed.