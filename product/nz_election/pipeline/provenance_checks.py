"""Check that route footnotes lead directly to relocated source records, without Chromium."""
from html.parser import HTMLParser
from pathlib import Path
from .build import PREFIX


class Records(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = dict(tag=tag, attrs=dict(attrs), text='', children=[])
        for parent in self.stack:
            parent['children'].append(node)
        self.elements.append(node)
        if tag not in {'meta', 'link', 'img', 'input', 'br', 'hr', 'path', 'use'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        for node in self.stack:
            node['text'] += text


def check_site(site, envs):
    methods = Records((site / 'methods/index.html').read_text())
    anchors = {n['attrs']['id']: n for n in methods.elements if 'id' in n['attrs']}
    checked = 0
    for page in sorted((site / 'electorates').glob('*/index.html')):
        doc = Records(page.read_text())
        note = next(n for n in doc.elements if n['attrs'].get('id') == 'source-candidates-2026')
        target = PREFIX + 'methods/#home-candidates-2026'
        assert any(n['attrs'].get('href') == target for n in note['children']), 'PROVENANCE_LOCATION: candidate footnote'
        from .snapshot_views import load
        snapshot = anchors['home-candidates-2026']
        for candidate in load('candidates-2026'):
            assert candidate['name'] in snapshot['text'], 'PROVENANCE_LOCATION: snapshot identity'
            assert any(n['attrs'].get('href') == candidate['source_url'] for n in snapshot['children']), 'PROVENANCE_LOCATION: snapshot source'
        records = anchors['records-candidates']['text']
        for row in envs['candidates']['data']:
            for field in ('name', 'party_id'):
                for ref in row['field_sources'][field]:
                    assert ref['locator'] not in doc.elements[0]['text'], 'PROVENANCE_LOCATION: candidate locator on route'
                    assert ref['locator'] in records, 'PROVENANCE_LOCATION: missing candidate record'
        checked += 1
    polls = Records((site / 'polls/index.html').read_text())
    note = next(n for n in polls.elements if n['attrs'].get('id') == 'source-history')
    assert any(n['attrs'].get('href') == PREFIX + 'methods/#source-history' for n in note['children']), 'PROVENANCE_LOCATION: poll footnote'
    assert 'source-history' in anchors
    recent = sorted(envs['polls']['data'], key=lambda p: (p['fieldwork_end'], p['id']), reverse=True)[:10]
    table = next(n for n in polls.elements if n['attrs'].get('id') == 'recent-polls')
    for poll in envs['polls']['data']:
        record = anchors['source-' + poll['id']]
        assert record in anchors['source-history']['children'], 'PROVENANCE_LOCATION: records outside target'
        assert poll['pollster'] in record['text'] and 'Fieldwork ended' in record['text']
        for url in poll['reference_urls']:
            assert any(n['attrs'].get('href') == url for n in record['children']), 'PROVENANCE_LOCATION: missing poll report'
            if poll in recent:
                assert any(n['attrs'].get('href') == url for n in table['children']), 'PROVENANCE_LOCATION: recent poll report missing'
    assert checked, 'PROVENANCE_LOCATION: no electorate routes'
    return checked + 1


if __name__ == '__main__':
    import argparse
    from .export import validate_bundle
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS provenance locations: {check_site(args.site, validate_bundle(args.site / "data"))} routes')
