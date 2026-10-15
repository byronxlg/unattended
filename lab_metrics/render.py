"""Deterministic JSON document and escaped semantic HTML fragment."""
import json
import math
from dataclasses import asdict
from html import escape


def clean_text(value):
    return "".join("-" if ord(c) == 0x2014 else c for c in value
                   if not (0x1F300 <= ord(c) <= 0x1FAFF or 0x2600 <= ord(c) <= 0x27BF)
                   and not 0xD800 <= ord(c) <= 0xDFFF)


def render_document(head, indicators, diagnostics):
    diagnostics = dict(diagnostics)
    serialization_errors = 0

    def clean(value, precision=4):
        nonlocal serialization_errors
        if isinstance(value, str):
            return clean_text(value)
        if value is None or isinstance(value, (int, bool)):
            return value
        if isinstance(value, float):
            if not math.isfinite(value):
                serialization_errors += 1
                return None
            return round(value, precision) or 0.0
        if isinstance(value, list):
            return [clean(v, precision) for v in value]
        if isinstance(value, dict):
            cleaned = {clean_text(str(k)): clean(v, precision) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
            if value.get("value") is not None and cleaned.get("value") is None:
                cleaned.update(available=False, n=0, note="not shown: invalid aggregate")
            return cleaned
        serialization_errors += 1
        return None

    rows = []
    for indicator in indicators:
        row = clean(asdict(indicator), 6 if indicator.unit == "USD" else 4)
        row["series"].sort(key=lambda item: json.dumps(item, sort_keys=True))
        rows.append(row)
    html = []
    stages = list(dict.fromkeys(r["stage"] for r in rows))
    for stage in stages:
        html.append(f"<h2>{escape(stage)}</h2>")
        html.append("<table><thead><tr><th>Indicator</th><th>Definition</th>"
                    "<th>Value/unit</th><th>n</th><th>Note</th></tr></thead><tbody>")
        for row in rows:
            if row["stage"] != stage:
                continue
            value = row["value"]
            display = "unavailable" if not row["available"] else "no data (n=0)" if value is None else str(value)
            cells = [row["name"], row["definition"], f"{display} {row['unit']}", str(row["n"]), row["note"]]
            html.append("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in cells) + "</tr>")
        html.append("</tbody></table>")
    diagnostics = clean(diagnostics)
    if serialization_errors:
        diagnostics["invalid_output_values"] = serialization_errors
    doc = dict(generated_at=clean(head.committed_at), head_commit=clean(head.sha),
               indicators=rows, diagnostics=diagnostics, html="\n".join(html))
    return (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+"\n").encode("utf-8")
