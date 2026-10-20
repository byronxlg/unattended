"""Bound seat-note content before the phone fold, without a browser layout engine."""
from html.parser import HTMLParser
from pathlib import Path


class SeatNote(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = self.paragraphs = self.actions = self.links = self.notes = 0
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div':
            if self.depth or attrs.get('id') == 'source-seats':
                if not self.depth:
                    self.notes += 1
                self.depth += 1
        if self.depth:
            self.paragraphs += tag == 'p'
            self.links += tag == 'a'
            self.actions += tag == 'p' and 'source-actions' in attrs.get('class', '').split()

    def handle_endtag(self, tag):
        if tag == 'div' and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)


def check_markup(html):
    note = SeatNote(html)
    size = len(' '.join(' '.join(note.text).split()))
    if note.notes != 1 or note.paragraphs > 2 or note.actions != 1 or note.links > 6 or size > 320:
        raise ValueError(f'SOURCE_NOTE_CONTENT_BUDGET: notes={note.notes}, paragraphs={note.paragraphs}, '
                         f'actions={note.actions}, links={note.links}, characters={size}; '
                         'expected one note, at most two paragraphs, one action row, six links, 320 characters')
    return dict(paragraphs=note.paragraphs, links=note.links, characters=size)


def check_site(site):
    html = (site / 'index.html').read_text()
    results = {'index.html': check_markup(html)} if 'id="home-seats"' in html else {}
    polls = (site / 'polls/index.html').read_text()
    # The harness's earlier-coherent-window fixture renders the seat hero on polls/.
    if 'class="seat-figure"' in polls:
        results['polls/index.html'] = check_markup(polls)
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    print(f'PASS source-note budgets: {check_site(args.site)}')
