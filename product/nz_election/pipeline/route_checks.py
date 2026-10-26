"""Verify route cards against registered routes and the supplied built pages."""
import json
from html import escape
from .build import config, home_presentation, PREFIX
from .route_cards import route_key, summary, ORIGIN, card as render_card
from product.nz_election.tests.design_checks import Document, provenance


def registered():
    return config('routes') + [dict(path='electorates/' + r['slug'] + '/', label=r['name']) for r in config('electorates')]


def check_site(site, envs):
    from .verify import require
    routes = registered()
    cards = json.loads((site / 'og-manifest.json').read_text())
    require(len(cards) == len(routes) == 81, 'OG count')
    require({c['route'] for c in cards} == {r['path'] for r in routes}, 'OG routes')
    require(len({c['key'] for c in cards}) == 81, 'unique OG keys')
    built = json.loads((site / 'build-manifest.json').read_text())['data']['built_at']
    home = home_presentation(envs, built)
    for route in routes:
        path = route['path']
        card = next(c for c in cards if c['route'] == path)
        key = route_key(path)
        title, description = summary(route, envs, home, built)
        require(card == dict(route=path, key=key, title=title, description=description, html='og/' + key + '.html', png='og/' + key + '.png'), 'OG manifest content')
        html = (site / path / 'index.html').read_text()
        provenance(html)
        require('<title>' + escape(title) + ' | NZ election 2026</title>' in html, 'route title')
        meta = {a.get('property', a.get('name')): a.get('content') for tag, a in Document(html).nodes if tag == 'meta'}
        expected = {'description': description, 'og:title': title, 'og:description': description,
                    'og:image': ORIGIN + PREFIX + card['png'], 'twitter:image': ORIGIN + PREFIX + card['png'],
                    'og:image:width': '1200', 'og:image:height': '630', 'twitter:card': 'summary_large_image'}
        require(all(meta.get(k) == v for k, v in expected.items()), 'route metadata')
        og = (site / card['html']).read_text()
        provenance(og)
        require(og == render_card(route, envs, home, built), 'OG document content')
        require('<h1 ' in og and 'source-note' in og, 'OG content and source')
        if path == 'night/':
            from .night_page import page
            require('No publication between 00:00 and 19:00 NZDT on election day, under Electoral Act s197.' in html
                    and 'href="https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM310065.html"' in html,
                    'night publication freeze notice')
            require(page(envs, built) in html, 'night packaged results or absent countdown')
        if path.startswith('electorates/') and path != 'electorates/':
            row = next(r for r in envs.get('electorates', {}).get('data', config('electorates')) if path == 'electorates/' + r['slug'] + '/')
            from .electorate_pages import candidate_cards
            from .home_graphics import hex_map
            from .snapshot_views import load, result
            from .electorate_locator import LOCATOR_BYTE_CAP
            require(candidate_cards(row) in html, 'reconciled candidates and explicit incumbent flags')
            require('class="electorate-page"' in html, 'electorate overview')
            graphic, _ = hex_map(envs, load('hexmap'), {r['slug']: r for r in config('electorates')},
                                 lambda r: result(r, envs), selected=row['slug'])
            require(graphic in html and len(graphic.encode()) < LOCATOR_BYTE_CAP,
                    'shared hex locator within byte cap')
            require('id="source-boundaries-2025"' in html and 'CC BY 4.0' in html, 'locator provenance')
            require(html.index('class="race-cards"') < html.index('enrolled-electorate"'), 'candidate-first order')
            require('aria-current="location"' in graphic and f'data-electorate="{row["slug"]}"' in graphic, 'selected electorate')
            require('class="tile-map"' not in html and 'Local polls' not in html and '<h2>Enrolment' not in html,
                    'only accepted page answers')
            require('id="source-baseline-2023"' in html, 'baseline fragment preserved')



def check_images(site):
    """Deployment gate: every registered page must reference its existing 1200x630 PNG."""
    import struct
    from .verify import require
    for route in registered():
        relative = 'og/' + route_key(route['path']) + '.png'
        meta = {a.get('property', a.get('name')): a.get('content') for tag, a in Document((site / route['path'] / 'index.html').read_text()).nodes if tag == 'meta'}
        require(all(meta.get(k) == ORIGIN + PREFIX + relative for k in ('og:image', 'twitter:image')), 'OG image reference')
        image = site / relative
        require(image.is_file(), 'missing OG image: ' + relative)
        data = image.read_bytes()
        require(data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR' and struct.unpack('>II', data[16:24]) == (1200, 630), 'OG PNG dimensions')
