"""Accepted home question order and clock-driven transitions."""
from copy import deepcopy

from product.nz_election.pipeline.build import home_presentation
from product.nz_election.pipeline.home import page, voting_dates, hero
from product.nz_election.tests.design_checks import Document, provenance
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401


def test_enrolment_midnight_uses_nz_clock():
    assert 'Enrol by 25 October' in voting_dates('2026-10-25T10:59:59Z')
    after = voting_dates('2026-10-25T11:00:00Z')
    assert 'Enrolment closed on 25 October' in after
    assert 'advance voting from 26 October; election day 7 November' in after
    assert '/vote/' in after and 'https://vote.nz/' in after
    assert voting_dates(NOW, []) == ''


def test_night_handover_requires_time_and_published_2026_family(populated):
    envs, _ = populated
    before, after = '2026-11-07T05:59:59Z', '2026-11-07T06:00:00Z'
    presentation = home_presentation(envs, NOW)
    old = page(envs, before, presentation)
    assert 'id="night-summary"' not in old and 'id="seats"' in old
    new = page(envs, after, presentation)
    assert 'id="night-summary"' in new and 'id="seats"' not in new
    assert 'of voting places reported' in new and 'Updated 2026-' in new
    assert 'Election night results' in new
    # The night summary takes the top; the seat estimate and the voting-dates module leave.
    assert [a['id'] for tag, a in Document(new).nodes if tag == 'section'] == [
        'dates', 'night-summary', 'parties', 'trend', 'polls', 'electorates', 'thresholds']
    provenance(new)
    missing = {key: value for key, value in envs.items() if not key.startswith('night/')}
    html = page(missing, after, presentation)
    assert 'id="night-summary"' in html and 'id="seats"' not in html
    archive = deepcopy(envs)
    archive['night/index']['data'] = [seq for seq in archive['night/index']['data'] if seq['id'] != '2026-media']
    assert 'id="night-summary"' in page(archive, after, home_presentation(archive, after))


def test_removed_modules_keep_their_destination(populated):
    _, site = populated
    home = (site / 'index.html').read_text()
    # Thresholds came back to home with the redesign; markets stay on methods only.
    for identity in ('leaders', 'markets', 'more'):
        assert f'<section id="{identity}"' not in home
    assert 'id="home-thresholds"' in (site / 'methods/index.html').read_text()
    assert 'social/poc/' not in home
    assert 'id="home-markets"' in (site / 'methods/index.html').read_text()
    assert 'id="markets"' in (site / 'methods/index.html').read_text()
    assert 'Christopher Luxon' in (site / 'parties/index.html').read_text()


def test_one_block_per_allocator_seat(populated):
    envs, _ = populated
    presentation = home_presentation(envs, NOW)
    html = hero(envs, NOW, presentation)
    assert html.count('class="seat"') == presentation['result']['assumed_house']
    assert str(presentation['result']['assumed_majority']) + ' needed' in html


def test_chart_delta_compares_previous_daily_average(populated):
    from product.nz_election.pipeline.home import trend_graphic
    envs, _ = populated
    envs = deepcopy(envs)
    latest, previous = envs['averages']['data'][-1], envs['averages']['data'][-2]
    latest['descriptive']['nat'].update(value=32, scale=1)
    previous['descriptive']['nat'].update(value=30, scale=1)
    html = trend_graphic(envs)
    assert '+2.0 pp' in html and 'Change since ' + previous['date'] in html
    assert html.count('class="trend-layout"') == 2
    assert '<polygon ' in html and 'fill-opacity="0.3"' in html
