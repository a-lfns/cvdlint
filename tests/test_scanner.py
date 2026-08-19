import json
from pathlib import Path

import pytest

from cvdlint.scanner import SourceSyntaxError, extract_palettes, scan_paths


def test_extracts_literal_list_tuple_and_set() -> None:
    source = """
palette = ["#E41A1C", "#4DAF4A", "#377EB8"]
plot(colors=("#000000", "#FFFFFF"))
ignored = ["#000000", dynamic_color]
"""

    occurrences = extract_palettes(Path("chart.py"), source)

    assert [item.colors for item in occurrences] == [
        ("#E41A1C", "#4DAF4A", "#377EB8"),
        ("#000000", "#FFFFFF"),
    ]
    assert occurrences[0].line == 2


def test_reports_syntax_error_location() -> None:
    with pytest.raises(SourceSyntaxError, match=r"chart.py:1:\d+: syntax error"):
        extract_palettes(Path("chart.py"), "palette = [")


def test_scans_directories_and_skips_virtual_environments(tmp_path: Path) -> None:
    source = 'palette = ["#E41A1C", "#4DAF4A"]\n'
    (tmp_path / "chart.py").write_text(source)
    hidden = tmp_path / ".venv"
    hidden.mkdir()
    (hidden / "ignored.py").write_text(source)

    diagnostics = scan_paths((tmp_path,), tolerance=100)

    assert len(diagnostics) == 1
    assert diagnostics[0].occurrence.path == tmp_path / "chart.py"
    assert not diagnostics[0].report.passed


def test_extracts_palettes_from_notebook_code_cells(tmp_path: Path) -> None:
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ['not code: ["#000000", "#FFFFFF"]'],
            },
            {
                "cell_type": "code",
                "source": ['title = "example"\n', 'palette = ["#E41A1C", "#4DAF4A"]'],
            },
        ]
    }
    path = tmp_path / "chart.ipynb"
    path.write_text(json.dumps(notebook))

    diagnostics = scan_paths((path,), tolerance=100)

    assert len(diagnostics) == 1
    occurrence = diagnostics[0].occurrence
    assert occurrence.cell == 2
    assert occurrence.line == 2
    assert occurrence.colors == ("#E41A1C", "#4DAF4A")


def test_resolves_variables_dictionaries_named_colours_rgb_and_composition() -> None:
    source = """
RED = "firebrick"
BLUE = "#377EB8"
BASE = [RED, BLUE]
RGB = [(0.0, 1.0, 0.0), (255, 215, 0)]
COMBINED = BASE + RGB
MAPPING = {"first": RED, "second": BLUE}
"""

    occurrences = extract_palettes(Path("chart.py"), source)
    palettes = {occurrence.colors for occurrence in occurrences}

    assert ("#B22222", "#377EB8") in palettes
    assert ("#00FF00", "#FFD700") in palettes
    assert ("#B22222", "#377EB8", "#00FF00", "#FFD700") in palettes


def test_suppression_comment_ignores_palette() -> None:
    source = 'palette = ["#E41A1C", "#4DAF4A"]  # cvdlint: ignore\n'
    assert extract_palettes(Path("chart.py"), source) == ()


def test_notebook_resolves_values_from_previous_cells(tmp_path: Path) -> None:
    path = tmp_path / "chart.ipynb"
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": ['RED = "firebrick"']},
                    {
                        "cell_type": "code",
                        "source": ['palette = [RED, "steelblue"]'],
                    },
                ]
            }
        )
    )

    diagnostics = scan_paths((path,), tolerance=100)

    assert len(diagnostics) == 1
    assert diagnostics[0].occurrence.cell == 2
    assert diagnostics[0].occurrence.colors == ("#B22222", "#4682B4")


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("palette.json", '{"palette": ["firebrick", "steelblue"]}'),
        ("palette.toml", 'palette = ["firebrick", "steelblue"]'),
        ("palette.yaml", "palette:\n  - firebrick\n  - steelblue\n"),
        (
            "palette.yml",
            "palette:\n  primary: firebrick\n  secondary: steelblue\n",
        ),
    ],
)
def test_extracts_configuration_palettes(
    filename: str, source: str, tmp_path: Path
) -> None:
    path = tmp_path / filename
    path.write_text(source)

    diagnostics = scan_paths((path,), tolerance=100)

    assert len(diagnostics) == 1
    assert diagnostics[0].occurrence.colors == ("#B22222", "#4682B4")


def test_excludes_matching_paths(tmp_path: Path) -> None:
    (tmp_path / "keep.py").write_text('p = ["red", "blue"]')
    (tmp_path / "skip.py").write_text('p = ["red", "blue"]')

    diagnostics = scan_paths((tmp_path,), exclude=("skip.py",))

    assert len(diagnostics) == 1
    assert diagnostics[0].occurrence.path.name == "keep.py"
