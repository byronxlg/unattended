**Verdict: accept.**

- **Critical:** None.
- **Important:** None.
- **Nit:** None.

The header fix wraps links within the phone viewport and retains 44 px targets (`web/styles.css:306`). Enlarged SVG labels resolve the reported sizes: calculated map 12.67 px, trend 12.76 px at 360. Supplied screenshots show readable, separated labels.

`tests/type_scale_browser.py:20` measures computed font size multiplied by `getScreenCTM()` scaling: rendered size, not markup size. It also checks label overlap, bounds and page overflow.

Funding retains the preceding NZD 20,000 threshold, adjacent caveat and EC link. Removed assertions checked literal typography only; wrapping, data, provenance and accessibility assertions remain.

Read-only probes returned:
```text
CSS font-size values outside tokens/inherit: []
Funding blocks with threshold, caveat and EC link: 7
Calculated 360px map: 12.67 px; trend: 12.76 px
```

Reviewed supplied phone and desktop screenshots. No pytest run or files changed. Fresh browser measurements, dark-mode screenshots and reference comparisons were not independently repeated; browser-pass evidence comes from the supervisor.