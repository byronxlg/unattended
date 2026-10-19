"""Keep short attribution at the seat hero and full legal provenance on Methods."""
import pytest
from product.nz_election.pipeline.source_budget_checks import check_markup, check_site
from product.nz_election.pipeline.build import PREFIX
from product.nz_election.tests.test_home import populated


def test_seat_note_content_budget_and_methods_destination(populated):
    envs, site = populated
    assert set(check_site(site)) == {'index.html', 'polls/index.html'}
    polls = (site / 'polls/index.html').read_text()
    note = polls.split('id="source-seats"', 1)[1].split('</div>', 1)[0]
    assert 'Wikipedia contributors (CC BY-SA 4.0)' in note
    revision = next(s for s in envs['polls']['source'] if s['id'] == 'P')
    from html import escape
    assert f'href="{escape(revision["url"], quote=True)}"' in note
    assert f'href="{PREFIX}methods/#source-history-legal">Method</a>' in note
    assert 'Contributor history' not in note and 'Legislation has no copyright.' not in note
    methods = (site / 'methods/index.html').read_text()
    legal = methods.split('id="source-history-legal"', 1)[1].split('</section>', 1)[0]
    assert f'href="{escape(revision["history_url"], quote=True)}">Contributor history</a>' in legal
    assert 'Legislation has no copyright.' in legal
    assert 'Electoral Act 1993, sections 191-193</a>' in legal


@pytest.mark.parametrize('extra', ['<p>Legal history</p>', '<p>' + 'x' * 321 + '</p>',
                                  '<a href="#">Extra</a>' * 7])
def test_growing_source_note_rejected(extra):
    html = '<div id="source-seats"><p>Attribution</p><p class="source-actions">Method</p>' + extra + '</div>'
    with pytest.raises(ValueError, match='SOURCE_NOTE_CONTENT_BUDGET'):
        check_markup(html)
