"""Automatic dispatch for plotting-library objects."""

from __future__ import annotations

from typing import Any

from .core import Metric
from .models import CheckResult


def _type_roots(value: Any) -> set[str]:
    """Return top-level module names from an object's class hierarchy."""
    return {base.__module__.partition(".")[0] for base in type(value).__mro__}


def _is_root_canvas(value: Any) -> bool:
    """Whether a PyROOT object identifies itself as a ROOT pad or canvas."""
    inherits_from = getattr(value, "InheritsFrom", None)
    if inherits_from is None:
        return False
    try:
        return bool(inherits_from("TPad"))
    except Exception:
        return False


def check_figure(
    figure: Any,
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> CheckResult:
    """Check a Matplotlib, Seaborn, Plotly, or PyROOT plotting object.

    The plotting backend is inferred from the object's class hierarchy. Optional
    plotting libraries are imported only after their object type is detected.
    """
    type_roots = _type_roots(figure)
    options = {
        "tolerance": tolerance,
        "relative": relative,
        "severity": severity,
        "metric": metric,
    }

    if "matplotlib" in type_roots:
        from .adapters.matplotlib import check_figure as check_matplotlib_figure

        return check_matplotlib_figure(figure, **options)

    if "plotly" in type_roots:
        from .adapters.plotly import check_figure as check_plotly_figure

        return check_plotly_figure(figure, **options)

    if _is_root_canvas(figure):
        from .adapters.root import check_canvas

        return check_canvas(figure, **options)

    qualified_name = f"{type(figure).__module__}.{type(figure).__qualname__}"
    raise TypeError(
        f"unsupported figure type {qualified_name}; expected a Matplotlib, "
        "Seaborn, Plotly, or PyROOT figure or canvas"
    )
