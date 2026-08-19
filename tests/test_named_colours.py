from matplotlib.colors import CSS4_COLORS

from cvdlint.named_colours import CSS4_COLOURS


def test_css4_colours_match_matplotlib() -> None:
    """Ensure cvdlint's colour dictionary is correct and complete.
    
    Note: Matplotlib is only used as an independent reference during development."""
    expected = {name.lower(): value.upper() for name, value in CSS4_COLORS.items()}
    assert expected == CSS4_COLOURS
