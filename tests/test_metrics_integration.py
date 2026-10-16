import json
import runpy
import sys
import time
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

import yaml

from lab_metrics import cli
from lab_metrics.compute import compute
from lab_metrics.models import GitHubSnapshot, SourceResult
from lab_metrics.render import render_document

ROOT = Path(__file__).resolve().parents[1]


def test_real_state_under_60_seconds():
    start=time.monotonic()
    with patch.object(cli, "read_github", return_value=GitHubSnapshot({"prs":SourceResult(False,"offline")})):
        s=cli.collect(ROOT)
        doc=json.loads(render_document(s.head,compute(s),s.diagnostics))
    assert time.monotonic()-start < 60
    assert len(doc["indicators"]) == 56
    keys = {"stage", "kind", "name", "definition", "value", "unit",
            "n", "available", "note", "series"}
    assert all(set(row) == keys for row in doc["indicators"])


def test_pages_workflow_contract():
    doc=yaml.safe_load((ROOT/".github/workflows/pages.yml").read_text())
    steps=doc["jobs"]["build"]["steps"]
    commands=[s.get("run") for s in steps]
    assert commands.index("bin/metrics") < commands.index("bin/blog build")
    step=steps[commands.index("bin/metrics")]
    assert step["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert steps[0]["with"]["fetch-depth"] == 0


def test_ci_collects_root_tests():
    config=(ROOT/"pytest.ini").read_text()
    assert "norecursedirs = .* product" in config
    workflow=(ROOT/".github/workflows/ci.yml").read_text()
    assert "if ls tests/test_*.py >/dev/null" in workflow
    assert "uv run --with pytest pytest -q" in workflow
    assert "working-directory: product/fleet_audit" in workflow


def test_blog_consumes_fragment(tmp_path, capsys):
    # The build's Markdown dependency is irrelevant to this isolated fragment contract.
    with patch.dict(sys.modules, {"markdown":SimpleNamespace(markdown=lambda value, **kw:value)}):
        blog=runpy.run_path(str(ROOT/"bin/blog"),run_name="metrics_blog_test")
    build=blog["build"]
    namespace=build.__globals__
    namespace.update(ROOT=tmp_path, POSTS=tmp_path/"posts", SITE=tmp_path/"site")
    (tmp_path/"posts").mkdir()
    (tmp_path/"site/data").mkdir(parents=True)
    (tmp_path/"site/data/metrics.json").write_text(json.dumps({"html":"<h2>Plan</h2><p>Evidence</p>"}))
    build()
    assert "built 0 posts into site/" in capsys.readouterr().out
    page=(tmp_path/"site/metrics/index.html").read_text()
    assert "<h1>Metrics</h1><h2>Plan</h2>" in page
