"""Static output safety, honest failure states and preserved blog neighbours."""
import json
import pytest
from product.nz_election.pipeline.build import build, PREFIX, config
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline import export
from product.nz_election.pipeline.average import trend
from product.nz_election.pipeline.seats import project


def data(tmp_path):
    path = tmp_path / 'data'
    refresh(path, now='2026-10-17T01:00:00Z')
    return path


def rewrite(path, mutate):
    envs = export.validate_bundle(path)
    mutate(envs['polls']['data'])
    export.pair(path, 'polls', envs['polls'])
    averages = envs['averages']
    averages['data'] = trend(envs['polls']['data'], [a['date'] for a in averages['data']])
    averages['input_hashes']['polls.json'] = export.digest((path / 'polls.json').read_bytes())
    export.pair(path, 'averages', averages)
    seats = envs['seats']
    seats['data'] = project(averages['data'][-1])
    seats['input_hashes']['averages.json'] = export.digest((path / 'averages.json').read_bytes())
    export.pair(path, 'seats', seats)
    export.inventory(path, 'offline-verification', seats['code_sha'], '2026-10-17T01:00:00Z')


def test_registered_routes_and_prefix(tmp_path):
    out = build(data(tmp_path), tmp_path / 'output')
    for route in config('routes'):
        html = (out / route['path'] / 'index.html').read_text()
        from product.nz_election.pipeline.scripts import validate_scripts
        assert PREFIX in html and '<main ' in html and validate_scripts(html)
        assert 'Skip to content' in html
    expected = [r['path'] for r in config('routes')] + ['electorates/' + r['slug'] + '/' for r in config('electorates')]
    assert len(expected) == len(set(expected)) == 79
    assert {p.relative_to(out).as_posix() for p in out.rglob('index.html')} == {p + 'index.html' for p in expected}
    assert '26px' in (out / 'styles.css').read_text()


def test_no_data_first_build(tmp_path):
    out = build(tmp_path / 'absent', tmp_path / 'output')
    html = (out / 'index.html').read_text()
    assert 'id="home-seats"' not in html and '<section id="polls"' not in html
    assert 'class="strip"' not in html
    assert '2,851,211' in (out / 'methods/index.html').read_text()
    assert json.loads((out / 'build-manifest.json').read_text())['data']['data_sha'] is None


def test_incomplete_vector_withholds_seats(tmp_path):
    path = data(tmp_path)
    def remove(rows):
        max(rows, key=lambda p: p['fieldwork_end'])['shares']['nat'] = None
    rewrite(path, remove)
    out = build(path, tmp_path / 'output')
    html = (out / 'polls/index.html').read_text()
    assert 'class="strip"' not in html
    assert 'Incomplete party coverage' in (out / 'methods/index.html').read_text()
    assert 'Missing observations' not in html and 'How have the polls moved?' in html
    assert 'Missing observations' in (out / 'methods/index.html').read_text()


def test_source_html_escaped(tmp_path):
    path = data(tmp_path)
    def inject(rows):
        rows[0]['pollster'] = '<script>alert(1)</script>'
        rows[0]['reference_urls'] = ['javascript:alert(1)', 'https://example.invalid/?q="<bad>']
    rewrite(path, inject)
    site = build(path, tmp_path / 'output')
    html = (site / 'polls/index.html').read_text()
    assert '<script>' not in html and '&lt;script&gt;' in html
    assert 'href="javascript:' not in html
    html = (site / 'methods/index.html').read_text()
    assert '<script>' not in html and '&lt;script&gt;' in html
    assert 'href="javascript:' not in html and '&quot;&lt;bad&gt;' in html


def test_build_preserves_blog(tmp_path):
    site = tmp_path / 'site'
    site.mkdir()
    (site / 'index.html').write_text('blog home')
    (site / 'posts').mkdir()
    (site / 'posts/post.html').write_text('blog post')
    build(tmp_path / 'absent', site / 'nz-election')
    assert (site / 'index.html').read_text() == 'blog home'
    assert (site / 'posts/post.html').read_text() == 'blog post'
    build(tmp_path / 'absent', site / 'nz-election')
    assert (site / 'index.html').read_text() == 'blog home'


def test_failed_validation_preserves_deployment(tmp_path):
    path = data(tmp_path)
    out = build(path, tmp_path / 'output')
    before = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}
    (path / 'polls.json').write_text('{}')
    with pytest.raises(ValueError):
        build(path, out)
    assert before == {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}


def test_build_cli_records_actual_checkout_environment(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module('product.nz_election.pipeline.build')
    bundle = data(tmp_path)
    monkeypatch.setenv('GITHUB_SHA', 'c' * 40)
    monkeypatch.setenv('NZ_CODE_SHA', 'a' * 40)
    monkeypatch.setenv('NZ_DATA_SHA', 'b' * 40)
    monkeypatch.setenv('GITHUB_SERVER_URL', 'https://github.com')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'byronxlg/unattended')
    monkeypatch.setenv('GITHUB_RUN_ID', '123')
    out = tmp_path / 'output'
    monkeypatch.setattr('sys.argv', ['build.py', '--data', str(bundle), '--out', str(out)])
    module.main()
    manifest = json.loads((out / 'build-manifest.json').read_text())
    assert manifest['code_sha'] == manifest['data']['code_sha'] == 'a' * 40
    assert manifest['data']['data_sha'] == 'b' * 40
    assert manifest['data']['data_available'] is True
    assert manifest['data']['build_run_url'].endswith('/actions/runs/123')
