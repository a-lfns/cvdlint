"""Plotly colour extraction."""

from __future__ import annotations

from typing import Any

from ..core import Metric, palette_check
from ..models import CheckResult


def colors_from_figure(figure: Any) -> tuple[str, ...]:
    """Extract explicit line, marker, and fill colours from Plotly JSON."""
    # Inspect trace properties only. ``Figure.to_plotly_json()`` also expands the
    # complete template and would incorrectly report unused theme colours.
    payload = [trace.to_plotly_json() for trace in figure.data]
    colors: list[str] = []

    def visit(value: Any, key: str | None = None) -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif (
            key in {"color", "fillcolor"}
            and isinstance(value, str)
            and value.startswith("#")
            and len(value) in {4, 7}
        ):
            if len(value) == 4:
                value = "#" + "".join(character * 2 for character in value[1:])
            colors.append(value.upper())

    visit(payload)
    return tuple(dict.fromkeys(colors))


def check_figure(
    figure: Any,
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> CheckResult:
    """Extract and check explicitly assigned Plotly colours."""
    colors = colors_from_figure(figure)
    if len(colors) < 2:
        raise ValueError("Figure contains fewer than two explicit hex colours")
    return palette_check(
        colors,
        tolerance=tolerance,
        relative=relative,
        severity=severity,
        metric=metric,
    )
