"""Opened content keeps accessible landmarks and safe narrow-screen text styles."""
from pathlib import Path

import pytest

from product.nz_election.pipeline.landmark_checks import check_page, check_site, rendered_page
from product.nz_election.tests.design_checks import Document
from product.nz_election.tests.test_home import populated


def test_all_routes_after_client_startup(populated):
    _, site = populated
    assert check_site(site) == 79
    polls = rendered_page(site, (site / 'polls/index.html').read_text())
    names = [attrs['aria-label'] for _, attrs in Document(polls).nodes if attrs.get('role') == 'region']
    assert names.count('Theoretical seats and overhang') == 1
    assert names.count('Scenario seats and overhang') == 1
    assert '<caption>Scenario seats and overhang</caption>' in polls


def test_duplicate_region_rejected():
    with pytest.raises(ValueError, match='DUPLICATE_REGION: Seat table'):
        check_page('<div role="region" aria-label="Seat table"></div>' * 2)


@pytest.mark.parametrize('attributes', ['aria-label="Table"', 'tabindex="0"'])
def test_scroll_regions_need_name_and_keyboard_access(attributes):
    with pytest.raises(ValueError, match='SCROLL_REGION'):
        check_page(f'<div class="scroll" role="region" {attributes}></div>')


def test_open_records_keep_wrapping_and_source_typography():
    css = (Path(__file__).resolve().parents[1] / 'web/styles.css').read_text()
    assert '.download-catalogue pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px;max-width:100%}' in css
    assert '.candidate-list .candidate-sources{font-size:14px;overflow-wrap:anywhere}' in css
