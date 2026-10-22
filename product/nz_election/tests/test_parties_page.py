"""Party answers retain their order, absence semantics and EC-listed totals."""
from copy import deepcopy
from decimal import Decimal
import re

from product.nz_election.pipeline.parties_page import page, ordered, supplemental, polling, largest_donors
from product.nz_election.pipeline.snapshots import load
from product.nz_election.tests.design_checks import Document, provenance

BUILT = '2026-10-22T07:00:00Z'


def facts():
    return {**{n: load(n) for n in ('leaders', 'positions', 'donations')},
            **{n: supplemental(n) for n in ('policy-links', 'party-list-tops')}}


def averages():
    return [{'date': '2026-10-01', 'descriptive': {'nat': {'value': 35, 'scale': 1}, 'lab': {'value': 30, 'scale': 1}}},
            {'date': '2026-10-20', 'descriptive': {'nat': {'value': 320, 'scale': 10}, 'lab': {'value': 34, 'scale': 1}}}]


def test_latest_average_orders_sections_and_picker():
    rows = averages()
    html = page({'averages': {'data': list(reversed(rows))}}, BUILT)
    expected = ordered(rows)
    assert expected[:2] == ['lab', 'nat']
    doc = Document(html)
    sections = [a['id'] for t, a in doc.nodes if t == 'section']
    chips = [a['href'][1:] for t, a in doc.nodes if t == 'a' and a.get('href', '').startswith('#')]
    assert sections == chips == expected
    provenance(html)
    assert 'Up 4.0 percentage points since 1 Oct 2026' in html
    assert html.index('party-position') < html.index('party-policy') < html.index('party-candidates') < html.index('party-donations')


def test_absent_party_fields_drop_their_lines():
    data = facts()
    for name in data:
        data[name] = [r for r in data[name] if r.get('party_id') != 'lab']
    html = page({}, BUILT, data)
    section = html.split('id="lab"', 1)[1].split('</section>', 1)[0]
    assert not any(word in section for word in ('party-portrait', 'party-poll', 'party-position', 'party-policy', 'party-candidates', 'party-donations'))
    assert not re.search(r'not available|unavailable|missing|pending', html, re.I)
    data = facts()
    for leader in data['leaders']:
        leader.pop('photo', None)
    html = page({}, BUILT, data)
    assert '<img' not in html and 'Chris Hipkins' in html


def test_totals_include_unchecked_donation_rows():
    data = facts()
    assert any(not row['document_checked'] for row in data['donations'])
    html = page({}, BUILT, data)
    for party in ordered([]):
        rows = [r for r in data['donations'] if r['party_id'] == party and r['received'].startswith('2026')]
        section = html.split('id="' + party + '"', 1)[1].split('</section>', 1)[0]
        total = sum((Decimal(r['amount_nzd']) for r in rows), Decimal(0))
        assert f'data-total="{total:.2f}" data-count="{len(rows)}"' in section
        largest = largest_donors(rows)
        assert all(name.replace('&', '&amp;') in section for name, _ in largest)


def test_top_ranks_are_not_first_five_electorate_candidates():
    tops = {r['party_id']: r for r in supplemental('party-list-tops')}
    assert tops['nat']['candidates'][1]['name'] == 'Nicola Valentine Willis'
    assert tops['lab']['candidates'][3]['name'] == 'William Jackson'
    assert tops['nzf']['candidates'][0]['name'] == 'Winston Peters'
    assert tops['tpm']['candidates'] == [{'rank': 1, 'name': 'Lance Norman'}]
    assert all([c['rank'] for c in r['candidates']] == list(range(1, len(r['candidates']) + 1)) for r in tops.values())


def test_missing_latest_share_does_not_reuse_an_old_number():
    rows = deepcopy(averages())
    rows[-1]['descriptive']['lab']['value'] = None
    assert polling('lab', rows) == ''
    assert ordered(rows)[0] == 'nat'


def test_largest_donors_combine_returns_without_fuzzy_name_joins():
    rows = [dict(donor='A', amount_nzd='30000', received='2026-01-01'),
            dict(donor='A', amount_nzd='40000', received='2026-02-01'),
            dict(donor='A Ltd', amount_nzd='60000', received='2026-03-01')]
    result = largest_donors(rows)
    assert result[0] == ('A', dict(amount=Decimal('70000'), dates={'2026-01-01', '2026-02-01'}))
    assert result[1][0] == 'A Ltd'


def test_picker_chips_share_top_at_360(tmp_path):
    import subprocess
    result = subprocess.run(['uv', 'run', 'product/nz_election/tests/parties_picker_browser.py', str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS party picker' in result.stdout


def test_picker_overrides_shared_nav_wrapping():
    from product.nz_election.pipeline.build import PRODUCT
    shared = (PRODUCT / 'web/styles.css').read_text()
    picker = (PRODUCT / 'web/parties.css').read_text()
    assert re.search(r'nav\s*\{[^}]*flex-wrap:wrap', shared)
    rule = re.search(r'\.party-picker\s*\{([^}]+)\}', picker)[1]
    assert 'flex-wrap:nowrap' in rule
    assert 'overflow-x:auto' in rule
