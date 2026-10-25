"""Party provenance and rendered credits keep source-specific meaning."""
from copy import deepcopy
from html import unescape
import json
import re

import pytest

from product.nz_election.pipeline import snapshots
from product.nz_election.pipeline.parties_page import page, ordered


@pytest.mark.parametrize('name', ['policy-links', 'party-list-tops'])
@pytest.mark.parametrize('licence', ['CC0', 'Public domain'])
def test_party_source_rejects_recognised_wrong_licence(tmp_path, monkeypatch, name, licence):
    data = json.loads((snapshots.SNAPSHOTS / (name + '.json')).read_text())
    data['records'][0]['licence'] = licence
    (tmp_path / (name + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    with pytest.raises(ValueError, match='licence'):
        snapshots.load_party_details(name)


@pytest.mark.parametrize('name', ['policy-links', 'party-list-tops'])
def test_party_source_requires_source_url(tmp_path, monkeypatch, name):
    data = json.loads((snapshots.SNAPSHOTS / (name + '.json')).read_text())
    del data['records'][0]['source_url']
    (tmp_path / (name + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    with pytest.raises(ValueError, match='Invalid party source'):
        snapshots.load_party_details(name)


@pytest.mark.parametrize('empty_fields', [(), ('author',), ('source_url',),
                                        ('author', 'source_url'), ('licence',),
                                        ('author', 'licence'), ('changes',)])
def test_rendered_party_credits_join_only_visible_parts(empty_fields):
    leaders = deepcopy(snapshots.load('leaders'))
    for leader in leaders:
        if leader.get('photo'):
            for field in empty_fields:
                leader['photo'][field] = ''
    html = page({}, '2026-10-22T07:00:00Z', {'leaders': leaders})
    captions = re.findall(r'<div class="source-note party-credit"[^>]*><p class="source-actions">(.*?)</p>', html)
    assert captions
    rendered_leaders = [leader for party in ordered([]) for leader in leaders
                        if leader.get('party_id') == party]
    for leader, caption in zip(rendered_leaders, captions, strict=True):
        text = unescape(re.sub(r'<[^>]+>', '', caption))
        assert not text.startswith('. ')
        assert not re.search(r'(?:^|\s)/\s*(?:$|\.)|^\s*/', text)
        photo = leader.get('photo')
        if photo:
            attribution = ' '.join(photo[k].rstrip('.') + '.' for k in ('author', 'licence') if photo[k])
            assert text.strip() == ' '.join(part for part in (attribution, photo['changes']) if part)
