"""Fixtures cover all twelve design states, including explorer rejection variants."""
from copy import deepcopy
import re

from product.nz_election.pipeline import export, coalitions
from product.nz_election.pipeline.build import build, config
from product.nz_election.pipeline.daily_refresh import daily_refresh
from product.nz_election.pipeline.refresh import refresh
from product.nz_election.pipeline.models import ParseDrift

STATES = ('unavailable', 'stale', 'incomplete', 'earlier-coherent-window',
          'coalition-edit', 'coalition-vacancy', 'invalid-count', 'invalid-link',
          'changed-inputs', 'missing-baseline', 'unresolved', 'validation-error',
          'no-data', 'allocation-tie', 'source-conflict', 'offline')
CATEGORIES = {'loading': 'coalition-edit', 'no-data': 'no-data', 'overdue': 'stale',
              'failed': 'validation-error', 'unavailable': 'unavailable', 'seats-unavailable': 'incomplete',
              'explorer-rejection': 'invalid-count', 'allocation-tie': 'allocation-tie',
              'source-conflict': 'source-conflict', 'missing': 'missing-baseline',
              'unmatched': 'unresolved', 'offline': 'offline'}
COHERENT = {'earlier-coherent-window', 'coalition-edit', 'coalition-vacancy',
            'invalid-count', 'invalid-link', 'changed-inputs'}


def fixture(root, state):
    data, site = root / (state + '-data'), root / state
    site.mkdir()
    def fail(*args):
        raise ParseDrift('Controlled failed validation')
    if state == 'no-data':
        build(data, site / 'nz-election', built='2026-10-17T01:00:00Z')
        return site, ''
    refresh(data, now='2026-10-17T01:00:00Z', end_date='2026-07-18' if state in COHERENT else None,
            **({'parse': fail} if state == 'unavailable' else {}),
            run_url='local-stale-verification' if state == 'stale' else 'offline-verification')
    if state in {'incomplete', 'allocation-tie'}:
        from product.nz_election.tests.test_build import rewrite
        def omit_named_party(rows):
            max(rows, key=lambda p: p['fieldwork_end'])['shares']['nat'] = None
        rewrite(data, omit_named_party)
    if state == 'validation-error':
        refresh(data, now='2026-10-17T02:00:00Z', parse=fail, run_url='https://github.com/example/repo/actions/runs/1')
    if state in {'missing-baseline', 'unresolved', 'source-conflict'}:
        daily_refresh(data, now='2026-10-17T01:00:00Z')
    build(data, site / 'nz-election', built='2026-10-17T12:00:00Z' if state in {'stale', 'validation-error'} else '2026-10-17T01:00:00Z')
    route = 'polls/' if state in COHERENT else ''
    if state in {'missing-baseline', 'source-conflict'}:
        from product.nz_election.pipeline.electorate_pages import detail
        row = next(r for r in config('electorates') if r['slug'] == 'auckland-central')
        envs = deepcopy(export.validate_bundle(data))
        old = next(r for r in envs['baseline-2023']['data'] if r['old_electorate_id'] == 1)
        if state == 'missing-baseline':
            old['candidate_votes'] = None
            old['field_sources']['candidate_status'] = 'Missing candidate capture.'
        else:
            row = dict(row, baseline_ids=[], mapping_status='unresolved')
        route = 'electorates/auckland-central/'
        target = site / 'nz-election' / route / 'index.html'
        html = target.read_text()
        html = re.sub(r'(<main[^>]*>).*?(</main>)', lambda m: m[1] + '<h1>Auckland Central</h1>' + detail(row, envs) + m[2], html, flags=re.S)
        target.write_text(html)
    if state == 'unresolved':
        route = 'electorates/'
    if state == 'invalid-link':
        route = 'polls/#coalition=invalid'
    if state == 'changed-inputs':
        envs = export.validate_bundle(data)
        inputs = coalitions.inputs(envs['averages']['data'][-1], envs['seats']['data'], 'b' * 64)
        route = 'polls/' + coalitions.encode(inputs['initial'])
    if state == 'offline':
        route = 'downloads/'
    if state == 'allocation-tie':
        from product.nz_election.pipeline.build import polls_page
        envs = export.validate_bundle(data)
        from product.nz_election.pipeline.allocator import entitlement
        envs['seats']['data']['unresolved_ties'] = entitlement({'nat': 1, 'lab': 1}, ['nat', 'lab'], count=1)['unresolvedTies']
        target = site / 'nz-election/index.html'
        html = target.read_text()
        body = polls_page(envs, '2026-10-17T01:00:00Z')
        target.write_text(re.sub(r'(<main[^>]*>).*?(</main>)', lambda m: m[1] + '<h1>No seat estimate available yet.</h1>' + body + m[2], html, flags=re.S))
    return site, route
