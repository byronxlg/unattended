"""Opened content keeps accessible landmarks and safe narrow-screen text styles."""
from pathlib import Path

import pytest

from product.nz_election.pipeline.landmark_checks import check_page, check_site
from product.nz_election.tests.design_checks import Document
from product.nz_election.tests.test_home import populated


def test_all_server_rendered_routes(populated):
    _, site = populated
    assert check_site(site) == 81
    polls = (site / 'polls/index.html').read_text()
    names = [attrs['aria-label'] for _, attrs in Document(polls).nodes if attrs.get('role') == 'region']
    # Each scrolling table is a named region whose name matches its caption.
    assert names == ['Weekly snapshots of the 30-day average, percent', 'Every national poll this year, party vote percent']
    for name in names:
        assert f'>{name}</caption>' in polls
    assert '<fieldset' not in polls


def test_duplicate_region_rejected():
    with pytest.raises(ValueError, match='DUPLICATE_REGION: Seat table'):
        check_page('<div role="region" aria-label="Seat table"></div>' * 2)


@pytest.mark.parametrize('attributes', ['aria-label="Table"', 'tabindex="0"'])
def test_scroll_regions_need_name_and_keyboard_access(attributes):
    with pytest.raises(ValueError, match='SCROLL_REGION'):
        check_page(f'<div class="scroll" role="region" {attributes}></div>')


def test_open_records_keep_wrapping_and_source_typography():
    css = (Path(__file__).resolve().parents[1] / 'web/styles.css').read_text()
    assert '.download-catalogue pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:var(--fs-body);max-width:100%}' in css
    assert '.candidate-list .candidate-sources{font-size:var(--fs-caption);overflow-wrap:anywhere}' in css
