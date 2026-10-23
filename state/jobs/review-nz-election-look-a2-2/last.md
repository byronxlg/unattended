Verdict: **accept**, with verification limits below.

- **Critical:** None found.
- **Important:** None found.
- **Nit:** None.

Both disclosure fixes cover home, polls, affected modules, and OG cards. Verified 2,547 internal links and fragments, including the affected-poll list. Stale social rendering retains synthetic-data labels and source/input links.

Fix `4cc41f7` changes no tests inherited from `a39c2ec` and moves no checks. Reviewed supplied phone, desktop, and dark-mode screenshots; no new regression found.

Read-only Python checks:
```text
PASS retained bundle validates
PASS disclosure and provenance: home, polls, both OG cards
PASS internal links and fragments: 2547
PASS stale social disclosure and provenance: page and home
```

Limits: PR comments were inaccessible. The requested engineer-account path was absent; checked root `last.md` instead. `uv run --with pytest pytest -q` failed before collection because cache access was denied; fallback Python lacked pytest. Full-suite results were not independently reproduced.