"""The pre-freeze build hands over without another publication."""
import subprocess
from pathlib import Path

import pytest

from product.nz_election.pipeline.build import build
from product.nz_election.tests.test_home import populated  # noqa: F401


@pytest.mark.parametrize('clock', ['2026-11-07T05:59:00Z', '2026-11-07T06:01:00Z'])
def test_empty_night_build(clock, tmp_path, monkeypatch):
    from product.nz_election.pipeline import deployment_guard
    # Exercise rendering inside the freeze without authorizing publication.
    monkeypatch.setattr(deployment_guard, 'require_publication_allowed', lambda _: None)
    from product.nz_election.pipeline.refresh import refresh
    data = tmp_path / 'data'
    refresh(data, now=clock, end_date='2026-07-18')
    built = build(data, tmp_path / 'site/nz-election', built=clock)
    html = (built / 'index.html').read_text()
    if '05:59' in clock:
        assert 'id="seats"' in html
        assert 'home-live.mjs' in html
    else:
        assert 'id="night-summary"' in html and 'id="seats"' not in html
        assert 'Voting closed on 7 November at 7pm.' in html
        assert 'advance voting from' not in html
        assert 'Polls have closed and counting is under way.' in html
        assert 'https://www.electionresults.govt.nz/' in html
    from product.nz_election.tools.check_visible_text import check_absent_text
    check_absent_text(html)


@pytest.mark.parametrize('case', ['absent', 'zero', 'complete', 'recovery'])
def test_browser_handover(case):
    result = subprocess.run(['uv', 'run', '--with', 'playwright', 'python', '-m',
                             'product.nz_election.tests.home_handover_browser', case],
                            cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('case', ['absent', 'zero', 'complete', 'recovery'])
def test_dom_handover(case, tmp_path):
    from product.nz_election.pipeline.build import PRODUCT
    from product.nz_election.pipeline.scripts import home_client
    client = tmp_path / 'home-live.mjs'
    client.write_text(home_client(PRODUCT / 'web'))
    script = Path(__file__).with_name('home_handover_dom.mjs')
    result = subprocess.run(['node', str(script), case, client.as_uri()], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_live_package_reuses_home_summary(tmp_path):
    import json
    from product.nz_election.pipeline import night, night_live
    from product.nz_election.pipeline.home import night_summary
    from product.nz_election.pipeline.night_page import live_package
    from product.nz_election.tests.night_live_cases import Clock, captures
    clock = Clock()
    captured = night_live.cycle(acquire=captures().__getitem__, now=clock.now)
    night.prepare(tmp_path, night_live.loaded(captured), 'offline-verification', 'a'*40, captured['retrieved_at'])
    envs = {p.relative_to(tmp_path).as_posix()[:-5]: json.loads(p.read_text()) for p in tmp_path.rglob('*.json')}
    pack = live_package(envs, now=clock.now())
    assert pack['home_html'] == night_summary(envs, captured['retrieved_at'])
    assert '0 national seats reported.' in pack['home_html']
    assert 'House: 0 seats.' in pack['home_html']
    assert '1 for a majority' not in pack['home_html']


def test_after_stop_retains_past_tense():
    from product.nz_election.pipeline.home import page
    from product.nz_election.pipeline.build import home_presentation
    clock = '2026-11-15T00:00:00Z'
    html = page({}, clock, home_presentation({}, clock))
    assert 'New Zealand voted on 7 November' in html
    assert 'Voting closed on 7 November' in html
    assert 'home-live.mjs' not in html
    assert 'counting is under way' not in html
    assert 'id="night-summary"' in html and 'Live updates ended.' in html
    from product.nz_election.tools.check_visible_text import check_absent_text
    check_absent_text(html)


@pytest.mark.parametrize('cutoff', ['2026-11-07T05:00:00Z', '2026-11-07T07:00:00Z'])
def test_shared_cutoff_moves_hero_and_dates(monkeypatch, cutoff, populated):
    from datetime import datetime
    from product.nz_election.pipeline import sunsets
    from product.nz_election.pipeline.build import home_presentation
    from product.nz_election.pipeline.home import page
    monkeypatch.setattr(sunsets, 'END', datetime.fromisoformat(cutoff))
    clock = '2026-11-07T05:30:00Z' if 'T05:' in cutoff else '2026-11-07T06:30:00Z'
    envs, _ = populated
    envs = {key: value for key, value in envs.items() if not key.startswith('night/')}
    html = page(envs, clock, home_presentation(envs, '2026-10-17T01:00:00Z'))
    closed = sunsets.post_election(clock)
    assert ('id="night-summary"' in html) == closed
    assert ('Voting closed on 7 November' in html) == closed
    assert ('id="seats"' in html) == (not closed)
    from product.nz_election.pipeline.build import PRODUCT
    from product.nz_election.pipeline.scripts import home_client
    assert f"Date.parse('{sunsets.END.isoformat()}')" in home_client(PRODUCT / 'web')


@pytest.mark.parametrize('case', ['cached-after-stop', 'waiting-after-stop'])
def test_retirement_browser(case):
    test_browser_handover(case)


@pytest.mark.parametrize('case', ['cached-after-stop', 'waiting-after-stop'])
def test_retirement_dom(case, tmp_path):
    test_dom_handover(case, tmp_path)
