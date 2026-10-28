"""Retained poll answers precede refresh status on home."""
from copy import deepcopy

from product.nz_election.pipeline.build import home_presentation
from product.nz_election.pipeline.home import page, seat_hero
from product.nz_election.tests.design_checks import Document
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401
from product.nz_election.tools.check_visible_text import VisibleText, check_absent_text


def test_retained_answer_before_update_note(populated):
    envs, _ = populated
    expected = VisibleText(seat_hero(envs, NOW, home_presentation(envs, NOW))).text
    assert 'seats' in expected and 'poll average' in expected
    retained = deepcopy(envs)
    retained['status']['run_url'] = 'https://github.com/byronxlg/unattended/actions/runs/123'
    status = next(r for r in retained['status']['data'] if r['dataset'] == 'polls')
    status.update(state='failed',
                  error_code='parse_drift',
                  last_attempt_at='2026-10-28T20:09:00Z',
                  last_success_at='2026-10-28T18:22:00Z')
    built = '2026-10-29T01:00:00Z'
    html = page(retained, built, home_presentation(retained, built))
    text = VisibleText(html).text
    note = 'The 29 Oct, 09:09 NZDT update failed; showing previous data from 29 Oct, 07:22 NZDT.'
    assert expected in text
    assert text.index(expected) < text.index(note) < text.index('Update details')
    assert any(a.get('href') == retained['status']['run_url']
               for tag, a in Document(html).nodes if tag == 'a')
    assert retained['averages'] == envs['averages']
    assert retained['seats'] == envs['seats']
    check_absent_text(html)


def test_failed_without_retained_average_omits_answer(populated):
    envs = deepcopy(populated[0])
    for family in ('polls', 'averages', 'seats'):
        envs.pop(family)
    status = next(r for r in envs['status']['data'] if r['dataset'] == 'polls')
    status.update(state='failed', error_code='parse_drift')
    html = page(envs, NOW, home_presentation(envs, NOW))
    text = VisibleText(html).text
    assert 'Who is favoured' not in text
    assert 'Seats on the' not in text
    check_absent_text(html)
