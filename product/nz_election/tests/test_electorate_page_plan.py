"""Accepted question order, reconciled identities and absent-block contracts."""
from copy import deepcopy
from urllib.parse import urljoin, urlsplit, unquote
import pytest
from product.nz_election.pipeline.build import config, PREFIX
from product.nz_election.pipeline.content_checks import Tree, Node
from product.nz_election.pipeline.electorate_pages import detail, previous_result
from product.nz_election.pipeline import snapshot_views, snapshots
from product.nz_election.tests.design_checks import provenance


def seat(slug='wellington-north'):
    return next(r for r in config('electorates') if r['slug'] == slug)


def text(node):
    if isinstance(node, str):
        return node
    return ' '.join(' '.join(text(child) for child in node.children).split())


def descendants(node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from descendants(child)


def accessible_name(node, tree):
    if node.attrs.get('aria-labelledby'):
        ids = {n.attrs.get('id'): n for n in tree.nodes if n.attrs.get('id')}
        return ' '.join(text(ids[ref]) for ref in node.attrs['aria-labelledby'].split())
    return node.attrs.get('aria-label') or text(node) or node.attrs.get('alt', '')


def heading(tree, title):
    return next(n for n in tree.nodes if (n.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
                                        or n.attrs.get('role') == 'heading') and text(n) == title)


def answer_region(tree, title):
    title_node = heading(tree, title)
    regions = [n for n in tree.nodes if (n.tag in {'section', 'article'} or n.attrs.get('role') == 'region')
               and title_node in list(descendants(n))]
    return min(regions, key=lambda n: len(list(descendants(n))))


def links(tree):
    return [n for n in tree.nodes if n.tag == 'a' and n.attrs.get('href')]


def assert_map_accessibility(html, row, site=None):
    tree = Tree(html)
    maps = [n for n in tree.nodes if n.attrs.get('role') in {'group', 'img', 'region'}
            and 'map' in accessible_name(n, tree).lower()]
    assert maps, 'Electorate map needs an accessible name'
    selected = [n for graphic in maps for n in descendants(graphic)
                if n.attrs.get('aria-current', 'false') != 'false' or n.attrs.get('aria-selected') == 'true']
    assert len(selected) == 1, 'Exactly one electorate must be identified as selected'
    assert row['name'] in accessible_name(selected[0], tree), 'Selected map item must name this electorate'
    routes = {PREFIX + r['path'] for r in config('routes')}
    routes.update(PREFIX + 'electorates/' + r['slug'] + '/' for r in config('electorates'))
    current = PREFIX + 'electorates/' + row['slug'] + '/'
    map_links = [n for graphic in maps for n in descendants(graphic) if n.tag == 'a' and 'href' in n.attrs]
    assert map_links, 'The map must provide an accessible selection link'
    for link in map_links:
        assert accessible_name(link, tree).strip(), 'Map links need accessible names'
        target = urlsplit(urljoin(current, link.attrs['href']))
        assert not target.scheme and not target.netloc and target.path in routes
        if site is not None:
            destination = site / target.path.removeprefix(PREFIX) / 'index.html'
            assert destination.is_file(), target.path
            target_tree = Tree(destination.read_text())
        else:
            target_tree = tree if target.path == current else None
        if target.fragment and target_tree is not None:
            assert unquote(target.fragment) in {n.attrs.get('id') for n in target_tree.nodes}


def test_selected_seat_identity_accessible_links_and_provenance():
    for row in config('electorates'):
        html = detail(row, {})
        assert_map_accessibility(html, row)
        visible = text(Tree(html).root)
        assert 'Schematic, not a legal boundary.' in visible
        assert 'Local polls' not in visible
        provenance(html)


def test_page_plan_question_order(populated):
    _, site = populated
    for row in config('electorates'):
        tree = Tree((site / 'electorates' / row['slug'] / 'index.html').read_text())
        answers = [heading(tree, 'Who is standing in 2026?'),
                   next(n for n in links(tree) if accessible_name(n, tree) == 'Check your enrolled electorate at vote.nz'),
                   next(n for n in links(tree) if accessible_name(n, tree) == 'Compare these candidates at Policy.nz')]
        result_headings = [n for n in tree.nodes if n.tag in {'h2', 'h3'} and text(n) == 'Who won last time?']
        answers += result_headings
        positions = [tree.nodes.index(n) for n in answers]
        assert positions == sorted(positions), f'{row["name"]}: expected candidates, enrolment, policy, then previous result; positions={positions}'


def test_reconciled_display_names_ranks_order_and_only_explicit_incumbents():
    for row in config('electorates'):
        tree = Tree(detail(row, {}))
        region = answer_region(tree, 'Who is standing in 2026?')
        rec = next(r for r in snapshot_views.load('candidate-reconciliation-2026') if r['electorate_slug'] == row['slug'])
        originals = {(c['name'], c['party']): c for c in snapshot_views.load('candidates-2026') if c['electorate_slug'] == row['slug']}
        candidates = rec['matched'] + rec['added_by_ec']
        records = [n for n in descendants(region) if n.tag in {'li', 'tr'} or n.attrs.get('role') in {'listitem', 'row'}]
        records = [n for n in records if n.tag == 'li' or n.attrs.get('role') == 'listitem'
                   or any(c.tag == 'td' or c.attrs.get('role') == 'cell' for c in descendants(n))]
        assert len(records) == len(candidates)
        for record, candidate in zip(records, candidates):
            content = text(record)
            assert candidate['snapshot_name'] in content and candidate['party'] in content
            if 'list_rank' in candidate:
                assert f'List {candidate["list_rank"]}' in content
            original = originals.get((candidate['snapshot_name'], candidate['snapshot_party']), {})
            assert ('Incumbent' in content) == bool(original.get('sitting_electorate_mp'))
    content = text(Tree(detail(seat(), {})).root)
    assert 'Michael Appleby' in content and 'APPLEBY, Michael' not in content
    assert 'Josh Harford' in content and 'HARFORD, Joshua' not in content


def test_policy_link_only_when_present(monkeypatch):
    def policy_links(row):
        return [n.attrs['href'] for n in links(Tree(detail(row, {})))
                if urlsplit(n.attrs['href']).hostname == 'policy.nz']
    original = snapshot_views.load
    monkeypatch.setattr(snapshot_views, 'load', lambda n: [] if n == 'policy-links' else original(n))
    assert not policy_links(seat())
    url = 'https://policy.nz/2026/electorate-vote/wellington-north'
    monkeypatch.setattr(snapshot_views, 'load', lambda n: [{'electorate_slug': 'wellington-north', 'url': url}] if n == 'policy-links' else original(n))
    assert policy_links(seat()) == [url]
    assert not policy_links(seat('te-tai-tonga'))


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
    content = text(answer_region(Tree(html), 'Who won last time?'))
    assert 'by-election' in content
    assert f'{ranked[0]["votes"]-ranked[1]["votes"]:,} votes' in content
    for v in votes:
        assert f'{v["votes"]:,} votes' in html


def live_env():
    return {'night/index': {'data': [{'id': 'live', 'reference_path': 'night/references/current.json', 'snapshot_paths': ['night/live/current.json']}]},
            'night/references/current': {'data': [{'electorates': {'59': {'electorate_name': 'Wellington North'}}, 'candidates': {'1': {'candidate_name': 'Test leader'}, '2': {'candidate_name': 'Test runner'}}}]},
            'night/live/current': {'data': [{'leaders': {'59': {'leader': '1', 'margin': 123, 'status': 'provisional', 'statistics': {'total_voting_places_counted': 4, 'total_voting_places': 12}}}, 'source_updated_local': '2026-11-07T20:00:00'}]}}


def test_current_night_answer_promotes_above_candidates():
    envs = live_env()
    html = detail(seat(), envs, '2026-11-07T07:00:00Z')
    tree = Tree(html)
    assert tree.nodes.index(heading(tree, 'Who is leading here now?')) < tree.nodes.index(heading(tree, 'Who is standing in 2026?'))
    assert 'Test leader' in html and 'Margin: 123 votes' in html
    assert '4 of 12 voting places counted' in html and 'Provisional leader' in html
    provenance(html)
    assert 'Who is leading here now?' in detail(seat(), envs, '2026-11-07T06:00:00+00:00')
    assert 'Who is leading here now?' not in detail(seat(), envs, '2026-11-07T05:59:59Z')
    assert 'Who is leading here now?' not in detail(seat('te-tai-tonga'), envs, '2026-11-07T07:00:00Z')
    envs['night/index']['data'][0]['id'] = '2023'
    assert 'Who is leading here now?' not in detail(seat(), envs, '2026-11-07T07:00:00Z')


def test_night_absent_and_tied_counts():
    envs = live_env()
    item = envs['night/live/current']['data'][0]['leaders']['59']
    item.update(status='not yet reported', leader=None, margin=None)
    assert 'Who is leading here now?' not in detail(seat(), envs)
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
        source_ids = {ref for node in tree.nodes for ref in node.attrs.get('aria-describedby', '').split()}
        for parent in tree.nodes:
            children = [n for n in parent.children if not isinstance(n, str)]
            for left, right in zip(children, children[1:]):
                if all(n.attrs.get('id') in source_ids for n in (left, right)):
                    assert ' '.join(left.text.split()) != ' '.join(right.text.split()), 'REPEATED_ADJACENT_PROVENANCE'
        assert text(tree.root).count('Data to 20 October 2026.') == 1
        check_sources(html)
        provenance(html)


def test_methods_describe_current_detail_graphic_and_names():
    html = snapshot_views.sources({})
    assert 'squares on detail pages' not in html
    assert 'Electorate detail pages use the same schematic hex layout' in html
    assert 'candidate cards display the reconciled snapshot names' in html
    tree = Tree(html)
    ids = {n.attrs.get('id') for n in tree.nodes}
    boundary_links = [n for n in links(tree) if 'boundary' in accessible_name(n, tree).lower()]
    assert boundary_links
    assert all(unquote(n.attrs['href'][1:]) in ids for n in boundary_links if n.attrs['href'].startswith('#'))


from product.nz_election.tests.test_home import populated  # noqa: F401


def assert_readable_person_names(html):
    import re
    content = text(Tree(html).root)
    assert content
    assert not re.search(r"\b[A-ZĀĒĪŌŪ][A-ZĀĒĪŌŪ'’-]+,\s+[A-ZĀĒĪŌŪ][a-zāēīōū]", content), 'EC_SHEET_PERSON_NAME'


def test_no_ec_sheet_person_names_on_electorate_pages(populated):
    _, site = populated
    pages = list((site / 'electorates').glob('*/index.html'))
    assert len(pages) == 71
    for path in pages:
        html = path.read_text()
        assert_readable_person_names(html)
        assert_map_accessibility(html, seat(path.parent.name), site)
    wellington = (site / 'electorates/wellington-north/index.html').read_text()
    assert 'Tamatha Paul won by' in wellington
    assert 'Tamatha Paul' in text(answer_region(Tree(wellington), 'Who is standing in 2026?'))
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


def test_empty_candidates_map_links_resolve(monkeypatch):
    original = snapshot_views.load
    monkeypatch.setattr(snapshot_views, 'load', lambda name: [dict(r, matched=[], added_by_ec=[])
        for r in original(name)] if name == 'candidate-reconciliation-2026' else original(name))
    for row in config('electorates'):
        html = detail(row, {})
        assert 'Who is standing in 2026?' not in text(Tree(html).root)
        assert_map_accessibility(html, row)
        provenance(html)


@pytest.mark.parametrize('case', ['fold', 'empty'])
def test_electorate_phone_browser(populated, tmp_path, case):
    import subprocess
    from pathlib import Path
    _, site = populated
    result = subprocess.run(['uv', 'run', str(Path(__file__).with_name('electorate_phone_browser.py')),
                             '--site', str(site.parent), '--case', case, '--out', str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS electorate ' + case in result.stdout
