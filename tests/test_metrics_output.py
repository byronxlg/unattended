import json
from pathlib import Path
from unittest.mock import patch

import pytest

from lab_metrics import cli
from lab_metrics.compute import compute
from lab_metrics.models import Head
from lab_metrics.render import render_document
from lab_metrics.sources import day, read_changes, read_jobs, read_ticks, read_evals, read_mistakes
from test_metrics_indicators import snapshot, change, pr, source


def document(s):
    return render_document(s.head, compute(s), s.diagnostics)


def test_deterministic_bytes():
    s = snapshot(changes=[change(attempts=2), dict(slug="y",attempts=3)],
                 jobs=[dict(id="b",change="y",duration_s=1),dict(id="a",change="x",duration_s=2)])
    first = document(s)
    s.changes.data.reverse()
    s.jobs.data.reverse()
    assert document(s) == first


def test_html_safety():
    s=snapshot()
    indicators=compute(s)
    indicators[0].note='<script>alert("x")</script>'+chr(0x2014)+chr(0x1F600)
    doc=json.loads(render_document(s.head,indicators,{}))
    assert "<script>" not in doc["html"] and "<style>" not in doc["html"]
    assert "&lt;script&gt;" in doc["html"]
    assert chr(0x2014) not in doc["html"] and chr(0x1F600) not in doc["html"]
    assert "<h1>" not in doc["html"]
    assert doc["html"].count("<h2>") == 12


def test_all_spec_rows_present():
    doc=json.loads(document(snapshot()))
    assert len(doc["indicators"]) == 56
    assert {r["stage"] for r in doc["indicators"]} == {
        "Plan","Design","Build","CLAUDE.md","Parallel","Test","Evals","Deploy","Gates","CI/CD","Maintain","Cost"}
    assert all(set(r) == {"stage","kind","name","definition","value","unit","n","available","note","series"}
               for r in doc["indicators"])


def test_empty_and_unavailable_differ():
    doc=json.loads(document(snapshot()))
    rows={i["name"]:i for i in doc["indicators"]}
    assert rows["eval_pass_rate"]["available"]
    assert rows["eval_pass_rate"]["n"] == 0
    assert not rows["breach_to_intent"]["available"]
    assert rows["breach_to_intent"]["value"] is None


def test_nz_day_and_dst():
    assert day("2026-01-01T11:00:00Z") == "2026-01-02"
    assert day("2026-09-26T11:59:00Z") == "2026-09-26"
    assert day("2026-09-26T12:00:00Z") == "2026-09-27"
    s=snapshot(jobs=[dict(id="x",started="2026-09-26T13:00:00Z",ended="2026-09-26T15:00:00Z")])
    rows={r.name:r for r in compute(s)}
    assert rows["mean_jobs"].value == 1
    assert len(rows["mean_jobs"].series) == 1


def test_cli_stdout_and_generated_file(tmp_path, capsys):
    with patch.object(cli, "ROOT", tmp_path), patch.object(cli, "collect", side_effect=lambda root:snapshot()):
        assert cli.main([]) == 0
        report=(tmp_path/"site/data/metrics.json").read_bytes()
        assert capsys.readouterr().out.startswith("metrics: ")
        assert cli.main(["--json","-"]) == 0
        assert capsys.readouterr().out.encode() == report


@pytest.mark.parametrize("value", [None, True, [], {}, "bad", -1, float("inf"), 10**1000])
def test_compute_render_untrusted_values(value):
    s=snapshot(changes=[change(attempts=value,started=value,outcome=value,plan_match=value,prs=[])],
               jobs=[dict(id="x",duration_s=value,usage={"input_tokens":value},started=value,
                          ended=value,rate_limits=value,change=value)],
               ticks=[dict(ts=value,supervisor=value)],
               mistakes=[dict(mistake="x",occurrences=value)],evals=[dict(eval="e",ts=value,passed=value)])
    assert json.loads(document(s))["indicators"]


def test_synthetic_fixture_pipeline():
    base=Path(__file__).parent/"fixtures/metrics/synthetic"
    s=snapshot()
    s.jobs=read_jobs(base/"ledger.jsonl")
    s.ticks=read_ticks(base/"ticks.jsonl")
    s.changes=read_changes(base/"changes.yaml")
    s.mistakes=read_mistakes(base/"mistakes.jsonl")
    s.evals=read_evals(base/"evals.jsonl")
    assert json.loads(document(s))["indicators"]

    s.history=source(json.loads((base/"git_history.json").read_text()))
    s.github.sources={k:source(v) for k,v in json.loads((base/"github.json").read_text()).items()}
    rows={r["name"]:r for r in json.loads(document(s))["indicators"]}
    assert rows["wall_time"]["value"] == 6
    assert rows["deployment_lead_time"]["value"] == 1
    assert rows["total_tokens"]["value"] == 120
