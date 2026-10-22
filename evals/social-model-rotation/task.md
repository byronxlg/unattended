# Eval: upstream default rotation cannot fail a social daily

Origin: run 39792706334 on 22 October 2026 spent the day's credits, then
classification failed with `SOCIAL_CLASSIFICATION_FAILED`, HTTP 200, `check=model`.
The request named `jev-latest`, which had rotated to `jev-1.14.0`, while the
reviewed registry accepted `jev-1.13.0`. Explicit requests for `jev-1.13.0`
were still served with that version.

Invariant: the requested version and accepted versions share one definition.
Keep strict model validation and record the actual response version in
`model_versions`; do not follow an unreviewed upstream default.

Check: `evals/social-model-rotation/check.sh` reserves and refreshes a synthetic
day through an injected transport. It returns `jev-1.14.0` for `jev-latest`
and echoes pinned versions otherwise. No network or credits are used.
The refresh must classify all 240 posts without classification exclusions
and persist the reviewed version. Expected last line:
`PASS model rotation: 240 classified, pinned model recorded`.
