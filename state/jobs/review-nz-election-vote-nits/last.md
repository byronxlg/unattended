**Verdict: request changes.**

**Critical:** None.

**Important**

- `product/nz_election/pipeline/vote_page.py:44-47`: Source credits filter on `source_url`, while the graphics filter only on `date`. Removing election-day’s `source_url` leaves `aria-describedby="source-countdown"` dangling; removing all timeline URLs similarly loses its description. The filter also excludes drawn records from retrieval-date selection: an election-day record retrieved on 26 October without a URL still produces a timeline credit dated 20 October. Select provenance from the records actually drawn and ensure every emitted description reference resolves.

**Nit**

Three visual weaknesses in the supplied screenshots, none blocking:
- `vote_page.py:97`: Deadline paragraphs remain repetitive and dominate the phone help section.
- `styles.css:509`: The desktop label column leaves substantial whitespace beside longer answers.
- `vote_page.py:46`: Repeated source wording adds vertical space on mobile.

**Verification:** Read-only `python3 -B -c` probes; no pytest. Output included:

```text
election missing source_url base dangling=[]
election missing source_url head dangling=['source-countdown']
election missing retrieved_at base KeyError 'retrieved_at'
election missing retrieved_at head KeyError 'retrieved_at'
```

Normal phases, empty records, absent countdown and absent dates had no dangling references. Links and complete snapshot credits matched the base across four phases. Missing `retrieved_at` still crashes, but that is pre-existing.

Inspected both supplied screenshots. Tests are unchanged; existing tests include markup-dependent assertions and do not cover these metadata gaps. No files changed.