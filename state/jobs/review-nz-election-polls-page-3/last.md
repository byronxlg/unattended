request changes

Critical: None.

Important:
- `product/nz_election/web/polls.css:1` / `product/nz_election/tests/screenshots.py:208`: Visual verification still targets the wrong page. Both supplied screenshots show “What do the polls tell us?” and seats first; the built branch HTML starts “Who is ahead in the polls?” with averages first. This branch’s `.home-hero` strip should measure **120 px at 390 and 144 px at 1280**, not the reported 72/120. Re-run the host harness and screenshots against the served a538aae build.

Nit: None.

Confirmed: `git diff 93696cc a538aae` removes only the scoped height override. Tests and harness are unchanged; other routes cannot be affected because `polls.css` is loaded only on `polls/`. The code fix is sound, but the supplied evidence does not verify it.