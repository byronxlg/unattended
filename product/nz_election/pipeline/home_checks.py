"""Inspect the supplied feed and moved polls page, including source/fragment contracts."""
from .build import config, PREFIX
from .home import watch_rows
from product.nz_election.tests.design_checks import Document, provenance

MODULES = ('seats', 'polls', 'electorates', 'directory', 'social', 'method')


def check_site(site, envs):
    from .verify import require
    home = (site / 'index.html').read_text()
    polls = (site / 'polls/index.html').read_text()
    provenance(home)
    provenance(polls)
    positions = [home.index(f'<section id="{name}"') for name in MODULES]
    require(positions == sorted(positions), 'home module order')
    require(home.count('<h1') == 1 and 'New Zealand votes on 7 November 2026' in home, 'home heading')
    require('coalitions.mjs' not in home and 'Poll history' not in home, 'poll detail only on polls')
    ids = {a['id'] for _, a in Document(polls).nodes if 'id' in a}
    require({'main', 'seats', 'polls', 'explorer', 'source-seats', 'source-thresholds'} <= ids, 'poll anchors')
    if 'polls' in envs:
        require({'coalition-explorer', 'coalition-title', 'source-history', 'source-average'} <= ids, 'legacy fragment inventory')
        require(all({r['id'], 'source-' + r['id']} <= ids for r in envs['polls']['data']), 'published poll fragment inventory')
    for _, attrs in Document(polls).nodes:
        if attrs.get('href', '').startswith('#'):
            require(attrs['href'][1:] in ids, 'poll fragment link')
    def seats(html):
        return html.split('<div class="seat-module">', 1)[1].split('</section>\n', 1)[0]
    require(seats(home) == seats(polls), 'identical shared seats')
    directory = home.split('<section id="directory"')[1].split('</section>')[0]
    require(directory.count('<li>') == 71, 'home directory count')
    require(all(PREFIX + 'electorates/' + r['slug'] + '/' in directory for r in config('electorates')), 'home directory identity')
    if 'baseline-2023' in envs and 'candidates' in envs:
        from html import escape
        watch = home.split('<section id="electorates"')[1].split('</section>')[0]
        require(watch.count('<article>') == len(watch_rows(envs)), 'watch selection size')
        require(all(escape(text) in watch and PREFIX + 'electorates/' + r['slug'] + '/' in watch for _, _, r, text in watch_rows(envs)), 'watch joins')
    require('incumbent' not in home.lower(), 'no inferred incumbents')
    require(len(home.encode()) + (site / 'styles.css').stat().st_size < 200_000, 'home byte budget')
    require((site / 'styles.css').stat().st_size < 12_000, 'CSS budget')
    expected = {r['path'] + 'index.html' for r in config('routes')} | {'electorates/' + r['slug'] + '/index.html' for r in config('electorates')}
    require(len(expected) == 79 and {p.relative_to(site).as_posix() for p in site.rglob('index.html')} == expected, '79 exact routes')
    for path in site.rglob('index.html'):
        html = path.read_text()
        nav = html.split('<header>')[1].split('</header>')[0]
        require(nav.count(f'<a href="{PREFIX}"') == 2 and nav.count(f'<a href="{PREFIX}polls/"') == 2, 'both navigation copies')
        require(('aria-label="Home sections"' in html) == (path == site / 'index.html'), 'home-only sections')
