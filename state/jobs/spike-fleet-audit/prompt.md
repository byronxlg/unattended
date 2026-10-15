# Spike: Fleet Audit launchctl observer

You are the engineer in the unattended lab (read AGENTS.md). This is a one-job throwaway spike in
phase 1 research: the branch you are on is never merged, so optimise for evidence, not polish.
Keep the whole job under 25 minutes of work.

Read first: intent/candidates/fleet-audit.md (the candidate; especially "Spike", the host
evidence and the interpretation table).

## Goal

Answer with evidence: can the output of `launchctl print gui/<uid>/<label>` on this host be
parsed into structured records (state, pid, runs, last exit code, program, argv, working
directory, schedule as interval seconds or a calendar dictionary, plist path) reliably enough to
fixture, and how many of the host's loaded services parse fully?

## Do

1. Enumerate labels: `launchctl print gui/$(id -u)` and read the services block. Note how many
   labels there are. Also record whether `launchctl list` works in this sandbox (the read-only
   job saw exit 1 with no output) and whether `crontab -l` works.
2. Write spike/launchctl_parse.py (stdlib only, Python 3.12, under 200 lines): parse the nested
   `key = value` and `key = { ... }` text into a dict, then normalise to the record above with
   every field nullable and a `parse_warnings` list. Handle `78: EX_CONFIG` style exit codes,
   arguments containing spaces, `spawn scheduled`, and calendar descriptors that are a list.
3. Run it over every label in gui/$(id -u). Print a table: label, parsed fields present, missing
   fields, warnings. Count how many parse with all of state, program, argv, schedule.
4. Freeze five real outputs as fixtures under spike/fixtures/: com.unattended.tick,
   com.pdw.docker-restart, org.nixos.skhd, one third-party updater, and the error output for
   com.koekeishiya.yabai (exit 113). Write spike/test_parse.py asserting the normalised records
   (tick: program /bin/bash, argv two entries, working directory the repo, interval 600; the
   calendar job: Minute 30 Hour 3 Weekday 0 and pid null; skhd: last exit 78 with the text kept
   in a separate field; the 113 case: a record with a `collection_error` and no invented fields).
5. Compare the disabled-services override block with the per-service lookups and say in the
   final message which labels are disabled, which are absent, and which are both.

## Constraints

Read-only on the host: never bootstrap, bootout, enable, disable, kickstart or load anything.
Do not read evidence files of other projects; only launchctl output and plists under
~/Library/LaunchAgents. Do not edit bin/, state/, docs/ or anything outside spike/. No
dependencies. Commit on this branch. No emojis, no em dashes.

## Definition of done

`uv run --with pytest pytest -q spike/` exits 0. Final message under 60 lines: the answer to the
goal question with the counts (N labels, M parse fully, the failing ones named with why), the
table from step 3, the disabled-versus-absent finding, and anything that surprised you.
