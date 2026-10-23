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
    hero = html.split('id="seats"', 1)[1].split('</section>', 1)[0]
    assert 'class="poll-change"' in hero and 'since ' in hero
    assert hero.index('class="poll-change"') < hero.index('class="strip"')
    assert html.count('Browse all electorates and candidates') == 1
    assert 'See all electorates' not in html
    assert 'Māori<br>electorates' in html
    assert 'class="picker-map" tabindex="0"' in html


def test_picker_directory_overrides_shared_desktop_grid():
    import re
    from product.nz_election.pipeline.build import PRODUCT

    css = (PRODUCT / 'web/styles.css').read_text()
    blocks = re.findall(r'\.home-picker\s+\.home-directory\s*\{([^{}]*)\}', css)
    assert any(re.search(r'(?:^|;)\s*display\s*:\s*block\s*(?:;|$)', block) for block in blocks), (
        'HOME_PICKER_DIRECTORY_LAYOUT: the single picker link must override the shared multi-column directory grid'
    )
