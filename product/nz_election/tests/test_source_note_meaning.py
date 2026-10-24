"""Each numeric group's note describes its own operation and contributing polls."""
from html import unescape
import re

import pytest

from product.nz_election.pipeline import export
from product.nz_election.pipeline.build import build, compact_time, observation_label, source_note
from product.nz_election.pipeline.refresh import refresh


def paragraph(html, identity):
    return re.search(r'id="' + identity + r'"[^>]*>\s*<p>(.*?)</p>', html, re.S)[1]


def assert_dates(note, rows, fetched):
    latest = max(p['fieldwork_end'] for p in rows)
    assert f'Fieldwork ended <time datetime="{latest}">{observation_label(latest)}</time>.' in note
    assert f'Retrieved <time datetime="{fetched}">{compact_time(fetched)}</time>.' in note
    assert note.count('Fieldwork ended') == 1


@pytest.mark.parametrize(('end_date', 'built', 'available'), [
    ('2026-07-18', '2026-10-17T01:00:00Z', True),
    ('2026-07-18', '2026-10-17T04:00:01Z', False),
    ('2026-10-17', '2026-10-17T01:00:00Z', True),
])
def test_built_note_sentences_and_contributing_dates(tmp_path, end_date, built, available):
    data = tmp_path / 'data'
    refresh(data, now='2026-10-17T01:00:00Z', end_date=end_date)
    envs = export.validate_bundle(data)
    polls = envs['polls']['data']
    selected = [p for p in polls if p['id'] in envs['averages']['data'][-1]['poll_ids']]
    site = build(data, tmp_path / 'output', built=built)
    html = (site / 'polls/index.html').read_text()
    assert ('class="strip"' in html) is available
    cases = [
        ('source-history', 'Polls parsed by this site.', polls, 'polls'),
        ('source-average', 'Available poll shares averaged with equal weight by this site.', selected, 'averages'),
        ('source-thresholds', 'Threshold shares averaged with equal weight by this site.', selected, 'seats'),
        ('source-seats', 'Seats calculated by this site.' if available else 'Seats withheld; see the headline.',
         selected if available else polls, 'polls'),
    ]
    for identity, _, _, _ in cases:
        assert f'id="{identity}"' in html
    assert 'methods/#source-average' in html
    assert 'methods/#source-history' in html
    downloads = (site / 'downloads/index.html').read_text()
    assert unescape(paragraph(downloads, 'source-polls')).endswith('Polls parsed by this site.')
    validation = (site / 'methods/index.html').read_text()
    assert 'Calculation verified against captured final results.' in validation
    assert 'Final results <time datetime="2023-11-03">3 Nov 2023</time>.' in validation
    assert 'Seats calculated by this site.' not in paragraph(validation, 'source-polls')
    if end_date == '2026-07-18':
        later = max(p['fieldwork_end'] for p in polls)
        assert later > max(p['fieldwork_end'] for p in selected)
        for identity in ('source-average', 'source-thresholds'):
            assert f'Fieldwork ended <time datetime="{later}">' not in paragraph(validation, identity)
    for identity, sentence, contributors, stem in cases:
        note = paragraph(validation, identity)
        assert unescape(note).endswith(sentence)
        assert_dates(note, contributors, envs[stem]['fetched_at'])


def test_no_contributing_polls_does_not_substitute_retrieval_date():
    from product.nz_election.pipeline.refresh import source_entries
    env = dict(source=source_entries()[0], run_url='offline-verification',
               fetched_at='2026-10-17T01:00:00Z', data=[dict(fieldwork_end='2026-10-16')])
    html = source_note(env, calculation='Available poll shares averaged with equal weight by this site.',
                       contributing_polls=[])
    assert 'Fieldwork ended' not in html
    assert 'Retrieved <time datetime="2026-10-17T01:00:00Z">17 Oct, 14:00 NZDT</time>.' in html
    assert 'Available poll shares averaged with equal weight by this site.' in html
