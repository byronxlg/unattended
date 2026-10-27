"""Inspect the supplied feed and moved polls page, including source/fragment contracts."""
from .build import config, PREFIX
from .home import watch_rows
from product.nz_election.tests.design_checks import Document, provenance

MODULES = ('dates', 'seats', 'parties', 'trend', 'polls', 'electorates', 'thresholds', 'night')
ORDER = ('dates', 'night-summary', 'seats', 'parties', 'trend', 'polls', 'electorates', 'thresholds', 'night')


def check_site(site, envs):
    from .verify import require
    home = (site / 'index.html').read_text()
    polls = (site / 'polls/index.html').read_text()
    provenance(home)
    provenance(polls)
    from .home import night_summary
    from .build import home_presentation
    import json
    built = json.loads((site / 'build-manifest.json').read_text())['data']['built_at']
    top = 'night-summary' if night_summary(envs, built) else 'seats' if home_presentation(envs, built)['result'] else None
    averages, polls_data = envs.get('averages', {}).get('data'), envs.get('polls', {}).get('data')
    expected_modules = (['dates'] + ([top] if top else []) + (['parties', 'trend'] if averages else [])
                        + (['polls'] if averages and polls_data else []) + ['electorates'])
    actual_modules = [a['id'] for tag, a in Document(home).nodes if tag == 'section']
    # Thresholds and key dates are data-dependent; the dates module leaves once polls close.
    optional = {'thresholds', 'night'}
    require([m for m in actual_modules if m not in optional] == expected_modules
            and actual_modules == [m for m in ORDER if m in actual_modules]
            and not (top == 'night-summary' and 'night' in actual_modules), 'home module order')
    require(home.count('<h1') == 1, 'home heading')
    from .scripts import validate_scripts
    validate_scripts(home)
    require('allocator.mjs' not in home and '<fieldset' not in home and ('id="trend"' in home) == bool(envs.get('averages', {}).get('data')), 'home trend without interactive explorer')
    ids = {a['id'] for _, a in Document(polls).nodes if 'id' in a}
    require({'main', 'seats', 'polls', 'explorer', 'source-seats', 'source-thresholds'} <= ids, 'poll anchors')
    require({'coalition-explorer', 'coalition-title', 'source-history', 'source-average', 'source-grouping', 'source-trend'} <= ids,
            'legacy fragment inventory: resolves even without poll data')
    require('<script' not in polls and '<fieldset' not in polls, 'polls answers are server-rendered')
    if 'polls' in envs:
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
        closest = watch.split('<ol class="closest">')[1].split('</ol>')[0] if '<ol class="closest">' in watch else ''
        items = closest.split('</li>')[:-1]
        require(len(items) == len(watch_rows(envs)), 'watch selection size')
        require(all(f'<b>{margin:,}</b>' in item and f'href="{PREFIX}electorates/{r["slug"]}/"' in item
                    for item, (margin, _, r, text) in zip(items, watch_rows(envs))), 'watch joins')
    require('incumbent' not in home.lower(), 'no inferred incumbents')
    expected = {r['path'] + 'index.html' for r in config('routes')} | {'electorates/' + r['slug'] + '/index.html' for r in config('electorates')}
    require(len(expected) == 82 and {p.relative_to(site).as_posix() for p in site.rglob('index.html')} == expected, '82 exact routes')
    for path in site.rglob('index.html'):
        html = path.read_text()
        nav = html.split('<header>')[1].split('</header>')[0]
        require(nav.count(f'<a href="{PREFIX}"') == 1 and nav.count(f'<a href="{PREFIX}polls/"') == int(bool(envs.get('polls', {}).get('data'))), 'visible route navigation')
        require('aria-label="Home sections"' not in html, 'single route navigation')
