"""Reject malformed provenance without changing the committed facts."""
import json

import pytest

from product.nz_election.pipeline import snapshots


@pytest.mark.parametrize(('name', 'field', 'value'), [
    ('party-list-tops', 'source_url', 'https://example.com/list.pdf'),
    ('party-list-tops', 'source_url', 'http://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf'),
    ('party-list-tops', 'source_url', 'https://vote.nz/not-the-party-list.html'),
    ('policy-links', 'source_url', 'https://example.com/parties'),
    ('policy-links', 'source_url', 'https://policy.nz.example.com/parties'),
    ('party-list-tops', 'licence', 'Invented licence'),
    ('policy-links', 'licence', 'Invented licence'),
    ('party-list-tops', 'source_locator', None),
    ('party-list-tops', 'source_locator', '  '),
    ('policy-links', 'policy_text', 'Copied policy text'),
    ('policy-links', 'url', 'https://policy.nz/2026/party-vote/parties/'),
    ('policy-links', 'url', 'https://policy.nz/2026/party-vote/parties/national-party/policies'),
    ('policy-links', 'url', 'https://policy.nz/2026/party-vote/parties/national-party?copy=text'),
    ('policy-links', 'url', 'https://policy.nz/2026/party-vote/parties/national-party#policies'),
    ('policy-links', 'url', 'https://policy.nz/2026/party-vote/parties/%2e%2e'),
], ids=['list-foreign-origin', 'list-http', 'list-not-pdf', 'policy-foreign-origin',
        'policy-lookalike-host', 'list-invented-licence', 'policy-invented-licence',
        'null-locator', 'blank-locator', 'copied-policy-text', 'empty-slug',
        'slug-extra-path', 'slug-query', 'slug-fragment', 'slug-encoded-traversal'])
def test_party_provenance_rejected(tmp_path, monkeypatch, name, field, value):
    data = json.loads((snapshots.SNAPSHOTS / (name + '.json')).read_text())
    data['records'][0][field] = value
    (tmp_path / (name + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    with pytest.raises(ValueError):
        snapshots.load(name)


def test_list_locator_required(tmp_path, monkeypatch):
    name = 'party-list-tops'
    data = json.loads((snapshots.SNAPSHOTS / (name + '.json')).read_text())
    del data['records'][0]['source_locator']
    (tmp_path / (name + '.json')).write_text(json.dumps(data))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    with pytest.raises(ValueError):
        snapshots.load(name)
