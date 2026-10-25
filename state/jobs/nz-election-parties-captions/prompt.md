# Parties captions: no orphan punctuation

Page plan: intent/nz-election/pages/parties.md

Goal: on parties/ the source notes under each leader photo and each polling sparkline render as
sentences. Today, at 390x844 and 1280x800 on a live-data build, they show orphan fragments: a lone
"/" before "CC BY-SA 4.0", ". Square crop, resized to 320 pixels..." on its own line, and
". CC BY-SA 4.0. 5% qualifies..." starting a line after "Poll inputs and method". Cause to confirm:
links inside `p.source-actions` are laid out as separate boxes (flex or block, for the 44 px target
rule), so the text nodes between them become their own lines. See parties_page.py:65-67 and
wherever the leader photo credit is rendered (author / licence / changes from snapshots/leaders.json).

This branch stacks on change/nz-election-party-lists (PR #87, open); keep the diff to the caption
markup and CSS.

Constraints:
- Keep the screenshot harness target-size rules passing (SMALL_TARGET etc.); fix the structure
  (for example links as their own items, sentences as their own items, no stray separators), do not
  shrink or exempt targets. Check whether the same `source-actions` markup is shared by home or
  electorate pages; if so, those must not regress either.
- No "not available"-style absent text; credit and licence stay present and linked.
- Tests on main at 3ee6372 are not edited unless a pinned caption string moves with this change;
  say which and why in last.md.
- Add a test that fails on the current branch head: a rendered parties/ source note has no text
  node that starts with "." or "/" once whitespace is trimmed (or an equivalent structural check).

Done when (from the worktree):
- `uv run --with pytest pytest -q product/nz_election/tests -k "parties or design or source"` 0 failed
  (Chromium may be blocked in the sandbox; list which cases were).
- the new test fails with parties_page.py and CSS from origin/change/nz-election-party-lists.
- `bin/lint` prints `lint ok`.
Commit on the branch, do not push, do not commit last.md or artifacts/.
