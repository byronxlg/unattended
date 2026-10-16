import json
from pathlib import Path
import yaml

FIXTURES = Path(__file__).parent / "fixtures/metrics"

def test_real_fixture_shapes():
    jobs = [json.loads(x) for x in (FIXTURES / "real/ledger.jsonl").read_text().splitlines()]
    assert [j["id"] for j in jobs] == ["smoke-0", "smoke-1"]
    changes = yaml.safe_load((FIXTURES / "real/changes.yaml").read_text())["changes"]
    assert changes[0]["attempts"] == 11
    assert len(changes[0]["prs"]) == 5

import subprocess
import time
from unittest.mock import patch
import pytest
from lab_metrics import sources as s

def test_malformed_line_skipped_and_counted(tmp_path):
    p = tmp_path / "jobs"
    p.write_text('\nno\n[]\n{}\n{"id":"x","duration_s":true}\n')
    r = s.read_jobs(p)
    assert r.skipped == 3
    assert r.warnings["invalid_number"] == 1
    assert r.data[0]["duration_s"] is None

def test_duplicate_job_ids(tmp_path):
    p = tmp_path / "jobs"
    p.write_text('{"id":"x"}\n{"id":"x","kind":"fix"}\n{"id":"y"}\n{"id":"y"}\n')
    r = s.read_jobs(p)
    assert [x["id"] for x in r.data] == ["y"]
    assert r.skipped == 3

def test_optional_evidence_missing(tmp_path):
    assert not s.read_evals(tmp_path / "missing").available
    p = tmp_path / "empty"
    p.touch()
    assert s.read_evals(p).available

@pytest.mark.parametrize("value", [True, [], {}, "nan", "inf", -1, 10**1000])
def test_invalid_numbers(value):
    r = s.SourceResult()
    assert s.number(value, r) is None
    assert r.warnings == {"invalid_number": 1}

@pytest.mark.parametrize("value", [True, [], {}, "no", "0001-01-01T00:00:00+12:00", "9999-12-31T23:00:00Z"])
def test_invalid_timestamps(value):
    r = s.SourceResult()
    assert s.timestamp(value, r) is None
    assert r.warnings == {"invalid_timestamp": 1}

def test_github_pagination_and_envelopes():
    with patch.object(s.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '[[{"number":2}],[{"number":1}]]', "")) as run:
        assert [x["number"] for x in s.read_prs("a/b", time.monotonic()+10).data] == [1,2]
        assert "--paginate" in run.call_args.args[0]
    with patch.object(s.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '[{"check_runs":[]},{}]', "")):
        assert not s.read_checks("a/b", "abc", time.monotonic()+10).available

@pytest.mark.parametrize("error", ["401 auth", "403", "rate limit", "connection"])
def test_github_unavailable(error):
    with patch.object(s.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", error)):
        assert not s.read_prs("a/b", time.monotonic()+10).available

@pytest.mark.parametrize("error", [FileNotFoundError(), subprocess.TimeoutExpired("gh", 1)])
def test_github_process_failure(error):
    with patch.object(s.subprocess, "run", side_effect=error):
        assert not s.read_prs("a/b", time.monotonic()+10).available

def test_github_deadline():
    with patch.object(s.subprocess, "run") as run:
        assert not s.read_prs("a/b", time.monotonic()-1).available
        run.assert_not_called()

def test_git_first_addition_and_touches(tmp_path):
    with patch.object(s, "git", side_effect=lambda root,args: "aaa\t2026-01-01T00:00:00Z\n" if "--diff-filter=A" in args else "aaa\t2026-01-01T00:00:00Z\nbbb\t2026-01-02T00:00:00Z\n"):
        rows = s.read_artifact_history(tmp_path, ["x"]).data
        assert len(rows) == 6
        assert rows[0]["added"] and not rows[1]["added"]

def test_nested_yaml_and_invalid_slug(tmp_path):
    p=tmp_path/"changes.yaml"
    p.write_text("changes:\n  - slug: 12\n  - slug: good\n    usage: &loop\n      usage: *loop\n")
    r=s.read_changes(p)
    assert r.skipped == 1
    assert r.warnings["excessive_nesting"] == 1

def test_github_concurrency_cache_and_global_stop():
    import threading
    active=peak=0
    calls=[]
    lock=threading.Lock()
    def run(args, **kw):
        nonlocal active,peak
        endpoint=args[args.index("GET")+1]
        with lock:
            active+=1
            peak=max(peak,active)
            calls.append(endpoint)
        time.sleep(0.005)
        if "/pulls?" in endpoint:
            payload=[[{"number":1,"head":{"sha":"abc"}},{"number":2,"head":{"sha":"abc"}}]]
        elif "/runs?" in endpoint:
            payload=[{"workflow_runs":[]}]
        elif "check-runs?" in endpoint:
            payload=[{"check_runs":[]}]
        else:
            payload=[[]]
        with lock:
            active-=1
        return subprocess.CompletedProcess(args,0,json.dumps(payload),"")
    with patch.object(s.subprocess,"run",side_effect=run):
        snap=s.read_github("a/b",[1,2],time.monotonic()+5)
    assert peak == 2
    assert sum("check-runs?" in path for path in calls) == 1
    assert snap.get("checks:1").available
    with patch.object(s.subprocess,"run",return_value=subprocess.CompletedProcess([],1,"","401 auth")) as run:
        s.read_github("a/b",[],time.monotonic()+5)
        assert run.call_count <= 2

def test_invalid_optional_shape_counted(tmp_path):
    p=tmp_path/"jobs"
    p.write_text('{"id":"x","usage":[],"rate_limits":false,"change":{},"killed":"yes"}\n')
    r=s.read_jobs(p)
    assert sum(r.warnings.values()) == 4


def test_github_bounded_calls():
    """At most 4 + 3*linked_PRs + failed_Pages_runs subprocesses: 12 here, for 500 runs."""
    from test_metrics_indicators import snapshot, change, metrics, pr
    calls = []
    runs = [dict(id=i, created_at="2026-01-01T00:00:00Z",
                 updated_at="2026-01-01T08:00:00Z", head_sha="merge",
                 conclusion="failure" if i < 2 else "cancelled" if i % 3 == 0 else "success")
            for i in range(500)]
    def run(args, **kwargs):
        endpoint = args[args.index("GET")+1]
        calls.append(endpoint)
        if "/pulls?" in endpoint:
            payload = [[pr(n, head={"sha":str(n)}, merge_commit_sha="merge") for n in (1, 2)]]
        elif "/workflows/pages.yml/runs?" in endpoint:
            payload = [{"workflow_runs":runs[:250]}, {"workflow_runs":runs[250:]}]
        elif "/workflows/ci.yml/runs?" in endpoint:
            payload = [{"workflow_runs":[]}]
        elif "/jobs?" in endpoint:
            ident = int(endpoint.split("/runs/")[1].split("/")[0])
            assert ident in (0, 1)
            payload = [{"jobs":[dict(id=ident, name="deploy", status="completed",
                                    conclusion="failure", completed_at="2026-01-01T07:00:00Z")]}]
        elif "/check-runs?" in endpoint:
            payload = [{"check_runs":[]}]
        else:
            payload = [[]]
        return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
    with patch.object(s.subprocess, "run", side_effect=run):
        github = s.read_github("a/b", [1, 2], time.monotonic()+45)
    assert len(calls) <= 12
    assert {key for key in github.sources if key.startswith("jobs:")} == {"jobs:0", "jobs:1"}
    snap = snapshot(changes=[change(prs=[1, 2], outcome="merged")])
    snap.github = github
    rows = metrics(snap)
    for name in ("deployment_frequency", "deployment_lead_time", "restore_time"):
        assert rows[name].available
        assert rows[name].n > 0
