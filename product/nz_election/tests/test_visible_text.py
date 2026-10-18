"""Guard against disclosure metadata becoming unbroken visible prose."""
import pytest

from product.nz_election.tests.test_home import populated
from product.nz_election.tools.check_visible_text import VisibleText, check_site


def test_populated_routes_have_bounded_visible_text(populated):
    _, site = populated
    assert check_site(site) == 79
    downloads = (site / 'downloads/index.html').read_text()
    assert '<details><summary>Full manifest record (stored UTC)</summary>' in downloads
    assert '<pre>' in downloads and '{"bytes":' not in VisibleText(downloads).text


@pytest.mark.parametrize('wrapper', ['<p>{}</p>', '<details open><summary>Record</summary>{}</details>',
                                     '<details><summary>{}</summary>Record</details>'])
def test_long_visible_text_rejected(tmp_path, wrapper):
    (tmp_path / 'index.html').write_text(wrapper.format('x' * 201))
    with pytest.raises(ValueError, match='VISIBLE_TEXT_RUN.*201 > 200'):
        check_site(tmp_path)


def test_closed_disclosures_and_inline_text(tmp_path):
    hidden = 'x' * 201
    html = '<details><summary>Record</summary><pre>' + hidden + '</pre></details>'
    html += '<script>' + hidden + '</script><span hidden>' + hidden + '</span>'
    html += '<details><summary>Outer</summary><details open><summary>' + hidden + '</summary></details></details>'
    page = tmp_path / 'index.html'
    page.write_text(html)
    assert check_site(tmp_path) == 1
    assert hidden not in VisibleText(html).text
    page.write_text('<p>' + 'x' * 100 + '<span>' + 'x' * 101 + '</span></p>')
    with pytest.raises(ValueError, match='VISIBLE_TEXT_RUN.*201 > 200'):
        check_site(tmp_path)


def test_rewriting_closed_json_to_div_reproduces_regression(tmp_path):
    html = '<details><summary>Record</summary><pre>{"bytes":' + '1' * 220 + '}</pre></details>'
    page = tmp_path / 'index.html'
    page.write_text(html)
    assert check_site(tmp_path) == 1
    page.write_text(html.replace('<details>', '<div>').replace('</details>', '</div>'))
    with pytest.raises(ValueError, match='VISIBLE_TEXT_RUN'):
        check_site(tmp_path)
