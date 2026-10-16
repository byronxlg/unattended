No findings in `7dca242..5a4d299`.

- Count updates cover no-seats states, hash restoration and Reset.
- Test changes are additions only; no existing assertions changed.
- Browser regressions exercise unavailable allocations and verify 71 → 70 → 71.
- Allowlist wording matches validation and module copying.

Parity tests compare canonical bytes. Local execution was blocked: `uv` reported `Failed to initialize cache` with `Operation not permitted`. Chromium was not run; browser paths were reviewed from code.

Important findings: 0