"""Interactive map accessibility must survive static build verification."""
import pytest

from product.nz_election.pipeline.image_role_checks import check_page
from product.nz_election.pipeline.snapshot_views import winner_name


@pytest.mark.parametrize('child', ['<a href="/">Seat</a>', '<g><a href="/">Seat</a></g>',
                                  '<button>Seat</button>', '<span tabindex="-1">Seat</span>',
                                  '<input>', '<div contenteditable="true"></div>'])
def test_image_rejects_focusable_descendants(child):
    with pytest.raises(ValueError, match='ROLE_IMG_FOCUS'):
        check_page('<svg role="img">' + child + '</svg>')


def test_group_preserves_interactive_descendants():
    check_page('<svg role="group"><a href="/">Seat</a></svg>')
    check_page('<svg role="img"><rect/><title>Seat</title></svg><a href="/">Seat</a>')


def test_winner_display_uses_explicit_incumbent():
    assert winner_name({'slug': 'nelson'}, {'name': 'BOYACK-MAYER, Rachel Elizabeth', 'party_id': 'lab'}) == 'Rachel Boyack'
    assert winner_name({'slug': 'nelson'}, {'name': 'EXAMPLE, Jane Anne', 'party_id': 'nat'}) == 'Jane Anne Example'
