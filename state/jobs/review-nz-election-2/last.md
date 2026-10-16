1. **Important - [average.py:26](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/pipeline/average.py:26): arithmetic rounds before display.** `values()` and `mean_vector()` use Decimal’s default precision before producing integer shares. Reproduction: one poll with `scale=10**30`, party share `5*scale-1`, Others `95*scale+1`. Python reproduction printed `exact input qualifies: False`, then `published mean qualifies: True`.
   Fix: normalize and sum using integer scaling or Fraction; reserve Decimal rounding for display.

2. **Important - [build.py:143](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/pipeline/build.py:143): excluded polls affect threshold watch.** The renderer passes every window poll instead of the average’s included IDs. Reproduction: included poll reports 9%, reviewed excluded poll reports 6%; threshold watch still includes the party despite its only included observation being 9%. Excluded rows also contaminate missing-coverage reporting.
   Fix: filter threshold inputs by `average['poll_ids']`.

3. **Important - [publish.py:51](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/pipeline/publish.py:51): newer failure status can be discarded.** A failed 03:00 attempt based on a 01:00 snapshot is rejected when the repository contains a successful 02:00 acquisition. The read-only mocked reproduction returned `older-run-retained`, leaving status fresh and hiding the later failure.
   Fix: retain the newer successful bundle while independently merging the latest attempt’s failure status and current last-good references.

4. **Important - [build.py:221](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/pipeline/build.py:221): output protection permits deleting blog-owned directories.** The guard rejects `site` but accepts `site/posts`, `site/about`, and `site/data`, confirmed by evaluating its predicate. Passing one as `--out` reaches the directory exchange, whose cleanup deletes its previous contents.
   Fix: reject blog-owned destinations and ancestors before staging or replacement.

5. **Important - [build.py:209](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/pipeline/build.py:209): downloads omit required provenance fields.** The rendered catalogue shows neither size, hash, observation range nor per-file producing run, although the manifest contains them. Reproduction: inspect either downloads screenshot or its generated HTML; only file, licence, rows, acquisition and immutable-download columns exist.
   Fix: render the missing manifest fields, with producing-run links and explicit unavailable values.

6. **Important - [styles.css:4](/Users/byron/repos/unattended/.worktrees/nz-election-2/product/nz_election/web/styles.css:4): phone strip uses detached cards instead of anchored label lanes.** `earlier-coherent-window-390x844.png` shows every segment label hidden and six equal bordered tiles below the strip. Labels have no spatial connection to their segments; numerical seat ranges substitute for the required anchors. This conflicts with the anchored-lane and no-repeated-cards requirements.
   Fix: position labels in lanes visibly connected to their proportional segments, retaining 40px counts.

Important findings: 6.