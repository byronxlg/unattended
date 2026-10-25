# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Offline state transitions from a validated complete preliminary package."""
import argparse
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, night_live
from product.nz_election.pipeline.deployment_guard import require_publication_allowed
from product.nz_election.pipeline.night_seats import official_change
from product.nz_election.pipeline.result_sources import official_results_notice
from product.nz_election.pipeline.sunsets import NIGHT_CLOSE

SETTLED = 'Settled preliminary results'
OFFICIAL = 'Official results'
MODES = {'settled': SETTLED, 'official': OFFICIAL}


def comparison(row, status):
    return dict(election='2026', status=status, reference_version=row['reference_version'],
                date=row['source_updated_local'], seats={p: r['total_seats'] for p, r in row['party_results'].items()})


def sentence(row, built=None):
    if row.get('result_state') == 'official':
        clock = datetime.fromisoformat(row['source_updated_local'])
        return f'{official_results_notice(built, [row])} Updated {clock.day} {clock:%B at %H:%M} (source local time).'
    if row.get('result_state') == 'settled':
        clock = datetime.fromisoformat(row['source_updated_local'])
        return (f'Preliminary results; live updates ended. Last complete count {clock.day} {clock:%B %H:%M} '
                f'(source local time); {official_results_notice(built, [row]).lower()}')
    return row['mode'] + '.'


def validate(row, env, reference):
    state = row.get('result_state')
    if state not in MODES or row['mode'] != MODES[state] or row['rehearsal']:
        raise ValueError('NIGHT_STATE')
    package = row['preliminary_package']
    export.validate_envelope(package, 'night/live/current')
    if len(package['data']) != 1:
        raise ValueError('NIGHT_BASELINE')
    baseline = package['data'][0]
    if baseline.get('mode') != night_live.MODE or 'result_state' in baseline:
        raise ValueError('NIGHT_BASELINE')
    night_live.validate_row(baseline, package, reference)
    plain = {k: v for k, v in row.items() if k not in {'result_state', 'preliminary_package'}}
    if state == 'settled':
        plain['mode'] = night_live.MODE
        if plain != baseline:
            raise ValueError('NIGHT_BASELINE')
        night_live.validate_row(plain, env, reference)
    else:
        night_live.validate_row(plain, env, reference, official=True)
        if official_change(comparison(baseline, 'preliminary'), comparison(row, 'official')) is None:
            raise ValueError('NIGHT_BASELINE')


def transition(envs, state, *, now, captured=None):
    require_publication_allowed(now)
    instant = datetime.fromisoformat(now.replace('Z', '+00:00'))
    if instant < NIGHT_CLOSE:
        raise ValueError('NIGHT_NOT_SETTLED')
    if state not in MODES:
        raise ValueError('NIGHT_STATE')
    current = envs.get('night/live/current')
    if not current or current['data'][0].get('rehearsal'):
        raise ValueError('NIGHT_BASELINE')
    row = current['data'][0]
    if captured is not None:
        try:
            export.timestamp(captured['retrieved_at'])
            retrieved = datetime.fromisoformat(captured['retrieved_at'].replace('Z', '+00:00'))
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ValueError('NIGHT_STATE') from None
        if retrieved > instant:
            raise ValueError('NIGHT_STATE')
    if state == 'settled':
        if row['mode'] != night_live.MODE:
            raise ValueError('NIGHT_STATE')
        loaded = ({k: deepcopy(v['data']) for k, v in envs.items() if k.startswith('night/')},
                  deepcopy(current['source']), deepcopy(current['input_hashes']))
        baseline = deepcopy(current)
    else:
        if row.get('result_state') != 'settled' or captured is None:
            raise ValueError('NIGHT_STATE')
        loaded = night_live.loaded(captured)
        baseline = deepcopy(row['preliminary_package'])
    payloads, sources, hashes = loaded
    result = payloads['night/live/current'][0]
    if state == 'official' and result['mode'] != OFFICIAL:
        raise ValueError('NIGHT_STATE')
    result.update(mode=MODES[state], result_state=state, preliminary_package=baseline)
    for seq in payloads['night/index']:
        seq.pop('files', None)
        if seq['id'] == 'live':
            seq['mode'] = result['mode']
    reference = payloads['night/references/live'][0]
    validate(result, dict(source=sources, input_hashes=hashes), reference)
    return loaded


def prepare(data, out, state, *, now, run_url, captured):
    from product.nz_election.pipeline.daily_refresh import daily_refresh
    envs = export.validate_bundle(data)
    loaded = transition(envs, state, now=now, captured=captured)
    daily_refresh(out, loaders={'night': lambda: loaded}, now=now, run_url=run_url)
    checked = export.validate_bundle(out)
    if checked.get('night/live/current', {}).get('data', [{}])[0].get('result_state') != state:
        raise ValueError('NIGHT_STATE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state', choices=MODES)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--now', required=True)
    parser.add_argument('--run-url', default='offline-verification', help='Producing Actions run URL for reviewed real captures')
    parser.add_argument('--capture', help='Manifest-checked fixture path containing raw XML and retrieval time')
    args = parser.parse_args()
    from product.nz_election.pipeline import fixtures
    captured = json.loads(fixtures.captures(paths={args.capture})[args.capture]) if args.capture else None
    prepare(args.data, args.out, args.state, now=args.now, run_url=args.run_url, captured=captured)
    print('PASS result state: ' + args.state + (' (offline verification)' if args.run_url == 'offline-verification' else ''))


if __name__ == '__main__':
    main()
