"""Resolve every local fragment against its built target in every browser design state."""
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import pytest

from product.nz_election.tests.design_checks import Document, PREFIX
from product.nz_election.tests.design_states import STATES, fixture


def broken_fragments(site):
    pages = {p.relative_to(site).as_posix(): Document(p.read_text()).nodes
             for p in Path(site).rglob('index.html')}
    ids = {name: {attrs['id'] for _, attrs in nodes if 'id' in attrs}
           for name, nodes in pages.items()}
    broken = []
    for name, nodes in pages.items():
        for tag, attrs in nodes:
            if tag not in {'a', 'link'} or 'href' not in attrs:
                continue
            target = urlsplit(urljoin(PREFIX + name, attrs['href']))
            if target.scheme or target.netloc or not target.fragment:
                continue
            path = unquote(target.path)
            if not path.startswith(PREFIX):
                broken.append((name, attrs['href']))
                continue
            path = path.removeprefix(PREFIX)
            if path.endswith('/'):
                path += 'index.html'
            if path.endswith('.html') and unquote(target.fragment) not in ids.get(path, set()):
                broken.append((name, attrs['href']))
    return broken


@pytest.mark.parametrize('state', STATES)
def test_every_design_state_resolves_local_fragments(tmp_path, state):
    site, _ = fixture(tmp_path, state)
    root = site / 'nz-election'
    assert len(list(root.rglob('index.html'))) == 81
    assert not (broken := broken_fragments(root)), f'BROKEN_FRAGMENT: {state}: {broken}'


def test_fragment_check_resolves_target_not_linking_page(tmp_path):
    (tmp_path / 'polls').mkdir()
    (tmp_path / 'index.html').write_text(
        '<p id="missing">Home only</p><a href="polls/#missing">Broken</a>'
        '<a href="polls/#M%C4%81ori">Encoded</a><a href="#missing">Local</a>'
        '<a href="https://example.org/#missing">External</a>')
    (tmp_path / 'polls/index.html').write_text('<p id="Māori">Target</p>')
    assert broken_fragments(tmp_path) == [('index.html', 'polls/#missing')]
