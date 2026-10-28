"""Release acceptance uses published bytes, never a freshly substituted capture."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from product.nz_election.pipeline import advance, export, verify
from product.nz_election.pipeline.build import build
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.tools import harden

NOW = '2026-10-29T01:00:00Z'


@pytest.fixture
def release(tmp_path, monkeypatch):
    data = tmp_path / 'data'
    daily_refresh(data, loaders={'advance': advance.load}, now=NOW)
    site = build(data, tmp_path / 'site/nz-election', built=NOW)
    # The existing fixture smoke check is independent of release acceptance.
    monkeypatch.setattr(verify, 'verify_advance', lambda *a, **kw: None)
    return data, site


def accept(data, site=None, check='advance'):
    args = [check, '--require', 'advance', '--data', str(data)]
    if site is not None:
        args += ['--site', str(site)]
    verify.cli(args)


def rewrite(data, env):
    export.pair(data, 'advance-voting', env)
    export.inventory(data, 'offline-verification', 'test', NOW)


def test_matching_release_and_both_pages(release, capsys):
    data, site = release
    accept(data, site.parent)
    assert 'PASS advance' in capsys.readouterr().out
    accept(data)
    verify.cli(['advance', '--require', 'advance', '--site', str(site)])


@pytest.mark.parametrize('check', ['advance', 'all'])
def test_omitted_publication_fails(release, check):
    data, _ = release
    for ext in ('json', 'csv'):
        (data / ('advance-voting.' + ext)).unlink()
    export.inventory(data, 'offline-verification', 'test', NOW)
    with pytest.raises(SystemExit, match=f'^FAIL {check}: ADVANCE_NOT_PUBLISHED$'):
        accept(data, check=check)


def test_requires_release_evidence():
    with pytest.raises(SystemExit, match='ADVANCE_NOT_PUBLISHED$'):
        verify.cli(['advance', '--require', 'advance'])


def test_older_registered_capture_fails(release, tmp_path, monkeypatch):
    data, _ = release
    registry = tmp_path / 'registry'
    registry.mkdir()
    original = deepcopy(next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries']
                             if e.get('advance', {}).get('year') == 2026))
    raw = (advance.ROOT / original['path']).read_bytes()
    original['path'] = 'old.csv'
    newer_raw = raw + b'28 October,"123,456"\n'
    newer = dict(original, path='new.csv', captured_at=NOW, sha256=export.digest(newer_raw), bytes=len(newer_raw))
    (registry / 'old.csv').write_bytes(raw)
    (registry / 'new.csv').write_bytes(newer_raw)
    (registry / 'manifest.json').write_text(json.dumps({'entries': [newer, original]}))
    monkeypatch.setattr(advance, 'ROOT', registry)
    with pytest.raises(SystemExit, match='ADVANCE_STALE$'):
        accept(data)
    daily_refresh(data, loaders={'advance': advance.load}, now=NOW)
    accept(data)


@pytest.mark.parametrize('route', ['index.html', 'vote/index.html'])
@pytest.mark.parametrize('mutation', ['count', 'date', 'hidden', 'missing'])
def test_each_rendered_page_is_checked(release, route, mutation):
    data, site = release
    path = site / route
    html = path.read_text()
    sentence = '175,748 advance votes reported through 27 October.'
    replacement = {'count': sentence.replace('175,748', '175,747'),
                   'date': sentence.replace('27 October', '26 October'),
                   'hidden': '<span hidden>' + sentence + '</span>', 'missing': ''}[mutation]
    assert sentence in html
    path.write_text(html.replace(sentence, replacement))
    code = 'ADVANCE_NOT_PUBLISHED' if mutation in {'hidden', 'missing'} else 'ADVANCE_RENDER_MISMATCH'
    with pytest.raises(SystemExit, match=code + '$'):
        accept(data, site)


def test_site_bundle_also_must_match(release):
    data, site = release
    env = export.validate_bundle(site / 'data')['advance-voting']
    env['data'].pop()
    rewrite(site / 'data', env)
    with pytest.raises(SystemExit, match='ADVANCE_STALE$'):
        accept(data, site)


def test_gap_is_distinct_and_suppressed(release, tmp_path, monkeypatch):
    data, _ = release
    registry = tmp_path / 'gap-registry'
    registry.mkdir()
    entry = deepcopy(next(e for e in json.loads((advance.ROOT / 'manifest.json').read_text())['entries']
                          if e.get('advance', {}).get('year') == 2026))
    raw = b'Date,2026 General Election\n26 October,69034\n28 October,123456\n'
    entry.update(path='gap.csv', captured_at=NOW, sha256=export.digest(raw), bytes=len(raw))
    (registry / 'gap.csv').write_bytes(raw)
    (registry / 'manifest.json').write_text(json.dumps({'entries': [entry]}))
    monkeypatch.setattr(advance, 'ROOT', registry)
    daily_refresh(data, loaders={'advance': advance.load}, now=NOW)
    site = build(data, tmp_path / 'gap-site', built=NOW)
    for route in ('index.html', 'vote/index.html'):
        assert 'advance votes reported through' not in (site / route).read_text()
    for location in (None, site):
        with pytest.raises(SystemExit, match='ADVANCE_GAP$'):
            accept(data, location)
    path = site / 'index.html'
    path.write_text(path.read_text().replace('</main>', '<p>69,034 advance votes reported through 26 October.</p></main>'))
    with pytest.raises(SystemExit, match='ADVANCE_RENDER_MISMATCH$'):
        accept(data, site)


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-private-content'])
def test_malformed_bundle_has_fixed_code(release, bad):
    data, _ = release
    path = data / 'advance-voting.json'
    path.write_text(json.dumps(bad))
    with pytest.raises(SystemExit, match='^FAIL advance: ADVANCE_INVALID_BUNDLE$'):
        accept(data)


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-private-content'])
def test_malformed_count_has_fixed_code(release, bad):
    data, _ = release
    path = data / 'advance-voting.json'
    env = json.loads(path.read_text())
    env['data'][-1]['cumulative'] = bad
    path.write_text(json.dumps(env))
    with pytest.raises(SystemExit, match='^FAIL advance: ADVANCE_INVALID_BUNDLE$'):
        accept(data)


def test_harden_forwards_requirement_and_rejects_acceptance_failure(capsys):
    calls = []
    def runner(cmd, **kw):
        calls.append(cmd)
        if 'all' in cmd:
            assert cmd[-2:] == ['--require', 'advance']
            return SimpleNamespace(stdout='FAIL all: ADVANCE_STALE\n', returncode=1)
        return SimpleNamespace(stdout='', returncode=0)
    assert harden.main(['--data', 'bundle', '--site', 'site', '--require', 'advance', '--history'], runner=runner) == 1
    assert capsys.readouterr().out.splitlines()[-1] == 'FAIL harden: verify all'
    assert any('all' in cmd for cmd in calls)


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-private-content'])
def test_malformed_registry_has_fixed_code(release, tmp_path, monkeypatch, bad):
    data, _ = release
    registry = tmp_path / 'invalid-registry'
    registry.mkdir()
    (registry / 'manifest.json').write_text(json.dumps(bad))
    monkeypatch.setattr(advance, 'ROOT', registry)
    with pytest.raises(SystemExit, match='^FAIL advance: ADVANCE_CAPTURE_INVALID$'):
        accept(data)


@pytest.mark.parametrize('route', ['index.html', 'vote/index.html'])
@pytest.mark.parametrize('attributes', [
    'hidden', 'aria-hidden="true"', 'style="display:none"',
    'style="visibility:hidden"', 'style="color:red; DISPLAY : NONE !important;"',
    'style="visibility:/* hidden from readers */hidden"',
])
@pytest.mark.parametrize('ancestor', [False, True], ids=['paragraph', 'ancestor'])
def test_hidden_advance_sentence_is_not_published(release, route, attributes, ancestor):
    data, site = release
    path = site / route
    html = path.read_text()
    start = html.index('<p>175,748 advance votes reported through 27 October.')
    end = html.index('</p>', start) + len('</p>')
    paragraph = html[start:end]
    replacement = ('<div ' + attributes + '><div>' + paragraph + '</div></div>' if ancestor else
                   paragraph.replace('<p>', '<p ' + attributes + '>', 1))
    path.write_text(html[:start] + replacement + html[end:])
    with pytest.raises(SystemExit, match='^FAIL advance: ADVANCE_NOT_PUBLISHED$'):
        accept(data, site)


@pytest.mark.parametrize('route', ['index.html', 'vote/index.html'])
def test_visible_advance_sentence_with_inline_style_is_accepted(release, route, capsys):
    data, site = release
    path = site / route
    html = path.read_text()
    path.write_text(html.replace('<p>175,748', '<p style="display:block; visibility:visible">175,748'))
    accept(data, site)
    assert 'PASS advance' in capsys.readouterr().out
