# Eval: a retry must not discard the day's fetched windows

Run `evals/social-retry-budget/check.sh [checkout]`. The optional checkout lets
one unchanged eval exercise baseline code. All requests and sleeps are injected;
no network or paid service is used. Window indices are zero-based.

The transport returns one 503 at window 5, then 200 with ten synthetic posts per
fetched window. Exactly 24 attempts exhaust the 7,560-credit allocation. Expect
23 sampled windows, 230 classifications, fresh status and 7,560 conservative
spent credits. Main 28279a5 instead returns SOCIAL_CREDIT_CAP without a record
(and reports 3,765 spent after its successful-page refunds).

Provenance lists only fetched windows, in strictly increasing order from the
canonical 24-hour schedule. Missing entries mean not fetched; an empty fetched
page still has a timestamp and page-limit flag. This preserves existing complete
records without inventing timestamps for unfetched windows. Captions and status
count the entries. Allocation-limited runs retain worst-case per-attempt charges;
completed runs retain existing successful-page refunds. Reservations and the
pre-request cap are unchanged.
