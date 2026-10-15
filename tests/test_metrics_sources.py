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
