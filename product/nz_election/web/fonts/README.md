# Self-hosted type

Libre Franklin 400 and 700 and JetBrains Mono 400, under SIL OFL 1.1. Full licences
are beside the fonts. No font service is contacted by the site or build.

Sources downloaded 19 October 2026:

- https://raw.githubusercontent.com/google/fonts/main/ofl/librefranklin/LibreFranklin%5Bwght%5D.ttf
- https://raw.githubusercontent.com/google/fonts/main/ofl/librefranklin/OFL.txt
- https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf
- https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/OFL.txt

Generated with fontTools.varLib.instancer (static weights), then
fontTools.subset and Brotli, preserving U+0020-017F and available U+2000-206F.
Mono keeps kern, mark, mkmk and locl features; programming ligatures are omitted.
Libre Franklin is unhinted. This includes Latin Extended-A. Cmaps were checked for āēīōūĀĒĪŌŪ in all three files.

| File | Bytes |
| --- | ---: |
| libre-franklin-400.woff2 | 16168 |
| libre-franklin-700.woff2 | 16284 |
| jetbrains-mono-400.woff2 | 9668 |

The transfer check follows CSS font URLs and counts all 42120 bytes against the
unchanged 100000-byte first-view limit. Faces use font-display: swap.
