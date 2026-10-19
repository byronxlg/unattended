"""Static coverage of the unchanged harness's home row keyboard target."""
from html.parser import HTMLParser
import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from product.nz_election.pipeline.build import build, PRODUCT, PREFIX
from product.nz_election.tests.design_states import STATES, fixture


class RowLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent_hidden, parent_row = self.stack[-1][1:] if self.stack else (False, False)
        hidden = parent_hidden or 'hidden' in attrs or (tag == 'details' and 'open' not in attrs)
        row = parent_row or bool({'watch-rows', 'home-directory'} & set(attrs.get('class', '').split()))
        if tag == 'a' and row and not hidden and 'href' in attrs and int(attrs.get('tabindex', '0')) >= 0:
            self.links.append(attrs['href'])
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, hidden, row))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def assert_home_row(site):
    links = RowLinks((site / 'index.html').read_text()).links
    assert links, 'HOME_ROW_KEYBOARD_FOCUS: neither watch rows nor directory has a focusable link'
    for href in links:
        path = urlsplit(href).path
        assert path.startswith(PREFIX)
        assert (site / path.removeprefix(PREFIX) / 'index.html').is_file(), href


@pytest.mark.parametrize('state', STATES)
def test_home_row_in_every_design_state(tmp_path, state):
    site, _ = fixture(tmp_path, state)
    assert_home_row(site / 'nz-election')


def test_home_row_with_deployment_data(tmp_path):
    data = Path(os.environ.get('NZ_ELECTION_TEST_DATA', PRODUCT / 'data'))
    site = build(data, tmp_path / 'site/nz-election', built='2026-10-19T01:00:00Z')
    assert_home_row(site)


def test_row_check_rejects_non_focusable_or_unrelated_links():
    html = '<div class="watch-rows"><a>No href</a><a href="/" tabindex="-1">Removed</a></div>'
    html += '<ul class="home-directory" hidden><li><a href="/">Hidden</a></li></ul><a href="/">Unrelated</a>'
    assert RowLinks(html).links == []


def test_directory_remains_available_when_no_margins_can_be_ranked():
    from product.nz_election.pipeline.home import directory_links
    html = directory_links({'baseline-2023': {'data': []}, 'candidates': {'data': []}})
    assert RowLinks(html).links == [PREFIX + 'electorates/']
