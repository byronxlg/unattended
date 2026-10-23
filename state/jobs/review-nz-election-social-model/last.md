Verdict: **accept**, with verification limits below.

- Critical: none.
- Important: none.
- Nit: none.

Request and validation share the pin (`social.py:46,47,290`). The regression exercises the real request path through injected transport (`test_social_model_rotation.py:11`). The runbook explains pin changes and historical-version retention (`runbook.md:251`). No existing checks weakened; no raw posts, handles, or keys found in the diff. No data or log files changed.

In-memory comparison using main and head:
```text
main ['jev-latest'] SOCIAL_CLASSIFICATION_FAILED
head ['jev-1.13.0'] classified 10
10 malformed model probes passed
```

Verification limits: `evals/social-model-rotation/check.sh` could not create temporary files in the read-only sandbox. Pytest was unavailable and uv cache access was blocked. Full eval fail/pass remains unverified. GitHub connectivity failed, so PR text/comments could not be checked for leaks.