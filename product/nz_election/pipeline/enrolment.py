"""Dated roll evidence; national age tables do not establish electorate totals."""
from datetime import datetime
from html.parser import HTMLParser
import re
from . import daily_sources as ds
from .refresh import config


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def observation(raw):
    parser = Text()
    parser.feed(raw.decode('utf-8'))
    text = ' '.join(' '.join(parser.parts).split())
    match = re.search(r'Enrolment statistics as at (\d{1,2} [A-Za-z]+ \d{4})', text)
    if not match or 'Total' not in text or 'Roll' not in text:
        return None
    return datetime.strptime(match[1], '%d %B %Y').date().isoformat()


def load():
    paths = {f'ec-2026/wayback-enrolment-{kind}.html' for kind in ('general', 'maori')}
    raw, sources, hashes = ds.inputs(paths)
    rows = []
    for electorate in config('electorates'):
        path = f'ec-2026/wayback-enrolment-{electorate["kind"]}.html'
        as_of = observation(raw[path])
        refs = ds.refs(path, 'Enrolment statistics as at; national age table (name=all)', ['as_of', 'roll_basis'])
        rows.append(dict(id='enrolment-' + electorate['id'], electorate_id=electorate['id'], as_of=as_of,
                         observed_at=as_of, enrolled=None, eligible=None,
                         roll_basis=('National ' + ('Māori' if electorate['kind'] == 'maori' else 'general') +
                                     ' roll age table; electorate total unavailable.') if as_of else None,
                         field_sources=refs, source_ref=refs))
    return {'enrolment': rows}, sources, hashes
