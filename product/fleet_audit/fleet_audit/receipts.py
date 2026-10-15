"""Bounded final physical line parsing for ticks_jsonl version 1."""
import json
import re
from dataclasses import replace
from datetime import datetime, timezone

from .models import Error, ReceiptData
from .output import age


def read_tail(path, files, limit=65536):
    return files.read_tail(path, limit)


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z') if parsed.utcoffset() is not None else None
    except ValueError:
        return None


def normalize_tick(value):
    if not isinstance(value, dict):
        return ReceiptData(parsing_errors=('receipt must be an object',))
    ts = timestamp(value.get('ts'))
    errors = [] if ts is not None else ['invalid receipt ts']
    supervisor = value.get('supervisor')
    if not isinstance(supervisor, dict):
        return ReceiptData(ts=ts, parsing_errors=tuple(errors + ['missing supervisor mapping']))
    ran, rc, error, result = (supervisor.get(k) for k in ('ran', 'rc', 'error', 'result'))
    if type(ran) is not bool:
        errors.append('invalid ran')
    if 'rc' not in supervisor or not (rc is None or type(rc) is int or isinstance(rc, str) and re.fullmatch(r'[+-]?[0-9]+', rc)):
        errors.append('invalid rc')
    elif isinstance(rc, str):
        try:
            rc = int(rc)
        except ValueError:
            errors.append('invalid rc')
    if 'error' not in supervisor or error is not None and not isinstance(error, str):
        errors.append('invalid error')
    # Decision 4 allows absent result: free text never establishes semantic success.
    if result is not None and not isinstance(result, str):
        errors.append('invalid result')
    outcome = 'unestablished'
    if not errors:
        if ran is False:
            outcome = 'completed' if error is None or error.startswith('skipped:') else 'failed'
        elif error is not None or rc is not None and rc != 0:
            outcome = 'failed'
        elif rc == 0:
            outcome = 'completed'
    # Unknown producer keys are discarded so receipt text cannot become collection input.
    safe = {'ts': ts, 'supervisor': {'ran': ran if type(ran) is bool else None,
                                   'rc': rc if type(rc) is int else None,
                                   'error': error if isinstance(error, str) else None,
                                   'result': result if isinstance(result, str) else None}}
    return ReceiptData(last_object=safe, ts=ts, ran=safe['supervisor']['ran'], rc=safe['supervisor']['rc'],
                       error=safe['supervisor']['error'], result=safe['supervisor']['result'],
                       outcome=outcome, parsing_errors=tuple(errors))


def parse_receipt(tail):
    data = tail.data
    if tail.error is not None or data is None:
        return replace(tail, data=ReceiptData(path=data.path if data else '', tail=data))
    try:
        if data.changed or data.before != data.after or data.after != data.path_after:
            raise ValueError('receipt changed during read')
        if not all(meta.regular for meta in (data.before, data.after, data.path_after)):
            raise ValueError('not a regular file')
        raw = data.tail_bytes
        if (len(raw) > 65536 or data.bytes_read != len(raw)
                or data.bytes_read != data.before.size - data.offset):
            raise ValueError('receipt tail exceeds bounds')
        raw = raw[:-1] if raw.endswith(b'\n') else raw
        if b'\n' not in raw and not data.starts_at_line_boundary:
            raise ValueError('final line extends beyond retained tail')
        line = raw.rsplit(b'\n', 1)[-1]
        if not line.strip():
            raise ValueError('blank final line')
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError('duplicate JSON key')
                result[key] = value
            return result
        def constant(value):
            raise ValueError('invalid JSON constant')
        value = json.loads(line.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
        if not isinstance(value, dict):
            raise ValueError('receipt must be an object')
        receipt = normalize_tick(value)
        receipt = replace(receipt, path=data.path, tail=data, age_seconds=age(receipt.ts, tail.observed_at))
        return replace(tail, data=receipt)
    except (ValueError, UnicodeError, RecursionError) as exc:
        return replace(tail, data=ReceiptData(path=data.path, tail=data, parsing_errors=(str(exc),)),
                       error=Error('receipt_parse', str(exc)))
