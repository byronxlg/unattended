Verdict: **request changes** for missing visual verification. No functional defect found.

- **Critical:** None.
- **Important:** `REVIEW.md:15`, `intent/nz-election/pages/parties.md:58`: Pass 4 cannot be completed. No 390x844 or 1280x800 screenshots are available; `last.md` records Chromium launch failure. Supply screenshots and record the visible answers to the top three questions: policies, leadership/candidates, and governing partners.
- **Nit:** None.

Read-only Python probes, without pytest:
```text
PASS 32 empty-field combinations
PASS licences ending in a period are not doubled
head live/offline: 0 orphan nodes
main 6366d90 live/offline: 20 orphan nodes
PASS HTML outside photo/poll captions identical to main, live and offline
```

The revised pinned assertion preserves exact visible-part equality, allowing only surrounding whitespace. The new regression assertion fails on `6366d90` in both modes. No files changed.