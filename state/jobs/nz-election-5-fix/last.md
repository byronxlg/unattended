Committed `e8d1d77`; not pushed. Full diff:

```diff
diff --git a/product/nz_election/tests/screenshots.py b/product/nz_election/tests/screenshots.py
index 7602b00..d317441 100644
--- a/product/nz_election/tests/screenshots.py
+++ b/product/nz_election/tests/screenshots.py
@@ -59,7 +59,7 @@ def check_page(page, url, site, origin):
     from product.nz_election.pipeline.scripts import validate_scripts
     assert validate_scripts(page.content())
     assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'PAGE_OVERFLOW: ' + url
-    for href in page.locator('a[href],link[href]').evaluate_all('(els)=>els.map(e=>e.href)'):
+    for href in page.locator('a[href],link[href]').evaluate_all('(els)=>els.map(e=>new URL(e.getAttribute("href"), document.baseURI).href)'):
         parsed = urlsplit(href)
         if not href.startswith(origin):
             continue
```

SVG anchors retain the existing prefix, file and fragment checks.

```text
uv run --with pytest pytest -q
288 passed in 36.28s

bin/lint
lint ok (253 text files)
```

Departures: none. Chromium was not launched; screenshot verification remains host-only.