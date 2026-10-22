"""Open prose on every route while retaining full data-table disclosures."""
import pytest

from product.nz_election.pipeline.disclosure_checks import check_site
from product.nz_election.tests.test_home import populated


def test_non_home_disclosures_hold_tables(populated):
    _, site = populated
    assert check_site(site) == 80


@pytest.mark.parametrize('body', [
    '<p>Method note</p>', '<ul><li>Source</li></ul>', '<pre>{"record": 1}</pre>',
    '<details><summary>Nested prose</summary><p>Note</p></details><table></table>',
    '<!-- <table> --><p>Not a table</p>',
])
def test_prose_disclosure_rejected(tmp_path, body):
    route = tmp_path / 'methods'
    route.mkdir()
    (route / 'index.html').write_text('<details><summary>Method</summary>' + body + '</details>')
    with pytest.raises(ValueError, match='PROSE_DISCLOSURE: methods/index.html'):
        check_site(tmp_path)


def test_long_table_and_open_prose_allowed(tmp_path):
    route = tmp_path / 'polls'
    route.mkdir()
    rows = '<tr><td>Poll</td></tr>' * 13
    (route / 'index.html').write_text('<div><p>Method</p></div><details><summary>All polls</summary>'
                                    '<table>' + rows + '</table></details>')
    assert check_site(tmp_path) == 1
