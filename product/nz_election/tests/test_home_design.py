"""Home charts and derived seat answer, checked without a browser."""
from copy import deepcopy

import pytest

from product.nz_election.pipeline.build import home_presentation
from product.nz_election.pipeline.home import hero
from product.nz_election.tests.design_checks import Document
from product.nz_election.tests.test_home import populated, NOW  # noqa: F401


@pytest.mark.parametrize('name', ['polls', 'electorates'])
def test_named_modules_have_accessible_svg(populated, name):
    _, site = populated
    section = (site / 'index.html').read_text().split(f'<section id="{name}"')[1].split('</section>')[0]
    charts = [attrs for tag, attrs in Document(section).nodes if tag == 'svg' and attrs.get('aria-hidden') != 'true']
    assert charts and all(a.get('role') == ('group' if a.get('class') == 'tile-map' else 'img') and a.get('aria-label') and a.get('aria-describedby') for a in charts)
    assert 'class="chart-data"' in section


@pytest.mark.parametrize(('difference', 'answer'), [(0, 'exactly enough seats to govern'), (3, '3 more than the 67 needed'), (-3, '3 short of the 67 needed')])
def test_hero_answers_from_allocator(populated, difference, answer):
    envs, _ = populated
    presentation = deepcopy(home_presentation(envs, NOW))
    result = presentation['result']
    result.update(seats={'nat': 67+difference}, assumed_house=133, assumed_majority=67, overhang=13)
    html = hero(envs, NOW, presentation)
    assert 'Governing parties: ' + f'{67+difference} seats, ' + answer + '.' in html
    assert '67 seats are needed' in html and '133-seat House' in html and '13 overhang seats' in html


def test_reading_column_is_capped(populated):
    _, site = populated
    assert 'main:has(.home-hero){max-width:732px}' in (site / 'styles.css').read_text()


def test_trend_has_direct_labels_and_threshold(populated):
    _, site = populated
    html = (site / 'index.html').read_text().split('<div id="trend"')[1].split('</section>')[0]
    svg = html.split('</svg>')[0]
    assert 'stroke-dasharray="4 3"' in svg
    for party in ['National', 'Labour', 'ACT', 'NZ First', 'Te Pāti Māori']:
        assert party in html
    assert '<path d="M' in svg and 'L' in svg


def test_compact_poll_rows_and_threshold_marks(populated):
    from product.nz_election.pipeline.home import party_order
    _, site = populated
    html = (site / 'index.html').read_text()
    polls = html.split('<section id="polls"')[1].split('</section>')[0]
    assert polls.count('class="chart-row"') == len(party_order()) + 1
    assert all(shape in polls for shape in ['Filled circle', 'Open square', 'Triangle', '(newest)'])
    from product.nz_election.pipeline.home import thresholds
    threshold = thresholds(populated[0])
    assert '<rect ' in threshold and 'stroke-dasharray="4 3"' in threshold
    assert 'Electorate assumed' in threshold and 'Needs 5%' in threshold
    for module in ['polls', 'electorates']:
        section = html.split(f'<section id="{module}"')[1].split('</section>')[0]
        assert '<text ' not in section
        assert 'chart-label' in section


@pytest.mark.parametrize('width', [360, 390, 1280])
def test_chart_type_gate_rejects_previous_scaling(width):
    from product.nz_election.tests.screenshots import assert_chart_text_sizes
    # 5cc640b used a 350-unit viewBox, 12-unit labels and 11-unit figures.
    scale = min(width-32, 700)/350
    with pytest.raises(AssertionError, match='HOME_CHART_TEXT_SIZE'):
        assert_chart_text_sizes([dict(text='party', pixels=12*scale), dict(text='value', pixels=11*scale)], 16)
    assert_chart_text_sizes([dict(text='party', pixels=14), dict(text='value', pixels=13), dict(text='status', pixels=12)], 16)


def test_trend_stops_at_last_observation(populated):
    from datetime import date, timedelta
    import re
    from product.nz_election.pipeline.home import trend_graphic
    from product.nz_election.pipeline.home_charts import colour
    envs, _ = populated
    envs = deepcopy(envs)
    averages = envs['averages']['data']
    cutoff = date.fromisoformat(averages[-1]['date']) - timedelta(days=14)
    for average in averages:
        if date.fromisoformat(average['date']) > cutoff:
            average['descriptive']['nat']['value'] = None
    selected = averages[-29::7]
    if averages[-1] not in selected:
        selected.append(averages[-1])
    last = next(a for a in reversed(selected) if a['descriptive']['nat']['value'] is not None)
    start, end = map(date.fromisoformat, [selected[0]['date'], selected[-1]['date']])
    last_date = date.fromisoformat(last['date'])
    last_x = 330 * (last_date-start).days / (end-start).days
    html = trend_graphic(envs)
    paths = [a['d'] for tag, a in Document(html).nodes if tag == 'path' and a.get('stroke') == colour('nat')]
    assert paths
    for path in paths:
        coordinates = re.findall(r'[ML]([\d.]+) [\d.]+', path)
        assert coordinates and all(float(x) <= last_x + 0.05 for x in coordinates), path
    assert re.search(r'National [^<]+\(' + re.escape(f'{last_date.day} {last_date:%b}') + r'\)', html)
