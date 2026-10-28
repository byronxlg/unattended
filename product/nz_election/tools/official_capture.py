# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Acquire and preflight an official capture against a pinned settled bundle."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import time

sys.dont_write_bytecode = True
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from product.nz_election.pipeline import export, fetch, fixtures, night_live, result_sources, result_states

PATHS = (*night_live.REFERENCES, 'election.xml', *(f'e{n:02}/e{n:02}.xml' for n in range(1, 72)))
CAPTURE = 'result-import/2026-11-27-official.json'
PASS = 'PASS official capture: 75 files, 71 electorates; official state accepted; review required'


class CaptureError(ValueError):
    pass


def require_date(stamp):
    if not result_sources.official_date_reached(stamp):
        raise CaptureError('OFFICIAL_NOT_DUE')


def preflight(data, captured, *, now):
    """Check immutable file evidence before parsing and use the import's validator."""
    try:
        require_date(now)
        source = captured.get('acquisition_source')
        if source != result_sources.source('official'):
            raise CaptureError('OFFICIAL_SOURCE')
        raw, files = captured['raw'], captured['files']
        if type(raw) is not dict or type(files) is not dict or set(raw) != set(PATHS) or set(files) != set(PATHS):
            raise CaptureError('OFFICIAL_INCOMPLETE')
        require_date(captured['retrieved_at'])
        for path in PATHS:
            entry = files[path]
            if entry['acquisition_source'] != source or entry['url'] != result_sources.ROOTS['official'] + path:
                raise CaptureError('OFFICIAL_SOURCE')
            if entry['sha256'] != export.digest(raw[path].encode('utf-8')):
                raise CaptureError('OFFICIAL_CHECKSUM')
            stamp = entry['retrieved_at']
            require_date(stamp)
            export.timestamp(stamp)
            if not stamp.endswith('Z') or not stamp <= captured['retrieved_at'] <= now:
                raise CaptureError('OFFICIAL_CLOCK')
        envs = export.validate_bundle(data)
        baseline = envs['night/live/current']['data'][0]
        if baseline.get('result_state') != 'settled':
            raise CaptureError('OFFICIAL_BASELINE')
        # Compare exact reference bytes before parsing to classify even registry drift.
        if any(raw[p] != baseline['raw_xml'][p] for p in night_live.REFERENCES):
            raise CaptureError('OFFICIAL_REFERENCE_DRIFT')
        try:
            _, row = night_live.parsed(raw)
        except ValueError as exc:
            if str(exc) == 'XML_TOTAL':
                raise CaptureError('OFFICIAL_TOTALS') from None
            raise
        details = list(row['leaders'].values())
        if (any(sum(d['party_votes'].get(p, 0) for d in details) != row['party_results'].get(p, {}).get('votes', 0)
                for p in set(row['party_results']) | {p for d in details for p in d['party_votes']})
                or any(sum(d['statistics'][key] for d in details) != row['statistics'][key]
                       for key in ('total_votes_cast', 'total_voting_places_counted'))):
            raise CaptureError('OFFICIAL_TOTALS')
        # prepare also validates the complete emitted bundle, as the import does.
        with tempfile.TemporaryDirectory(prefix='official-preflight-') as tmp:
            result_states.prepare(data, Path(tmp) / 'data', 'official', now=now,
                                  run_url='offline-verification', captured=captured)
    except CaptureError:
        raise
    except Exception:
        raise CaptureError('OFFICIAL_PREFLIGHT_FAILED') from None


def prepare(data, out, base_url, *, transport=fetch.http, sleep=time.sleep,
            now=lambda: datetime.now(timezone.utc)):
    try:
        require_date(night_live.stamp(now))
        if type(base_url) is not str or base_url != result_sources.ROOTS['official']:
            raise CaptureError('OFFICIAL_SOURCE')
        out = Path(out)
        if (out.resolve().is_relative_to(Path(data).resolve())
                or out.resolve().is_relative_to(fixtures.ROOT.resolve())):
            raise CaptureError('OFFICIAL_OUTPUT')
        if out.exists() or out.is_symlink():
            raise CaptureError('OFFICIAL_OUTPUT')
        # Reject an invalid baseline before any network request.
        envs = export.validate_bundle(data)
        if envs.get('night/live/current', {}).get('data', [{}])[0].get('result_state') != 'settled':
            raise CaptureError('OFFICIAL_BASELINE')
        source = result_sources.source('official')
        raw, files = {}, {}
        for path in PATHS:
            body = fetch.official_xml(base_url, path, transport=transport, sleep=sleep, now=now)
            raw[path] = body.decode('utf-8')
            files[path] = dict(url=base_url + path, retrieved_at=night_live.stamp(now),
                               sha256=export.digest(body), acquisition_source=source)
        captured = dict(raw=raw, files=files, retrieved_at=night_live.stamp(now), acquisition_source=source)
        preflight(data, captured, now=night_live.stamp(now))
        content = (json.dumps(captured, ensure_ascii=False, indent=2) + '\n').encode()
        draft = dict(path=CAPTURE, sha256=export.digest(content), bytes=len(content),
                     retrieved_at=captured['retrieved_at'], url=source['url'], source=source,
                     licence='Copyright Electoral Commission; no open licence stated.',
                     capture_kind='unreviewed', reviewer='',
                     baseline_manifest_sha256=export.digest((Path(data) / 'manifest.json').read_bytes()))
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.official-', dir=out.parent) as tmp:
            stage = Path(tmp) / 'capture'
            (stage / 'result-import').mkdir(parents=True)
            (stage / CAPTURE).write_bytes(content)
            (stage / 'manifest-draft.json').write_text(json.dumps(draft, indent=2) + '\n')
            if out.exists() or out.is_symlink():
                raise CaptureError('OFFICIAL_OUTPUT')
            stage.rename(out)
        return draft
    except CaptureError:
        raise
    except fetch.FetchError as exc:
        raise CaptureError(exc.code) from None
    except Exception:
        raise CaptureError('OFFICIAL_CAPTURE_FAILED') from None


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CaptureError('OFFICIAL_ARGUMENTS')


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--base-url', required=True)
    try:
        args = parser.parse_args(argv)
        prepare(args.data, args.out, args.base_url)
    except CaptureError as exc:
        raise SystemExit(str(exc)) from None
    print(PASS)


if __name__ == '__main__':
    main()
