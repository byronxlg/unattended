# Spike: Skill Contract Check probe runner

You are the engineer in the unattended lab (read AGENTS.md). This is a one-job throwaway spike in
phase 1 research: the branch you are on is never merged, so optimise for evidence, not polish.
Keep the whole job under 25 minutes of work.

Read first: intent/candidates/skill-contract.md (the candidate; especially "Three installed
skills inspected", "Proposed outcome" and "Spike"), then ~/.claude/skills/tts/SKILL.md and
~/.claude/skills/tts/scripts/say.sh (read only; never run say.sh with --text, it costs money).

## Goal

Answer with evidence: does a short author-written contract, run by a probe runner with
identity-bound receipts, catch anything on a real skill that a static linter (missing files,
missing executables) or an ordinary helper test would not?

## Do

1. Write spike/contracts/tts.toml: the executables say.sh needs (bash, jq, curl, ffmpeg,
   doppler, base64, afinfo), the helper's own flags from its --help text (at least --text,
   --voice, --speed, --help), and the two endpoint hostnames as declared-not-probed. Mark the
   example outputs as examples, not requirements.
2. Write spike/skillcheck.py (stdlib only, Python 3.12, under 250 lines): resolve each
   executable, record its path and sha256, run each declared help probe as an argv array with a
   5 second timeout, assert each declared flag appears in the help output, and write a JSON
   receipt with the hashes of SKILL.md, the helper, the contract and every resolved executable.
   A `verify` mode re-hashes and reports STALE when any byte changed. Exit codes 0 pass,
   1 mismatch, 2 incomplete, 3 stale.
3. Run it against the real tts skill from this sandbox. Paste the result. If the sandbox blocks
   the heredoc in say.sh again, say so and classify it as UNKNOWN, not FAIL.
4. Write fixture CLIs under spike/fixtures/ (tiny shell or Python scripts): one advertising
   --speed, one with --speed removed from help, one printing nothing with exit 0, one sleeping
   past the timeout, and two different scripts printing the same --version string. Write
   spike/test_spike.py asserting: removed flag is a mismatch; empty exit-0 is incomplete, not
   pass; timeout is incomplete; same version string but different bytes makes a receipt STALE.
5. In the final message, state plainly: for the real tts skill, did any probe produce a finding
   that `ls` of the referenced files plus `command -v` of the executables would not have?

## Constraints

No network calls, no credentials, never invoke doppler run or curl against an API. Do not edit
anything outside spike/ in this worktree, and nothing under ~/. No dependencies. Commit on this
branch. No emojis, no em dashes.

## Definition of done

`uv run --with pytest pytest -q spike/` exits 0. Final message under 60 lines: the answer to the
goal question, the real-skill run output, the fixture results, and anything that surprised you.
