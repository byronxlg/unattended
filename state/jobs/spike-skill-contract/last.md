Yes, beyond `ls` plus `command -v`: real tts accepts `--help` but omits it from help output. This is a documentation mismatch, not broken TTS behavior. An ordinary helper test could catch it too; this spike does not establish a standalone-product advantage.

Added under `spike/`: contract, 177-line stdlib runner, six fixtures, tests, real receipt, and findings README.

Real run:
```text
MISMATCH helper help interface: missing flags: --help
MISMATCH receipt: spike/tts-receipt.json
```
Exit 1. All executables resolved. Surprisingly, the earlier heredoc restriction did not recur. No network calls or credentials used.

Verification, with offline uv cache settings:
```text
$ uv run --with pytest pytest -q spike/
...........                                                              [100%]
11 passed in 5.53s
```
Fixtures confirmed removed flags mismatch, empty output and timeout remain UNKNOWN, and different bytes with identical version output make receipts STALE.

Open question: does receipt reuse justify maintaining separate contracts?

Commit blocked by sandbox permissions: Git could not create `/Users/byron/repos/unattended/.git/worktrees/spike-skill-contract/index.lock`. Files remain uncommitted.