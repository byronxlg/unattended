from lab_metrics.compute import compute
from lab_metrics.models import GitHubSnapshot, Head, Snapshot, SourceResult
from lab_metrics.sources import normalize


def source(rows=()):
    result = SourceResult()
    result.data = [normalize(r, result) for r in rows]
    return result


def snapshot(changes=(), jobs=(), prs=(), history=(), ticks=(), mistakes=(), evals=(), **github):
    sources = {"prs": source(prs), "gates": source(), "ci.yml": source(), "pages.yml": source()}
    sources.update({k: source(v) for k, v in github.items()})
    return Snapshot(Head("abc", "2026-01-04T00:00:00Z"), source(jobs), source(ticks),
                    source(changes), source(mistakes), source(evals), source(history), GitHubSnapshot(sources))


def metrics(s):
    return {i.name: i for i in compute(s)}


def artifact(name, hour, order, added=True, slug="x", sha=None):
    return dict(slug=slug, artifact=name, committed_at=f"2026-01-01T{hour:02}:00:00Z",
                order=order, added=added, sha=sha or str(order))


def pr(n=1, merged="2026-01-01T06:00:00Z", **kw):
    return dict(number=n, created_at="2026-01-01T00:00:00Z", merged_at=merged, **kw)


def change(**kw):
    return dict(slug="x", **kw)


def test_conversation_to_intent():
    m = metrics(snapshot(changes=[change(started="2026-01-01T00:00:00Z")], history=[artifact("intent", 2, 1)]))
    assert m["conversation_to_intent"].value == 2
    assert m["conversation_to_intent"].n == 1


def test_intent_survival():
    m = metrics(snapshot(changes=[dict(slug=str(i), outcome=o) for i,o in enumerate(["open","accepted","closed","reverted"])]))
    assert m["intent_survival"].value == 100*2/3
    assert m["intent_survival"].n == 3


def test_intent_changes_after_spec():
    m = metrics(snapshot(changes=[change()], history=[artifact("intent",0,0), artifact("spec",1,1),
                                                    artifact("intent",0,2,False), artifact("intent",2,1,False)]))
    assert m["intent_changes_after_spec"].value == 1


def test_intent_to_spec():
    m = metrics(snapshot(changes=[change()], history=[artifact("intent",1,0),artifact("spec",3,1)]))
    assert m["intent_to_spec"].value == 2


def test_spec_rework():
    m = metrics(snapshot(changes=[change()], history=[artifact("spec",1,0),artifact("plan",3,1)]))
    assert m["spec_rework"].value == 0
    assert m["spec_rework"].n == 1


def test_first_pass_merge():
    m = metrics(snapshot(changes=[change(outcome="merged",attempts=1),dict(slug="y",outcome="merged",attempts=2),
                                 dict(slug="z",outcome="merged",attempts=True)]))
    assert m["first_pass_merge"].value == 50
    assert m["first_pass_merge"].n == 2


def test_plan_to_final_merge():
    m = metrics(snapshot(changes=[change(outcome="merged",prs=[1,2])],prs=[pr(),pr(2, "2026-01-01T08:00:00Z")],
                         history=[artifact("plan",2,0)]))
    assert m["plan_to_final_merge"].value == 6


def test_rework_cycles():
    m = metrics(snapshot(changes=[change(attempts=11)], jobs=[dict(id=str(i),kind="fix",change="x",killed=True) for i in range(7)]))
    assert m["rework_cycles"].value == 17
    assert m["rework_cycles"].series[0]["fix_jobs"] == 7


def test_plan_match():
    m = metrics(snapshot(changes=[change(outcome="merged",plan_match=True),dict(slug="y",outcome="merged",plan_match=None)]))
    assert m["plan_match"].value == 100 and m["plan_match"].n == 1


def test_repeated_mistakes():
    m = metrics(snapshot(mistakes=[dict(mistake="x",occurrences=["a","a","b"])]))
    assert m["repeated_mistakes"].value == 1


def test_concurrent_jobs():
    jobs = [dict(id=str(i),started=f"2026-01-01T0{a}:00:00Z",ended=f"2026-01-01T0{b}:00:00Z")
            for i,a,b in [(1,0,2),(2,1,2),(3,2,3)]]
    m = metrics(snapshot(jobs=jobs))
    assert m["peak_jobs"].value == 2
    assert m["mean_jobs"].value == 4/3
    assert m["mean_jobs"].n == 3
    assert not m["review_quality_held"].available


def test_weekly_merges_and_rework():
    m = metrics(snapshot(changes=[change(outcome="merged",prs=[1,2],attempts=3)],
                         prs=[pr(1,"2025-12-31T00:00:00Z"),pr(2,"2026-01-01T00:00:00Z")]))
    assert m["weekly_merges"].series[0]["week"] == "2026-W01"
    assert m["weekly_merges"].value == 2
    assert m["weekly_completed_changes"].value == 1
    assert m["weekly_rework"].value == 2


def test_first_pass_ci():
    checks=[dict(id=i,app={"slug":"ci"},name="test",started_at=f"2026-01-01T0{i}:00:00Z",
                 status="completed",conclusion=c) for i,c in [(1,"failure"),(2,"success")]]
    s = snapshot(changes=[change(prs=[1])],jobs=[dict(id="j",kind="build",change="x")],prs=[pr()],
                 **{"checks:1":checks})
    assert metrics(s)["first_pass_ci"].value == 0
    s.github.sources["checks:1"].data[0]["status"] = "in_progress"
    assert metrics(s)["first_pass_ci"].n == 0


def test_review_time():
    m=metrics(snapshot(changes=[change(prs=[1])],prs=[pr()],**{"reviews:1":[dict(id=1,state="APPROVED",submitted_at="2026-01-01T00:30:00Z")]}))
    assert m["review_time"].value == 30


def test_change_failure_rate():
    s=snapshot(changes=[change(prs=[1,2],outcome="merged")],prs=[pr(),pr(2,"2026-01-01T08:00:00Z")],
               jobs=[dict(id="j",kind="fix",change="x",started="2026-01-01T07:00:00Z")])
    assert metrics(s)["change_failure_rate"].value == 0
    s.jobs.data[0]["started"]="2026-01-01T09:00:00Z"
    assert metrics(s)["change_failure_rate"].value == 100


def test_eval_pass_rate_and_latency():
    m=metrics(snapshot(evals=[dict(eval="e",ts="2026-01-01T02:00:00Z",incident_at="2026-01-01T00:00:00Z",passed=True),
                             dict(eval="e",ts="2026-01-02T00:00:00Z",passed=False), dict(eval="b",passed="yes")]))
    assert m["eval_pass_rate"].value == 50
    assert m["incident_to_eval"].value == 2
    assert m["incident_to_eval"].n == 1


def test_regression_detection():
    m=metrics(snapshot())
    assert all(not m[n].available for n in ["regressions_ci","regressions_after_merge","regressions_ci_share"])


def test_first_review():
    m=metrics(snapshot(changes=[change(prs=[1])],prs=[pr()],**{
        "reviews:1":[dict(id=1,state="APPROVED",submitted_at="2026-01-01T00:30:00Z")],
        "comments:1":[dict(id=2,created_at="2026-01-01T00:10:00Z")]}))
    assert m["first_review"].value == 10


def test_agent_resolution_proxy():
    m=metrics(snapshot(changes=[change(prs=[1,2])],prs=[pr(),pr(2,None)],**{
        "comments:1":[dict(id=1,created_at="2026-01-01T00:10:00Z")],
        "comments:2":[dict(id=2,created_at="2026-01-01T00:10:00Z")]}))
    assert m["agent_resolution_proxy"].value == 50
    assert not m["human_free_resolution"].available


def test_defect_proxies():
    m=metrics(snapshot(changes=[change(prs=[1],outcome="merged")],prs=[pr()],**{"comments:1":[
        dict(id=1,created_at="2026-01-01T01:00:00Z"),dict(id=2,created_at="2026-01-01T08:00:00Z")]}))
    assert m["pre_merge_comments"].value == 1
    assert m["post_merge_fixes"].value == 0
    assert not m["defects_caught"].available


def test_gate_wait():
    m=metrics(snapshot(gates=[dict(number=1,created_at="2026-01-01T00:00:00Z",closed_at="2026-01-01T02:00:00Z"),
                             dict(number=2,created_at="2026-01-03T00:00:00Z")]))
    assert m["closed_gate_wait"].value == 2
    assert m["open_gate_age"].value == 24


def test_pipeline_triage_proxy():
    m=metrics(snapshot(gates=[dict(number=1,body="https://x/1")],**{"ci.yml":[
        dict(id=1,status="completed",conclusion="failure",html_url="https://x/1"),
        dict(id=2,status="completed",conclusion="failure",html_url="https://x/2"),
        dict(id=3,status="completed",conclusion="cancelled",html_url="https://x/3")]}))
    assert m["unpaged_failure_proxy"].value == 50
    assert m["unpaged_failure_proxy"].n == 2


def test_dora():
    runs=[dict(id=i,created_at=f"2026-01-0{i}T00:00:00Z",head_sha="merge",
               conclusion="success" if i == 3 else "failure",
               updated_at=f"2026-01-0{i}T02:00:00Z") for i in range(1,4)]
    jobs={f"jobs:{i}":[dict(id=i,name="deploy",status="completed",conclusion=c,
                          completed_at=f"2026-01-0{i}T02:00:00Z")] for i,c in [(1,"failure"),(2,"failure")]}
    runs.extend([
        dict(id=4, created_at="2026-01-01T00:00:00Z", conclusion="failure"),
        dict(id=5, created_at="2026-01-01T00:00:00Z", conclusion="cancelled")])
    jobs["jobs:4"] = [dict(id=4, name="deploy", status="completed", conclusion="skipped",
                           completed_at="2026-01-01T01:00:00Z")]
    jobs["jobs:5"] = [dict(id=5, name="deploy", status="completed", conclusion="success",
                           completed_at="2026-01-01T01:00:00Z")]
    s = snapshot(changes=[change(prs=[1])],prs=[pr(merge_commit_sha="merge")],**{"pages.yml":runs,**jobs})
    m=metrics(s)
    assert m["deployment_frequency"].value == 1/3
    assert m["deployment_frequency"].n == 3
    assert m["deployment_lead_time"].value == 44
    assert m["restore_time"].value == 48
    assert [r["value"] for r in m["deployment_frequency"].series] == [0, 0, 1]
    assert all(m[name].available and "updated_at" in m[name].note for name in
               ("deployment_frequency", "deployment_lead_time", "restore_time"))
    s.github.sources["prs"].data[0]["merge_commit_sha"] = "different"
    assert metrics(s)["deployment_lead_time"].n == 0


def test_breach_to_intent():
    assert not metrics(snapshot())["breach_to_intent"].available


def test_findings_and_repeat_incidents():
    m=metrics(snapshot(changes=[change(origin="finding",outcome="merged"),
                               dict(slug="y",origin="finding",outcome="accepted")]))
    assert m["findings_to_fixes"].value == 100 and m["findings_to_fixes"].n == 1
    assert not m["repeat_incidents"].available


def test_codex_tokens():
    m=metrics(snapshot(jobs=[dict(id="x",usage=dict(input_tokens=100,cached_input_tokens=80,output_tokens=20,reasoning_output_tokens=5))]))
    assert m["total_tokens"].value == 120
    assert m["cached_input_tokens"].value == 80


def test_weekly_window():
    jobs=[dict(id=str(i),ended=f"2026-01-01T0{i}:00:00Z",rate_limits={"secondary":dict(window_minutes=10080,used_percent=p,resets_at=10)})
          for i,p in [(1,80),(2,5)]]
    m=metrics(snapshot(jobs=jobs))
    assert m["weekly_window"].value == 5
    assert m["weekly_window"].series[0]["value"] == 5
    assert m["weekly_window"].series[0]["n"] == 2


def test_supervisor_cost_and_turns():
    ticks=[dict(ts="2026-01-01T00:00:00Z",supervisor=dict(ran=ran,cost_usd=cost,turns=turns))
           for ran,cost,turns in [(True,0,1),(True,2,3),(False,100,100),(True,None,None)]]
    m=metrics(snapshot(ticks=ticks))
    assert m["supervisor_cost_usd"].value == 1
    assert m["supervisor_turns"].value == 2
    assert m["supervisor_cost_usd"].series[0]["value"] == 2


def test_wall_time():
    m=metrics(snapshot(changes=[change(prs=[1],outcome="merged",started="2026-01-01T00:00:00Z")],
                       prs=[pr()],jobs=[dict(id="x",change="x",duration_s=100)]))
    assert m["wall_time"].value == 6
    assert m["job_time"].value == 100


def test_invalid_closed_gate_is_not_open():
    s=snapshot(gates=[dict(number=1,created_at="2026-01-01T00:00:00Z",closed_at="invalid")])
    m=metrics(s)
    assert m["closed_gate_wait"].n == 0
    assert m["open_gate_age"].n == 0
    assert s.github.get("gates").warnings["invalid_timestamp"] == 1


def test_fractional_second_fix_counts_after_merge():
    s = snapshot(changes=[change(prs=[1], outcome="merged")], prs=[pr()],
                 jobs=[dict(id="fix", kind="fix", change="x", started="2026-01-01T06:00:00.5Z")])
    m = metrics(s)
    assert m["change_failure_rate"].value == 100
    assert m["post_merge_fixes"].value == 1


def test_frozen_state_totals():
    from pathlib import Path
    from lab_metrics.sources import read_changes, read_mistakes
    base = Path(__file__).parent / "fixtures/metrics/real"
    s = snapshot(jobs=[dict(id=f"fix-{i}", kind="fix", change="retired-product") for i in range(7)])
    s.changes = read_changes(base / "changes.yaml")
    s.mistakes = read_mistakes(base / "mistakes.jsonl")
    s.github.sources["prs"] = SourceResult(False, "offline")
    m = metrics(s)
    assert m["rework_cycles"].value == 17
    assert m["repeated_mistakes"].value == 1
    assert not m["plan_to_final_merge"].available
