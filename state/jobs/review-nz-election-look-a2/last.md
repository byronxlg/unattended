**Request changes.**

- **Important** | `product/nz_election/pipeline/build.py:161`: Headline seats and averages use derived Others without identifying the derivation in their source notes. **Fix:** disclose the rule and affected contributing polls wherever derived inputs feed displayed numbers.
- **Important** | `product/nz_election/pipeline/social_page.py:68`: The stale band publishes sample counts but omits provenance and synthetic-fixture disclosure. Reproduced: fixture data renders “240 posts sampled from X” without qualification. **Fix:** retain source/input links and the fixture notice alongside stale sample counts.

Read-only verification (`python3 -B -c …`): remainder boundaries passed; raw inputs unchanged; allocation reproduced Government 67, Opposition 58, House 133, majority 67. Bloc contrast passes AA: light blue **5.28:1**, coral **4.52:1**; dark minimum **7.38:1**, **7.53:1**. Inspected supplied screenshots; no route/fragment removal or weakened test assertion found in the diff.

Review limitation: PR #35 comments were inaccessible, so duplication with the supervisor’s findings remains unchecked. `last.md` was absent; `uv` checks were blocked by read-only cache permissions.