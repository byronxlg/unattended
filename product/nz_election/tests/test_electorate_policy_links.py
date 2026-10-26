"""Confirmed Policy index destinations render in question order, with silent absence."""
from copy import deepcopy
import json

import pytest

from product.nz_election.pipeline import snapshots, snapshot_views
from product.nz_election.pipeline.build import config
from product.nz_election.pipeline.content_checks import Tree
from product.nz_election.pipeline.electorate_pages import detail
from product.nz_election.tests.test_home import populated  # noqa: F401


def test_registered_policy_links_on_populated_pages(populated, monkeypatch):
    _, site = populated
    records = {r['electorate_slug']: r for r in snapshots.load('policy-links') if 'electorate_slug' in r}
    assert set(records) == {r['slug'] for r in config('electorates')}
    for slug, record in records.items():
        html = (site / 'electorates' / slug / 'index.html').read_text()
        sections = [n for n in Tree(html).nodes if n.tag == 'section']
        candidates = next(i for i, n in enumerate(sections) if n.attrs.get('class') == 'race-candidates')
        policy = sections[candidates + 1]
        assert policy.attrs.get('class') == 'electorate-policy'
        assert any(n.tag == 'a' and n.attrs.get('href') == record['url'] for n in policy.children[0].children if not isinstance(n, str))
        assert html.index('class="race-candidates"') < html.index('class="electorate-policy"')
        if 'Who won last time?' in html:
            assert html.index('class="electorate-policy"') < html.index('Who won last time?')
    original = snapshot_views.load
    monkeypatch.setattr(snapshot_views, 'load', lambda name: [r for r in original(name) if r.get('electorate_slug') != 'te-tai-tonga'] if name == 'policy-links' else original(name))
    row = next(r for r in config('electorates') if r['slug'] == 'te-tai-tonga')
    html = detail(row, {})
    assert 'electorate-policy' not in html and 'Policy.nz' not in html
    assert 'not available' not in html.lower()


def test_confirmed_electorate_policy_contract(tmp_path, monkeypatch):
    data = json.loads((snapshots.SNAPSHOTS / 'policy-links.json').read_text())
    record = next(r for r in data['records'] if r.get('electorate_slug') == 'auckland-central')
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    def write(records):
        (tmp_path / 'policy-links.json').write_text(json.dumps(dict(data, records=records)))
    write([record])
    assert snapshots.load('policy-links') == [record]
    write([record, record])
    with pytest.raises(ValueError):
        snapshots.load('policy-links')
    for field, values in {
        'electorate_slug': ['', None, [], {}, 1, 1.5, 10**100, 'unknown-seat', 'Ａuckland-central'],
        'url': ['', None, [], 1, 1.5, 10**100, 'https://example.com/2026/auckland-central-electorate/candidates/a', record['url'].replace('policy.nz', 'policy.nz.example.com'), record['url'].replace('auckland-central', 'nelson'), record['url']+'?text=yes', record['url']+'#text', record['url']+'/extra'],
        'source_url': ['https://example.com/', 'https://policy.nz.example.com/'],
    }.items():
        for value in values:
            bad = deepcopy(record); bad[field] = value
            write([bad])
            with pytest.raises(ValueError):
                snapshots.load('policy-links')
