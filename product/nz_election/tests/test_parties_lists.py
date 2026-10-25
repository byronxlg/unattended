"""Verified list sizes, provenance and field-level absence."""
from copy import deepcopy
import json

import pytest

from product.nz_election.pipeline import snapshots
from product.nz_election.pipeline.parties_page import page


def record():
    return dict(party_id='nat', source_url='https://vote.nz/assets/pagecomponent-file-files/Party-lists-for-the-2026-General-Election.pdf',
                source_locator='Page 2, National Party', retrieved_at='2026-10-26T00:00:00Z',
                licence='Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.',
                completeness='confirmed', list_size=72,
                list_size_source_url='https://elections.nz/media-and-news/2026/candidate-and-party-lists-released',
                candidates=[dict(rank=i, name=f'Candidate {i}', source_name=f'CANDIDATE, {i}') for i in range(1, 6)])


def validate(tmp_path, monkeypatch, row):
    data = dict(schema='party-list-tops-v1', retrieved_at=row['retrieved_at'], records=[row])
    (tmp_path / 'party-list-tops.json').write_text(json.dumps(data))
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    return snapshots.load_party_details('party-list-tops')


@pytest.mark.parametrize('value', [None, '', 0, -1, True, 3.5, 10**100, '72', [], {}, '７２'])
def test_invalid_list_size(tmp_path, monkeypatch, value):
    row = record()
    row['list_size'] = value
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)


@pytest.mark.parametrize('field', ['source_url', 'list_size_source_url'])
@pytest.mark.parametrize('value', [None, '', 'https://example.com/list.pdf',
                                   'https://elections.nz.example.com/list.pdf'])
def test_total_requires_ec_sources(tmp_path, monkeypatch, field, value):
    row = record()
    if value is None:
        del row[field]
    else:
        row[field] = value
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)


@pytest.mark.parametrize('ranks,total', [([1, 2, 3, 4, 5], 4), ([1, 1], 72), ([1, 3], 72)])
def test_duplicate_out_of_order_and_excess_ranks(tmp_path, monkeypatch, ranks, total):
    row = record()
    row.update(completeness='partial', list_size=total)
    row['candidates'] = [dict(rank=r, name='Name', source_name='NAME') for r in ranks]
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)


def test_confirmed_list_requires_all_opening_ranks(tmp_path, monkeypatch):
    row = record()
    row['candidates'].pop()
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)


def test_partial_record_keeps_verified_fields(tmp_path, monkeypatch):
    row = record()
    row.update(completeness='partial', candidates=row['candidates'][:1])
    del row['list_size']
    del row['list_size_source_url']
    assert validate(tmp_path, monkeypatch, row) == [row]


def test_list_size_and_five_names_render_with_absent_fields_omitted():
    row = record()
    html = page({}, '2026-10-26T00:00:00Z', {'party-list-tops': [row]})
    assert '72 list candidates' in html
    assert 'Top five list candidates' in html
    assert all(f'<li value="{i}">Candidate {i}</li>' in html for i in range(1, 6))
    partial = deepcopy(row)
    del partial['list_size']
    partial['completeness'] = 'partial'
    html = page({}, '2026-10-26T00:00:00Z', {'party-list-tops': [partial]})
    assert '72 list candidates' not in html
    partial['candidates'] = []
    html = page({}, '2026-10-26T00:00:00Z', {'party-list-tops': [partial]})
    assert 'party-candidates' not in html
    assert 'not available' not in html.lower()


def test_published_sizes_and_short_lists():
    rows = snapshots.load_party_details('party-list-tops')
    assert len(rows) == 17
    assert sum(r['list_size'] for r in rows) == 443
    by_id = {r['party_id']: r for r in rows if 'party_id' in r}
    assert {p: r['list_size'] for p, r in by_id.items()} == dict(nat=72, lab=71, grn=55, act=46, nzf=50, opp=40, tpm=1)
    assert all(len(r['candidates']) == min(5, r['list_size']) for r in rows)
    assert by_id['tpm']['candidates'] == [dict(rank=1, name='Lance Norman', source_name='NORMAN, Lance')]
    html = page({}, '2026-10-26T00:00:00Z', {'party-list-tops': [by_id['tpm']]})
    assert '1 list candidate</strong>' in html
    assert 'Top five' not in html


def test_partial_record_cannot_carry_foreign_total_source(tmp_path, monkeypatch):
    row = record()
    del row['list_size']
    row.update(completeness='partial', list_size_source_url='https://example.com/list')
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)


def test_partial_count_without_names_validates_then_renders(tmp_path, monkeypatch):
    row = record()
    row.update(completeness='partial', candidates=[])
    rows = validate(tmp_path, monkeypatch, row)
    html = page({}, row['retrieved_at'], {'party-list-tops': rows})
    assert '72 list candidates' in html
    assert '<ol>' not in html
    assert 'Top five' not in html and 'Top of the party list' not in html
    assert 'not available' not in html.lower()


def test_list_count_describes_recorded_source_note(tmp_path, monkeypatch):
    import re
    from product.nz_election.tests.design_checks import Document, provenance

    row = record()
    rows = validate(tmp_path, monkeypatch, row)
    html = page({}, row['retrieved_at'], {'party-list-tops': rows})
    count = re.search(r'<p aria-describedby="([^"]+)"><strong>72 list candidates</strong></p>', html)
    assert count is not None
    note = re.search(r'<div class="source-note" id="' + re.escape(count[1]) + r'">(.*?)</div>', html)
    assert note is not None
    doc = Document(note[1])
    assert any(tag == 'p' and attrs.get('class') == 'source-actions' for tag, attrs in doc.nodes)
    assert any(tag == 'a' and attrs.get('href') == row['list_size_source_url'] for tag, attrs in doc.nodes)
    assert row['licence'] in note[1]
    assert f'<time datetime="{row["retrieved_at"]}">' in note[1]
    assert 'Retrieved' in note[1] and '26 October 2026' in note[1]
    provenance(html)


@pytest.mark.parametrize('ranks,total', [([], 72), ([1, 2, 3, 4], 72),
                                        ([1, 2, 3, 4, 4], 72),
                                        ([1, 2, 3, 4, 6], 5)])
def test_confirmed_rank_guards_remain_strict(tmp_path, monkeypatch, ranks, total):
    row = record()
    row['list_size'] = total
    row['candidates'] = [dict(rank=r, name='Name', source_name='NAME') for r in ranks]
    with pytest.raises(ValueError):
        validate(tmp_path, monkeypatch, row)
