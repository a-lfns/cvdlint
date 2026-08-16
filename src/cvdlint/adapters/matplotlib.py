"""Matplotlib and Seaborn colour extraction."""

from __future__ import annotations

from typing import Any

from ..core import Metric, palette_check
from ..models import CheckResult


def colors_from_figure(figure: Any) -> tuple[str, ...]:
    """Extract visible artist colours from a Matplotlib figure."""
    try:
        from matplotlib.colors import to_hex
    except ImportError as error:
        raise ImportError(
            'Install Matplotlib support with "cvdlint[matplotlib]"'
        ) from error

    colors: list[str] = []

    def add(color: Any) -> None:
        try:
            value = to_hex(color, keep_alpha=True)
        except (TypeError, ValueError):
            return
        if len(value) == 9 and value[-2:] == "00":
            return
        colors.append(value[:7].upper())

    for axes in figure.axes:
        for line in axes.lines:
            add(line.get_color())
        for patch in axes.patches:
            add(patch.get_facecolor())
        for collection in axes.collections:
            for color in collection.get_facecolors():
                add(color)
            for color in collection.get_edgecolors():
                add(color)
    return tuple(dict.fromkeys(colors))


def check_figure(
    figure: Any,
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> CheckResult:
    """Extract and check the colours used by a Matplotlib/Seaborn figure."""
    colors = colors_from_figure(figure)
    if len(colors) < 2:
        raise ValueError("Figure contains fewer than two distinct visible colours")
    return palette_check(
        colors,
        tolerance=tolerance,
        relative=relative,
        severity=severity,
        metric=metric,
    )
