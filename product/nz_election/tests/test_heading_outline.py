"""Check the screenshot harness heading contract without launching a browser."""
from html.parser import HTMLParser

from product.nz_election.pipeline.build import config
from product.nz_election.tests.test_home import populated  # noqa: F401


class MainHeadings(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_main = False
        self.template_depth = 0
        self.levels = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'template':
            self.template_depth += 1
        if self.template_depth:
            return
        if tag == 'main':
            self.in_main = True
        if self.in_main and tag in ('h1', 'h2', 'h3', 'h4'):
            self.levels.append(int(tag[1]))

    def handle_endtag(self, tag):
        if tag == 'template':
            self.template_depth -= 1
        elif tag == 'main' and not self.template_depth:
            self.in_main = False


def test_populated_routes_heading_outline(populated):
    _, site = populated
    routes = {r['path'] for r in config('routes')}
    routes.update(f'electorates/{e["slug"]}/' for e in config('electorates'))
    pages = {p.parent.relative_to(site).as_posix().replace('.', '') + '/'
             for p in site.rglob('index.html')}
    assert pages == {route or '/' for route in routes}
    failures = {}
    for route in sorted(routes):
        levels = MainHeadings((site / route / 'index.html').read_text()).levels
        assert levels, f'{route}: no main headings'
        if not all(b <= a + 1 for a, b in zip(levels, levels[1:])):
            failures[route] = levels
    assert not failures, f'HEADING_OUTLINE: {failures}'
