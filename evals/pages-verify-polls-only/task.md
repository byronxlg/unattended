# Eval: the Pages verifier accepts a bundle with only the published families

Origin: production incident 2026-10-16T21:55Z. After increment 6 (PR #14, 379d93a) merged,
Pages runs 38972492825 and 38972584106 failed at "Verify election pages" with
`VERIFY_FAILED: supplied daily families`: the data branch held only the hourly polls family and
the verifier demanded every daily family, which no workflow published yet. Deploys were blocked
until the hotfix (change/nz-election-6-hotfix).

Invariant: the Pages build deploys whenever the published data validates; families that have not
been published render their empty state and are not demanded by the verifier.

Check: `evals/pages-verify-polls-only/check.sh` builds a polls-only bundle with the real pipeline,
builds the site from it, and runs `verify.py all` against both. Expected last line: `PASS all`.
