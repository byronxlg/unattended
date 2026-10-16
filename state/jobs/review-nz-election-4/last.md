- **Important - `product/nz_election/web/coalitions.mjs:153`**: Unresolved allocation ties leave the unassigned-electorate text stale. Reproduction: use votes `{a:239,b:1,others:0}`, initially zero electorate wins, then give `b` one electorate. The scenario changes unassigned seats from 71 to 70, but `draw()` returns before updating that text.
  **Fix:** Update `[data-unassigned]` before the unresolved-allocation return.

- **Important - `product/nz_election/pipeline/scripts.py:5`**: The stated hash allowlist is only a filename allowlist. No module bytes are hashed, so changing either allowed module, including adding an external import, passes this validator unchanged. `refresh.py` never calls it; build validates HTML before copying the modules.
  **Reproduction:** Alter module contents while retaining its filename; `validate_scripts()` receives identical HTML and returns `True`.
  **Fix:** Pin and verify both modules’ byte hashes before publication, with a mismatch regression check.

Other review results:

- Canonical JSON is re-serialized and compared in both decoders. In-memory probes reported: `Malformed hash probes: 25 Python/JS equal: True all rejected: True`. Dynamic hash content uses no `innerHTML`; rejection messages are static.
- Quotient arithmetic uses BigInt. Seat outputs, unassigned count and assumed House are converted to Number; entitlement counters also use Number. Current bounds prevent precision loss, but this is not literally “BigInt throughout.”
- Parity compares canonical bytes and covers empty selection, overhang, under-threshold electorate eligibility and totals of 71. It omits every-party selection and does not prove resistance to a Number-arithmetic substitution.
- Inspected all four coalition PNGs: majority/House wording remains conditional. Controls, focus and layout show no obvious accessibility defect.
- Module: 12,177 bytes; added CSS: 1,286 bytes. No numeric polls-page budget found in either available plan.

Read-only review; no changes or approval. `uv` execution was blocked by temporary-directory permissions; probes ran through `.venv/bin/python -B`.

Important findings: 2