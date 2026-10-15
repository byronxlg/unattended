# Skill Contract Check spike

## Finding

The real tts probe found something `ls` and `command -v` cannot: the helper
accepts `--help` but does not advertise it in its help output. All other declared
flags appeared. This is a help-documentation mismatch, not evidence of broken
audio generation or an unsupported flag. All eight declared executables resolved.
The earlier sandbox heredoc failure did not recur in this run.

An ordinary helper test can catch the same mismatch. The fixtures demonstrate
receipt invalidation when tool bytes change without a version change, but do not
establish a real tts regression or an advantage that ordinary tests plus hashes
cannot provide. This evidence does not justify a standalone product yet.

Both endpoint URLs have the same hostname, api.openai.com. Neither was probed.
Example outputs are metadata only and create no prerequisites or probes.

## Recorded real run

```text
$ uv run --python 3.12 spike/skillcheck.py check spike/contracts/tts.toml spike/tts-receipt.json
MISMATCH helper help interface: missing flags: --help
MISMATCH receipt: spike/tts-receipt.json
```

Exit 1. The committed receipt includes full help stdout, empty stderr, helper exit
0, resolved paths, SHA-256 identities, working directory, platform and timestamp.
Only bash and the helper's help path ran; curl and doppler were only hashed.

```text
$ uv run --python 3.12 spike/skillcheck.py verify spike/tts-receipt.json
UNCHANGED identities; original result MISMATCH (not a fresh probe)
```

Exit 1 preserves the original mismatch. Byte changes or missing recorded files
return STALE / exit 3; incomplete evidence returns UNKNOWN / exit 2.

## Verification

The default uv cache was not writable in the sandbox. Only the existing cached
pytest packages and their metadata were copied into ignored `spike/.uv-cache/`.
There were no network calls or downloads. These environment settings kept test
runtime files under spike and disabled network access by uv:

```sh
export UV_CACHE_DIR="$PWD/spike/.uv-cache" UV_OFFLINE=1 UV_PYTHON=3.12
export PYTEST_ADDOPTS='-o cache_dir=spike/.pytest_cache'
export TMPDIR="$PWD/spike/.uv-cache"
uv run --with pytest pytest -q spike/
```

```text
...........                                                              [100%]
11 passed in 5.53s
```

Fixtures cover compatible help, removed speed flag, empty exit-0 help, a 5-second
timeout, identical version output with changed executable bytes, changed skill,
helper and contract bytes, simulated sandbox diagnostics, flag token boundaries,
and missing executables. Absent example outputs do not prevent a passing check.

## Limits and open question

The runner is stdlib-only, under 250 lines, and executes trusted argv arrays.
The environment passes only PATH, HOME and LC_ALL. It is not a security sandbox:
help commands must be reviewed before use. Captured evidence is capped at 64 KiB
per stream, but subprocess capture can use more memory before that check.
Diagnostics and nonzero exits are conservatively UNKNOWN, not flag mismatches.

Receipts are unsigned and bind recorded paths and bytes, checked before and after
probes. Verification checks those paths, not a newly resolved PATH. Transitive
libraries, undeclared tools and the runner itself are not identity-bound. Hashes
do not establish behavioral compatibility, credential validity or audio quality.

Open question: is reusing recorded observations valuable enough to maintain a
separate author-written contract instead of ordinary helper tests?
