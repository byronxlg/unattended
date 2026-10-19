"""Provenance remains complete and linked without expanding the market summary."""
import pytest

from product.nz_election.pipeline.build import PREFIX
from product.nz_election.pipeline.market_budget_checks import check_markup, check_site
from product.nz_election.pipeline.market_panel import label, leaders
from product.nz_election.pipeline.presentation import market_money
from product.nz_election.tests.test_home import populated


def test_markets_keep_amounts_in_linked_methods_section(populated):
    envs, site = populated
    assert check_site(site) == 79
    html = (site / 'methods/index.html').read_text()
    module = html.split('<section id="markets"', 1)[1].split('</section>', 1)[0]
    records = html.split('<section id="market-observations"', 1)[1].split('</section>', 1)[0]
    assert f'href="{PREFIX}methods/#market-observations"' in module
    assert 'id="source-markets"' in module and 'class="source-actions"' in module
    for _, row in leaders(envs['markets']['data']):
        if row:
            assert f'{label(row)}: volume {market_money(row["volume"])}; liquidity {market_money(row["liquidity"])}. Observed {row["observed_at"]}.' in records
    assert 'aria-describedby="source-markets"' in records


@pytest.mark.parametrize('text', ['Contract: volume 1 USD', 'Contract: liquidity 2 USD'])
def test_inline_amounts_rejected_even_in_nested_sections(text):
    with pytest.raises(ValueError, match='MARKET_INLINE_PROVENANCE'):
        check_markup(f'<section id="markets"><section><p>{text}</p></section></section>')


def test_linked_records_do_not_count_as_inline():
    check_markup('<section id="markets"><p>Market price</p></section>'
                 '<section id="market-observations"><p>Volume 1 USD; liquidity 2 USD.</p></section>')
