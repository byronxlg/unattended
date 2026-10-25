"""Caption text cannot become punctuation-only flex items."""
from html.parser import HTMLParser

import pytest

from product.nz_election.pipeline.parties_page import page
from product.nz_election.tests.test_parties_page import BUILT, averages


class SourceText(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag not in {'img', 'path', 'circle'}:
            self.stack.append('source-actions' in dict(attrs).get('class', '').split())

    def handle_endtag(self, tag):
        if tag not in {'img', 'path', 'circle'}:
            self.stack.pop()

    def handle_data(self, text):
        if any(self.stack) and text.strip():
            self.text.append(text.strip())


@pytest.mark.parametrize('offline', [False, True])
def test_parties_source_text_has_no_orphan_punctuation(offline):
    env = {'data': averages()}
    if offline:
        env['run_url'] = 'offline-verification'
    html = page({'averages': env}, BUILT)
    texts = SourceText(html).text
    assert any('Square crop' in text for text in texts)
    assert any('5% qualifies' in text for text in texts)
    assert not [text for text in texts if text.startswith(('.', '/'))]
    assert ('Offline verification, not live data.' in texts) == offline
