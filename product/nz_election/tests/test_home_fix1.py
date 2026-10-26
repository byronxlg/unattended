"""Review regressions for the home fold and electorate picker."""
import pytest

from product.nz_election.tests.screenshots import assert_picker_targets
from product.nz_election.tests.test_home import populated  # noqa: F401


def test_picker_target_check_rejects_shrunken_and_missing_links():
    for targets in ([], [{'name': 'Auckland Central', 'width': 9, 'height': 9}],
                    [{'name': 'Auckland Central', 'width': 26, 'height': 23}]):
        with pytest.raises(AssertionError, match='HOME_PICKER_TARGET'):
            assert_picker_targets(targets)
    assert_picker_targets([{'name': 'Auckland Central', 'width': 24, 'height': 24}])


def test_home_movement_and_single_directory_link(populated):
    _, site = populated
    html = (site / 'index.html').read_text()
    # Movement is stated with its baseline date on the party cards.
    parties = html.split('<section id="parties"', 1)[1].split('</section>', 1)[0]
    assert 'class="change' in parties and 'since ' in parties
    assert html.index('<section id="seats"') < html.index('<section id="parties"')
    electorates = html.split('<section id="electorates"', 1)[1].split('</section>', 1)[0]
    assert 'href="/unattended/nz-election/electorates/"' in electorates
    assert 'class="map-label">Māori</text>' in electorates
    # Every hexagon is a link, so the map is reachable by keyboard.
    hexes = electorates.split('<svg class="hex-map"')[1].split('</svg>')[0]
    assert hexes.count('<a href="/unattended/nz-election/electorates/') == 71


def test_picker_directory_overrides_shared_desktop_grid():
    import re
    from product.nz_election.pipeline.build import PRODUCT

    css = (PRODUCT / 'web/styles.css').read_text()
    blocks = re.findall(r'\.home-picker\s+\.home-directory\s*\{([^{}]*)\}', css)
    assert any(re.search(r'(?:^|;)\s*display\s*:\s*block\s*(?:;|$)', block) for block in blocks), (
        'HOME_PICKER_DIRECTORY_LAYOUT: the single picker link must override the shared multi-column directory grid'
    )
