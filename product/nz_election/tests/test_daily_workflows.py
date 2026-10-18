"""Daily workflow mirrors the hourly isolation, artifact and lease gates."""
from product.nz_election.tests.test_workflows import workflow


def test_daily_schedule_and_dispatch():
    doc = workflow('nz-election-daily.yml')
    assert doc['name'] == 'NZ election daily'
    assert doc[True] == {'schedule': [{'cron': '43 15 * * *'}], 'workflow_dispatch': None}
    assert doc['permissions'] == {}
    assert doc['jobs']['refresh']['if'] == "github.ref == 'refs/heads/main'"


def test_daily_live_fetch_and_publication_contract():
    daily, hourly = [workflow('nz-election-' + name + '.yml') for name in ('daily', 'hourly')]
    # All isolation and upload gates stay identical to the fully checked hourly job.
    refresh = daily['jobs']['refresh']
    assert refresh['permissions'] == {'contents': 'read'}
    step = next(s for s in refresh['steps'] if s.get('id') == 'refresh')
    assert step['run'] == 'uv run product/nz_election/pipeline/daily_refresh.py --live --out _nz-election-data/product/nz_election/data'
    step.update(name='Refresh polls', run=next(s['run'] for s in hourly['jobs']['refresh']['steps'] if s.get('id') == 'refresh'))
    assert refresh == hourly['jobs']['refresh']
    publish = daily['jobs']['publish']
    assert publish['steps'][-1]['run'].endswith('publish.py --family daily --bundle _nz-election-bundle')
    publish['steps'][-1]['run'] = hourly['jobs']['publish']['steps'][-1]['run']
    assert publish == hourly['jobs']['publish']


def test_pages_daily_completion_guard():
    doc = workflow('pages.yml')
    assert doc[True]['workflow_run'] == {'workflows': ['NZ election hourly', 'NZ election daily'], 'types': ['completed'], 'branches': ['main']}
    assert 'conclusion' not in doc['jobs']['build']['if']
    assert 'head_repository.full_name == github.repository' in doc['jobs']['build']['if']
    assert doc['concurrency'] == {'group': 'pages', 'cancel-in-progress': False}
