import re

from cvdlint.named_colours import CSS4_COLOURS

HEX_COLOUR = re.compile(r"^#[0-9A-F]{6}$")


def test_contains_all_css4_named_colours() -> None:
    assert len(CSS4_COLOURS) == 148


def test_named_colours_have_normalised_names_and_values() -> None:
    assert all(name == name.lower() for name in CSS4_COLOURS)
    assert all(HEX_COLOUR.fullmatch(value) for value in CSS4_COLOURS.values())


def test_css_spelling_aliases_match() -> None:
    aliases = (
        ("gray", "grey"),
        ("darkgray", "darkgrey"),
        ("darkslategray", "darkslategrey"),
        ("dimgray", "dimgrey"),
        ("lightgray", "lightgrey"),
        ("lightslategray", "lightslategrey"),
        ("slategray", "slategrey"),
    )

    for first, second in aliases:
        assert CSS4_COLOURS[first] == CSS4_COLOURS[second]


def test_css4_adds_rebeccapurple() -> None:
    assert CSS4_COLOURS["rebeccapurple"] == "#663399"
