"""Campaign acceptance checks use real snapshots and isolated malformed copies."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from product.nz_election.pipeline import campaign_checks as c, snapshots, verify
from product.nz_election.pipeline.parties_page import page


@pytest.fixture
def copied(tmp_path):
    for name in ('donations.json', 'pollster-record.json'):
        shutil.copy(snapshots.SNAPSHOTS / name, tmp_path / name)
    shutil.copytree(snapshots.SNAPSHOTS / 'pollster-record-sources',
                    tmp_path / 'pollster-record-sources')
    return tmp_path


def edit(directory, name, change):
    path = directory / (name + '.json')
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def test_campaign_committed_fixtures():
    result = subprocess.run([sys.executable, str(Path(verify.__file__)), 'campaign'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == 'PASS campaign\n'


@pytest.mark.parametrize('field', ['party', 'donor', 'amount_nzd', 'document_url'])
@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid'])
def test_donation_required_facts(copied, field, bad):
    # Text fields accept any nonblank string, but party identity must still match.
    if field == 'donor' and bad == 'ſ-invalid':
        bad = ' \t'
    edit(copied, 'donations', lambda d: d['records'][0].update({field: bad}))
    with pytest.raises(ValueError, match='^' + c.DONATION_ROWS):
        c.check_snapshots(copied)


def test_donation_threshold(copied):
    edit(copied, 'donations', lambda d: d['records'][0].update(amount_nzd='20000'))
    with pytest.raises(ValueError, match='^' + c.DONATION_ROWS):
        c.check_snapshots(copied)


@pytest.mark.parametrize('field', ['received', 'disclosed'])
@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid', '2026-10-20'])
def test_donation_dates(copied, field, bad):
    edit(copied, 'donations', lambda d: d['records'][0].update({field: bad}))
    with pytest.raises(ValueError, match='^' + c.DONATION_DATES):
        c.check_snapshots(copied)


def test_absent_dates_remain_absent(copied):
    def remove(data):
        for field in ('received', 'disclosed'):
            data['records'][0].pop(field)
    edit(copied, 'donations', remove)
    rows, _ = c.check_snapshots(copied)
    assert 'received' not in rows[0] and 'disclosed' not in rows[0]


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid', 145])
def test_index_accounting(copied, bad):
    edit(copied, 'donations', lambda d: d.update(listed_return_count=bad))
    with pytest.raises(ValueError, match='^' + c.DONATION_INDEX):
        c.check_snapshots(copied)


def test_index_omission_requires_reason(copied):
    def omit(data):
        row = data['records'].pop()
        row.pop('donor')
        data['skipped_returns'].append(row)
    edit(copied, 'donations', omit)
    with pytest.raises(ValueError, match='^' + c.DONATION_INDEX):
        c.check_snapshots(copied)


def test_no_derived_funding_in_data(copied):
    edit(copied, 'donations', lambda d: d.update(total_funding='10000000'))
    with pytest.raises(ValueError, match='^' + c.NO_TOTAL_FUNDING):
        c.check_snapshots(copied)


def test_final_poll_not_earlier_poll(copied):
    def newer(data):
        row = deepcopy(next(r for r in data['records'] if r['year'] == 2020))
        for key in ('party_errors', 'official_shares', 'mean_absolute_error',
                    'compared_parties', 'not_reported_parties', 'election_day'):
            row.pop(key)
        row.update(id='test-later-poll', fieldwork_end='2020-10-16')
        data['candidates'].append(row)
    edit(copied, 'pollster-record', newer)
    with pytest.raises(ValueError, match='^' + c.FINAL_POLL):
        c.check_snapshots(copied)


@pytest.mark.parametrize('bad', ['', None, [], {}, True, 1.5, 10**100, 'ſ-invalid', '2023-10-15'])
def test_no_post_election_fieldwork(copied, bad):
    edit(copied, 'pollster-record', lambda d: next(
        r for r in d['records'] if r['year'] == 2023).update(fieldwork_end=bad))
    with pytest.raises(ValueError, match='^' + c.FINAL_POLL):
        c.check_snapshots(copied)


@pytest.mark.parametrize('field', ['party_errors', 'official_shares', 'mean_absolute_error'])
def test_official_party_errors(copied, field):
    edit(copied, 'pollster-record', lambda d: d['records'][0].update({field: {}}))
    with pytest.raises(ValueError, match='^' + c.OFFICIAL_ERRORS):
        c.check_snapshots(copied)


def test_coverage_stated(copied):
    edit(copied, 'pollster-record', lambda d: d['records'][0].update(compared_parties=[]))
    with pytest.raises(ValueError, match='^' + c.COVERAGE):
        c.check_snapshots(copied)


@pytest.mark.parametrize('change,reason', [
    (lambda h: h.replace('EC returns</a>', 'EC returns</span>').replace(
        '<a href="https://elections.nz/democracy-in-nz/political-parties-in-new-zealand/donations-exceeding-20000">', '<span>'), c.PROVENANCE),
    (lambda h: h.replace('aria-describedby=', 'data-description='), c.PROVENANCE),
    (lambda h: h + '<p>Not available</p>', c.ABSENT),
    (lambda h: h + '<p>Total funding: NZD 1,000,000</p>', c.NO_TOTAL_FUNDING),
    (lambda h: h.replace('data-total="', 'data-total="0'), c.ABSENT),
    (lambda h: h.replace('Who funds it?', 'Who funds it? NZD 0'), c.ABSENT),
])
def test_rendered_invariants(change, reason):
    rows, _ = c.check_snapshots()
    html = page({}, '2026-10-25T00:00:00Z')
    with pytest.raises(ValueError, match='^' + reason):
        c.check_markup(change(html), rows)


def test_absent_donations_cannot_render_zero():
    html = '<div class="party-donations" data-count="0" data-total="0.00">NZD 0</div>'
    with pytest.raises(ValueError, match='^' + c.ABSENT):
        c.check_markup(html, [])


def test_advance_delegated(tmp_path, monkeypatch):
    def fail(envs, root, **kwargs):
        raise ValueError('test advance failure')
    monkeypatch.setattr(verify, 'verify_advance', fail)
    with pytest.raises(ValueError, match='^' + c.ADVANCE + ': test advance failure'):
        verify.verify_campaign({}, tmp_path)


def test_supplied_data_used(tmp_path, monkeypatch):
    supplied = tmp_path / 'supplied'
    supplied.mkdir()
    seen = []
    monkeypatch.setattr(verify.export, 'validate_bundle', lambda path: seen.append(path) or {'total_funding': 1})
    with pytest.raises(ValueError, match='^' + c.NO_TOTAL_FUNDING):
        verify.verify_campaign({}, tmp_path, data=supplied)
    assert seen == [supplied]


def test_all_registers_campaign(tmp_path, monkeypatch, capsys):
    called = []
    for name in dir(verify):
        if name.startswith('verify_'):
            monkeypatch.setattr(verify, name, lambda *a, _name=name, **kw: called.append(_name))
    monkeypatch.setattr(verify, 'refresh', lambda *a, **kw: None)
    monkeypatch.setattr(verify.export, 'validate_bundle', lambda *a: {})
    monkeypatch.setattr(sys, 'argv', ['verify', 'all'])
    verify.main()
    assert called.count('verify_campaign') == 1
    assert 'PASS campaign\n' in capsys.readouterr().out


def test_national_poll_scope(copied):
    edit(copied, 'pollster-record', lambda d: d['records'][0].update(
        source_locator='Preferred prime minister table'))
    with pytest.raises(ValueError, match='^' + c.FINAL_POLL):
        c.check_snapshots(copied)


def test_official_results_bound_to_capture():
    data = json.loads((snapshots.SNAPSHOTS / 'pollster-record.json').read_text())
    result = next(r for r in data['official_results'] if r['year'] == 2020)
    result['parties'][0]['votes'] = '1'
    with pytest.raises(ValueError, match='^' + c.OFFICIAL_ERRORS):
        c.check_official(data)


def test_hidden_funding_attribute():
    with pytest.raises(ValueError, match='^' + c.NO_TOTAL_FUNDING):
        c.check_markup('<div data-total-funding="100">Example</div>', [])


def test_supplied_site_checked(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, 'verify_advance', lambda *args, **kwargs: None)
    site = tmp_path / 'site'
    (site / 'parties').mkdir(parents=True)
    (site / 'parties/index.html').write_text('<p>Not reported</p>')
    (site / 'build-manifest.json').write_text(json.dumps({'data': {'built_at': '2026-10-25T00:00:00Z'}}))
    with pytest.raises(ValueError, match='^' + c.ABSENT + ': ABSENT_TEXT'):
        verify.verify_campaign({}, tmp_path, site=site)


def test_unrenderable_optional_date_has_named_failure(tmp_path, monkeypatch):
    from product.nz_election.pipeline import parties_page
    monkeypatch.setattr(verify, 'verify_advance', lambda *args, **kwargs: None)
    def broken(*args, **kwargs):
        raise KeyError('received')
    monkeypatch.setattr(parties_page, 'page', broken)
    with pytest.raises(ValueError, match='^' + c.ABSENT + ': parties render:'):
        verify.verify_campaign({}, tmp_path)


def test_omitted_candidate_cannot_change_final_poll(copied):
    edit(copied, 'pollster-record', lambda d: d['candidates'].pop(0))
    with pytest.raises(ValueError, match='^' + c.FINAL_POLL + ': candidate ledger'):
        c.check_snapshots(copied)


def test_fieldwork_end_bound_to_source_label(copied):
    def change(data):
        row = data['candidates'][0]
        row['fieldwork_end'] = '2014-10-13'
    edit(copied, 'pollster-record', change)
    with pytest.raises(ValueError, match='^' + c.FINAL_POLL + ': fieldwork end'):
        c.check_snapshots(copied)
