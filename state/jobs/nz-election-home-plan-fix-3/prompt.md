# nz-election-home-plan fix-3 (PR #64, host harness on 9f555c7)

Host run on 9f555c7 (Chromium starts on the host):
- `check_methods.py artifacts/nz-election/before`: PASS.
- `artifacts/nz-election/fix1/check-review.py`: cf770ea EXPECTED FAIL at 360 and 390; HEAD PASS home and
  methods at 360 and 390, PASS home 1280, then `screenshots.py:191 AssertionError: SMALL_TARGET` on
  methods/ at 1280x800 (build `before`).
- The one offender: in `#records-candidates`,
  `<a href="https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf">Electoral Commission</a>`
  measures 43.984 px high (the 44 px floor misses by a sub-pixel; the global `a{min-height:44px}` is
  being overridden or shrunk in that context).

Fix: make that link (and any link in the same context) meet the 44 px target at every width, from the
markup or CSS, not by editing screenshots.py or the threshold. Tests on main at de9a7c2 may not be
weakened; this branch's own tests may move.

Definition of done:
- Same pytest command as fix-2 passes; `verify all` PASS all on a populated build; `bin/lint` ok.
- Rebuild `artifacts/nz-election/before` (and after, night) with your code; if Chromium starts, run
  `uv run artifacts/nz-election/fix1/check-review.py` (expect exit 0); if not, say so and the
  supervisor reruns it on the host.
- Commit on change/nz-election-home-plan; do not commit last.md or artifacts/.
