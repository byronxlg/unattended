Research incomplete: **no electorate-detail URL or HTTP 200 confirmed**. No files written, including `last.md`, respecting the read-only constraint and filesystem permissions.

1. **URL rules**
   - 2023 and mediademo: exact detail filename remains unresolved. An [EC disclosure, page 1](https://elections.nz/assets/OIA-requests/2024/2024-04-Documents-released.pdf) documents `https://electionresults.govt.nz/electionresults_2023/xml/e39/votingplaces/39-39034.xml`. This establishes a voting-place path, not the electorate-total filename.
   - 2026 preliminary: the [2026 media kit, page 11](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf) specifies `http://media.election.net.nz/xml/`. Its HTTPS equivalent and detail rule remain unverified.
   - 2026 official: `https://electionresults.govt.nz/electionresults_2026/xml/` remains an inferred archive convention, not a confirmed publication contract.
   - No observed HTTP status supports claiming 200 or 404 for these probes.

2. **Detail contents and element names**
   
   No detail XML body was fetched. Candidate/party vote elements, voting-place counters and update-time fields remain unconfirmed. The disclosure above cannot substitute for inspecting a file.

3. **2026 documentation**
   
   **Published:** [2026 General Election media kit, March 2026](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf), linked from [EC media resources](https://elections.nz/media-and-news/media-resources). Page 11 provides the HTTP feed address and directs media to `media@elections.govt.nz` for testing updates. I found no feed-specific HTTPS guarantee, CORS policy, rate limit or reuse terms in that kit. A separate 2026 XML specification was not located; its absence is not established.

4. **Increment 5 implications**
   
   Retain serial polling and the 30-second floor as **project safeguards**, not verified EC requirements. Nothing found justifies relaxing them. Keep HTTPS/CORS verification and packaged fallback as acceptance gates. The kit does not establish browser access. [Plan]( /Users/byron/repos/unattended/intent/nz-election/plan-m3.md:54), [EC kit](https://elections.nz/assets/2026-Media-Kit-/2026-General-Election-media-kit.pdf).

Verification command:
```text
curl -I --max-time 20 https://mediademo.electionresults.govt.nz/
curl: (6) Could not resolve host: mediademo.electionresults.govt.nz
```

Web-tool XML probes returned “not accessible via this tool”, including the known national file. Wayback 2017/2020/2023 media-page attempts also failed; no browser was available. These are access failures, not evidence of missing files. The exact paths, raw schema, status codes, CORS and XML-specific usage policy remain open.