"""Inspect the supplied feed and moved polls page, including source/fragment contracts."""
from .build import config, PREFIX
from .home import watch_rows
from product.nz_election.tests.design_checks import Document, provenance

MODULES = ('seats', 'polls', 'trend', 'electorates', 'thresholds', 'markets', 'night', 'more')


def check_site(site, envs):
    from .verify import require
    home = (site / 'index.html').read_text()
    polls = (site / 'polls/index.html').read_text()
    provenance(home)
    provenance(polls)
    positions = [home.index(f'<section id="{name}"') for name in MODULES]
    require(positions == sorted(positions), 'home module order')
    require(home.count('<h1') == 1 and 'Who is favoured to form the next government?' in home, 'home heading')
    require('coalitions.mjs' not in home and 'How have the polls moved?' in home, 'home trend without interactive explorer')
    ids = {a['id'] for _, a in Document(polls).nodes if 'id' in a}
    require({'main', 'seats', 'polls', 'explorer', 'source-seats', 'source-thresholds'} <= ids, 'poll anchors')
    if 'polls' in envs:
        require({'coalition-explorer', 'coalition-title', 'source-history', 'source-average'} <= ids, 'legacy fragment inventory')
        require(all({r['id'], 'source-' + r['id']} <= ids for r in envs['polls']['data']), 'published poll fragment inventory')
    for _, attrs in Document(polls).nodes:
        if attrs.get('href', '').startswith('#'):
            require(attrs['href'][1:] in ids, 'poll fragment link')
    from product.nz_election.tools.measure_home import measure
    measure(site / 'index.html')
    sources = (site / 'methods/index.html').read_text()
    source_ids = {a['id'] for _, a in Document(sources).nodes if 'id' in a}
    for tag, attrs in Document(home).nodes:
        if tag == 'figure':
            require(attrs.get('id') in source_ids, 'home figure provenance entry')
            require(f'methods/#{attrs["id"]}' in home, 'one-click figure provenance')
    directory = (site / 'electorates/index.html').read_text()
    require(all(PREFIX + 'electorates/' + r['slug'] + '/' in directory for r in config('electorates')), 'directory identity')
    if 'baseline-2023' in envs and 'candidates' in envs:
        watch = home.split('<section id="electorates"')[1].split('</section>')[0]
        require(watch.count('<tr>') == len(watch_rows(envs)) + 1, 'watch selection size')
        require(all(f'{margin:,} votes' in watch and PREFIX + 'electorates/' + r['slug'] + '/' in watch for margin, _, r, text in watch_rows(envs)), 'watch joins')
    require('incumbent' not in home.lower(), 'no inferred incumbents')
    require(len(home.encode()) + (site / 'styles.css').stat().st_size < 200_000, 'home byte budget')
    require((site / 'styles.css').stat().st_size < 16_000, 'CSS budget')
    expected = {r['path'] + 'index.html' for r in config('routes')} | {'electorates/' + r['slug'] + '/index.html' for r in config('electorates')}
    require(len(expected) == 79 and {p.relative_to(site).as_posix() for p in site.rglob('index.html')} == expected, '79 exact routes')
    for path in site.rglob('index.html'):
        html = path.read_text()
        nav = html.split('<header>')[1].split('</header>')[0]
        require(nav.count(f'<a href="{PREFIX}"') == 1 and nav.count(f'<a href="{PREFIX}polls/"') == 1, 'visible route navigation')
        require(('aria-label="Home sections"' in html) == (path == site / 'index.html'), 'home-only sections')
