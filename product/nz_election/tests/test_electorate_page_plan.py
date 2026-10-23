"""Accepted question order, reconciled identities and absent-block contracts."""
from copy import deepcopy
from html import escape
import pytest
from product.nz_election.pipeline.build import config
from product.nz_election.pipeline.electorate_pages import detail, previous_result
from product.nz_election.pipeline.electorate_locator import locator, LOCATOR_BYTE_CAP
from product.nz_election.pipeline import snapshot_views, snapshots
from product.nz_election.tests.design_checks import provenance


def seat(slug='wellington-north'):
    return next(r for r in config('electorates') if r['slug'] == slug)


def test_first_screen_order_and_all_locators():
    for row in config('electorates'):
        html = detail(row, {})
        assert html.index('class="race-cards"') < html.index('Check your enrolled electorate at vote.nz') < html.index('class="electorate-locator"')
        graphic = locator(row)
        assert graphic in html and len(graphic.encode()) < LOCATOR_BYTE_CAP == 24000
        assert f'data-electorate="{row["slug"]}"' in graphic
        assert '2025 locator, not a legal boundary. Stats NZ, CC BY 4.0.' in html
        assert all(x not in html for x in ('Local polls', '<h2>Enrolment', 'class="tile-map"'))
        provenance(html)


def test_reconciled_display_names_ranks_order_and_only_explicit_incumbents():
    for row in config('electorates'):
        html = detail(row, {})
        rec = next(r for r in snapshot_views.load('candidate-reconciliation-2026') if r['electorate_slug'] == row['slug'])
        originals = {(c['name'], c['party']): c for c in snapshot_views.load('candidates-2026') if c['electorate_slug'] == row['slug']}
        candidates = rec['matched'] + rec['added_by_ec']
        assert html.count('<li style="--party:') == len(candidates)
        for c in candidates:
            assert '<strong>' + escape(c['snapshot_name']) + '</strong>' in html
            if 'list_rank' in c:
                assert f'List {c["list_rank"]}' in html
        assert html.count('class="incumbent"') == sum(bool(originals.get((c['snapshot_name'], c['snapshot_party']), {}).get('sitting_electorate_mp')) for c in candidates)
        from product.nz_election.pipeline.content_checks import Tree
        cards = html.split('<ul class="race-cards"', 1)[1].split('</ul>', 1)[0]
        names = [n.text for n in Tree(cards).nodes if n.tag == 'strong']
        assert names == [c['snapshot_name'] for c in candidates]
    assert '<strong>Michael Appleby</strong>' in detail(seat(), {})
    assert 'APPLEBY, Michael' not in detail(seat(), {})
    assert 'Josh Harford' in detail(seat(), {}) and 'HARFORD, Joshua' not in detail(seat(), {})


def test_policy_link_only_when_present(monkeypatch):
    original = snapshot_views.load
    assert 'electorate-policy' not in detail(seat(), {})
    monkeypatch.setattr(snapshot_views, 'load', lambda n: [{'electorate_slug': 'wellington-north', 'url': 'https://policy.nz/2026/electorate-vote/wellington-north'}] if n == 'policy-links' else original(n))
    html = detail(seat(), {})
    assert html.index('class="locator-card"') < html.index('class="electorate-policy"')
    assert 'https://policy.nz/2026/electorate-vote/wellington-north' in html
    assert 'electorate-policy' not in detail(seat('te-tai-tonga'), {})


def test_no_comparable_candidate_record_drops_entire_result():
    row = seat()
    for votes in (None, [], [{'name': 'A', 'party': 'Independent', 'votes': 3}]):
        envs = {'baseline-2023': {'data': [{'old_electorate_id': row['baseline_ids'][0], 'old_name': 'Wellington Central', 'candidate_votes': votes, 'party_votes': [{'votes': 100}]}], 'source': []}}
        assert previous_result(row, envs, None) == ''
    assert previous_result(dict(row, baseline_ids=[]), {}, None) == ''


def test_port_waikato_bars_use_snapshot_even_without_baseline():
    html = detail(seat('port-waikato'), {})
    votes = snapshot_views.load('port-waikato-2023')
    ranked = sorted(votes, key=lambda v: -v['votes'])
    assert 'by-election' in html and 'class="result-bars"' in html
    assert f'{ranked[0]["votes"]-ranked[1]["votes"]:,}</strong> votes' in html
    for v in votes:
        assert f'{v["votes"]:,} votes' in html


def live_env():
    return {'night/index': {'data': [{'id': 'live', 'reference_path': 'night/references/current.json', 'snapshot_paths': ['night/live/current.json']}]},
            'night/references/current': {'data': [{'electorates': {'59': {'electorate_name': 'Wellington North'}}, 'candidates': {'1': {'candidate_name': 'Test leader'}, '2': {'candidate_name': 'Test runner'}}}]},
            'night/live/current': {'data': [{'leaders': {'59': {'leader': '1', 'margin': 123, 'status': 'provisional', 'statistics': {'total_voting_places_counted': 4, 'total_voting_places': 12}}}, 'source_updated_local': '2026-11-07T20:00:00'}]}}


def test_current_night_answer_promotes_above_candidates():
    envs = live_env()
    html = detail(seat(), envs, '2026-11-07T07:00:00Z')
    assert html.index('Who is leading here now?') < html.index('Standing in 2026')
    assert 'Test leader' in html and 'Margin: 123 votes' in html
    assert '4 of 12 voting places counted' in html and 'Provisional leader' in html
    provenance(html)
    assert 'electorate-night' in detail(seat(), envs, '2026-11-07T06:00:00+00:00')
    assert 'electorate-night' not in detail(seat(), envs, '2026-11-07T05:59:59Z')
    assert 'electorate-night' not in detail(seat('te-tai-tonga'), envs, '2026-11-07T07:00:00Z')
    envs['night/index']['data'][0]['id'] = '2023'
    assert 'electorate-night' not in detail(seat(), envs, '2026-11-07T07:00:00Z')


def test_night_absent_and_tied_counts():
    envs = live_env()
    item = envs['night/live/current']['data'][0]['leaders']['59']
    item.update(status='not yet reported', leader=None, margin=None)
    assert 'electorate-night' not in detail(seat(), envs)
    item.update(status='final', tied_candidates=['1', '2'], margin=0)
    html = detail(seat(), envs)
    assert 'Tied: Test leader, Test runner' in html and 'Margin: 0 votes' in html
    assert 'Final source count; leader provisional' in html


def test_electorate_policy_snapshot_contract(tmp_path, monkeypatch):
    import json
    original = snapshots.load('policy-links')[0]
    record = {k: v for k, v in original.items() if k != 'party_id'}
    record.update(electorate_slug='wellington-north', url='https://policy.nz/2026/electorate-vote/wellington-north')
    path = tmp_path / 'policy-links.json'
    monkeypatch.setattr(snapshots, 'SNAPSHOTS', tmp_path)
    def write(value):
        path.write_text(json.dumps(dict(schema='policy-links-v1', retrieved_at=record['retrieved_at'], records=[value])))
    write(record)
    assert snapshots.load('policy-links') == [record]
    for invalid in [dict(original, electorate_slug=None), dict(record, party_id='nat')]:
        write(invalid)
        with pytest.raises(ValueError):
            snapshots.load('policy-links')
    for field, values in [('electorate_slug', ['', None, 0, 1.5, 10**100, [], {}, 'Wellington North', 'ｗellington-north']), ('url', ['', None, 0, [], 'https://policy.nz/2026/electorate-vote/nelson', 'https://example.com/'])]:
        for value in values:
            bad = deepcopy(record)
            bad[field] = value
            write(bad)
            with pytest.raises(ValueError):
                snapshots.load('policy-links')


def test_no_repeated_adjacent_electorate_provenance():
    from product.nz_election.pipeline.content_checks import Tree, check_sources
    for row in config('electorates'):
        html = detail(row, {})
        tree = Tree(html)
        for parent in tree.nodes:
            children = [n for n in parent.children if not isinstance(n, str)]
            for left, right in zip(children, children[1:]):
                if all('source-note' in n.attrs.get('class', '').split() for n in (left, right)):
                    assert ' '.join(left.text.split()) != ' '.join(right.text.split()), 'REPEATED_ADJACENT_PROVENANCE'
        assert html.count('Data to 20 October 2026.') == 1
        check_sources(html)
        provenance(html)


def test_methods_describe_current_detail_graphic_and_names():
    html = snapshot_views.sources({})
    assert 'squares on detail pages' not in html
    assert 'Electorate detail pages use the simplified Stats NZ 2025 boundary locators' in html
    assert 'candidate cards display the reconciled snapshot names' in html
    assert 'href="#home-boundaries-2025"' in html


from product.nz_election.tests.test_home import populated  # noqa: F401


def assert_readable_person_names(html):
    import re
    from product.nz_election.pipeline.content_checks import Tree
    names = [n.text for n in Tree(html).nodes if n.tag == 'strong'
             or 'local-margin' in n.attrs.get('class', '').split()]
    assert names
    for name in names:
        assert not re.search(r"\b[A-ZĀĒĪŌŪ][A-ZĀĒĪŌŪ'’-]*,\s", name), 'EC_SHEET_PERSON_NAME: ' + name


def test_no_ec_sheet_person_names_on_electorate_pages(populated):
    _, site = populated
    pages = list((site / 'electorates').glob('*/index.html'))
    assert len(pages) == 71
    for path in pages:
        assert_readable_person_names(path.read_text())
    wellington = (site / 'electorates/wellington-north/index.html').read_text()
    assert 'Tamatha Paul won by' in wellington
    assert '<strong>Tamatha Paul</strong>' in wellington
    port = (site / 'electorates/port-waikato/index.html').read_text()
    assert 'Andrew Bayly won by' in port


@pytest.mark.parametrize(('source', 'expected'), [
    ('PAUL, Tamatha-Kaye Erin', 'Tamatha-Kaye Erin Paul'),
    ('TE WHĀNAU-SMITH, Hēmi-James', 'Hēmi-James Te Whānau-Smith'),
    ("O’NEILL, Mary-Anne", 'Mary-Anne O’Neill'),
    ('McDonald, Hana', 'Hana McDonald'),
    ('McANULTY, Kieran', 'Kieran McAnulty'),
    ('MacLEOD, David', 'David MacLeod'),
    ('Van AMERSFOORT, Jan', 'Jan Van Amersfoort'),
    ('de JONGE, Hēmi', 'Hēmi de Jonge'),
    ('Hana McDonald', 'Hana McDonald'),
])
def test_historical_person_name_conversion(source, expected):
    assert snapshot_views.person_name(source) == expected


def test_shared_winner_helper_prefers_reconciled_name():
    assert snapshot_views.winner_name(seat(), {'name': 'PAUL, Tamatha-Kaye Erin', 'party_id': 'grn'}) == 'Tamatha Paul'
    # Matching a current candidate requires exact source evidence, never a similar name.
    assert snapshot_views.winner_name(seat(), {'name': 'HAGUE, Matthew', 'party': 'ACT New Zealand', 'party_id': 'act'}) == 'Matthew Hague'
    assert snapshot_views.winner_name(seat(), {'name': 'HAGUE, Another', 'party': 'ACT New Zealand', 'party_id': 'act'}) == 'Another Hague'
