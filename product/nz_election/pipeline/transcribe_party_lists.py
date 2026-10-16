"""Transcribe the EC party-list PDF (pdftotext -bbox-layout XML) into a reviewed JSON.

Usage: python3 -I transcribe_party_lists.py <bbox.html> <pdf> <out.json>
Columns are fixed from measured x positions; candidates are "RANK SURNAME, Given" lines, with
continuation lines (no rank, not all caps) appended to the previous name. Party headers are
all-caps lines, possibly wrapped. Locators record page, column and line index for review.
"""
import hashlib, json, re, sys, xml.etree.ElementTree as ET
from datetime import datetime, timezone

bbox, pdf, out = sys.argv[1:4]
ns = {"x": "http://www.w3.org/1999/xhtml"}
root = ET.parse(bbox).getroot()
pages = root.findall(".//x:page", ns)
FOOTER = re.compile(r"^(Page \d+ of \d+|Authorised by|For more information)")

def words(line):
    return " ".join(w.text or "" for w in line.findall("x:word", ns)).strip()

def column_of(xmin, edges):
    for i, e in enumerate(edges):
        if xmin < e:
            return i
    return len(edges)

parties, cur, cur_cand = [], None, None
for pno, page in enumerate(pages, 1):
    lines = []
    for ln in page.findall(".//x:line", ns):
        t = words(ln)
        if not t or FOOTER.match(t):
            continue
        y = float(ln.get("yMin")); x = float(ln.get("xMin"))
        if y < 120 or y >= 815:  # title and preamble repeat on every page; footer
            continue
        lines.append((x, y, t))
    # four columns; line xMin clusters at 48, 184, 287 and 456 on every page (measured)
    edges = [130, 240, 400]
    cols = {}
    for x, y, t in lines:
        cols.setdefault(column_of(x, edges), []).append((y, x, t))
    for c in sorted(cols):
        for li, (y, x, t) in enumerate(sorted(cols[c])):
            m = re.match(r"^(\d+)\s+(.+)$", t)
            loc = {"page": pno, "column": c + 1, "line": li + 1, "y": round(y, 1)}
            if m:
                cur_cand = {"rank": int(m.group(1)), "name": m.group(2).strip(), "locator": loc}
                cur["candidates"].append(cur_cand)
            elif t == t.upper() and re.search(r"[A-Z]", t):
                if cur is None or cur["candidates"]:
                    cur = {"party_name": t, "header_locator": loc, "candidates": []}
                    parties.append(cur); cur_cand = None
                else:
                    cur["party_name"] += " " + t
            elif cur_cand is not None:
                cur_cand["name"] += " " + t
                cur_cand.setdefault("continuation_lines", []).append(loc)
            else:
                print("UNPLACED", pno, c + 1, t, file=sys.stderr)

problems = []
for p in parties:
    ranks = [c["rank"] for c in p["candidates"]]
    if ranks != list(range(1, len(ranks) + 1)):
        problems.append({"party": p["party_name"], "ranks": ranks})
    p["list_size"] = len(ranks)

sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
doc = {
    "schema": "ec-party-lists-2026-v1",
    "source": {"path": "ec-2026/wayback-party-lists.pdf", "sha256": sha, "pages": len(pages),
               "origin_url": "https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf"},
    "method": "pdftotext -bbox-layout, column clustering on x, rank lines by regex; see transcribe_party_lists.py",
    "transcribed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "reviewer": "supervisor (Claude), unattended lab",
    "review": {"rank_contiguity": "pass" if not problems else problems, "notes": []},
    "parties": parties,
}
json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)
print("parties", len(parties), "candidates", sum(p["list_size"] for p in parties), "problems", len(problems))
for p in parties:
    print(f'{p["list_size"]:3d}  {p["party_name"]}  p{p["header_locator"]["page"]}c{p["header_locator"]["column"]}')
