"""PyROOT colour extraction."""

from __future__ import annotations

from typing import Any

from ..core import Metric, palette_check
from ..models import CheckResult


def colors_from_canvas(canvas: Any) -> tuple[str, ...]:
    """Extract line, marker, fill, and text colours from ROOT pads."""
    try:
        import ROOT
    except ImportError as error:
        raise ImportError(
            "PyROOT must be installed to inspect ROOT canvases"
        ) from error

    indices: list[int] = []

    def walk(container: Any) -> None:
        primitives = container.GetListOfPrimitives()
        if primitives is None:
            return
        for primitive in primitives:
            if primitive.InheritsFrom("TPad"):
                walk(primitive)
            for getter in (
                "GetLineColor",
                "GetMarkerColor",
                "GetFillColor",
                "GetTextColor",
            ):
                if hasattr(primitive, getter):
                    index = int(getattr(primitive, getter)())
                    if index > 0:
                        indices.append(index)

    walk(canvas)
    colors: list[str] = []
    for index in dict.fromkeys(indices):
        color = ROOT.gROOT.GetColor(index)
        if color is not None:
            colors.append(
                f"#{round(color.GetRed() * 255):02X}"
                f"{round(color.GetGreen() * 255):02X}"
                f"{round(color.GetBlue() * 255):02X}"
            )
    return tuple(dict.fromkeys(colors))


def check_canvas(
    canvas: Any,
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> CheckResult:
    """Extract and check colours used by a ROOT canvas."""
    colors = colors_from_canvas(canvas)
    if len(colors) < 2:
        raise ValueError("Canvas contains fewer than two distinct visible colours")
    return palette_check(
        colors,
        tolerance=tolerance,
        relative=relative,
        severity=severity,
        metric=metric,
    )
