Verdict: **request changes**

Critical: None.

Important:
- `product/nz_election/tests/test_electorate_policy_links.py:25` still pins the exact `class="race-candidates module"` string, including class order. `tests/test_electorates.py:18,82` likewise pins `class="hex-map electorate-locator"`. These branch-modified assertions fail the requested no-markup/class-pinning condition. Use semantic identity and question-order assertions.

Nit:
- `intent/nz-election/plan.md:318` documents actions before candidates, contradicting the implementation and accepted page order. Update the recorded decision.

Both previous findings are fixed. Read-only probes passed for all 71 electorates with populated and empty candidate lists: fragment destinations resolve, empty candidates disappear, and candidate/enrolment/Policy order holds.

Inspected supplied phone, desktop and dark screenshots, including the 11-candidate Christchurch East ballot. Phone enrolment fits; reading text uses body-size tokens. No pytest run or files changed. Browser measurements rely on the supplied host verification.