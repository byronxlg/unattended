Fresh-context review of PR #70 (nz-election-publish-cleanup), read-only. Worktree .worktrees/nz-election-publish-cleanup,
branch change/nz-election-publish-cleanup, head 7943528. Diff: git diff 382c962...7943528 -- product. Judge against REVIEW.md.

Context: PR #69 CI failed once on an untouched test: publish.py:62 TemporaryDirectory cleanup raised because '.git'
was not empty, read as a detached automatic git gc/maintenance still writing. The change sets gc.auto 0,
maintenance.auto false, gc.autoDetach false in the throwaway checkout right after init. Check: the settings are local
to the throwaway checkout, never the remote or the host's global config; no behaviour of publish (retries, conflict
handling, outcomes) changes; the new test would fail without the three config lines; no pre-existing test edited.

Output: verdict (accept or request changes), then Critical / Important / Nit with file:line.
