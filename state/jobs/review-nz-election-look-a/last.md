**Verdict: request changes.**

- **Important** - [build.py:536](/Users/byron/repos/unattended/.worktrees/nz-election-look/product/nz_election/pipeline/build.py:536): Replacing the social page heading removes its visible “Proof of concept” label when populated; the populated body supplies no replacement. **Fix:** retain the question heading and add a persistent notice band.
- **Important** - [styles.css:31](/Users/byron/repos/unattended/.worktrees/nz-election-look/product/nz_election/web/styles.css:31): The section marker follows `:target`, so scrolling leaves “Seats” or the last clicked section marked indefinitely. **Fix:** progressively update the current marker from the visible section, preserving plain anchors.

Read-only checks: allocator/topline match; 79 routes; contrast passes both modes; font contract passes. First-view bytes: home **55,549**, polls **74,408**; CSS **14,640**. Requested screenshot views inspected. No edits.

Review limitation: PR #33 comments were inaccessible through CLI and connector, so findings could not be deduplicated against the supervisor’s review. Full pytest was not rerun; the local environment lacks pytest.