"""Lint colour palettes for colour-vision-deficiency accessibility."""

from importlib.metadata import version as _distribution_version

from .core import palette_check, palette_dist, simulate_palette
from .figure import check_figure
from .models import CheckResult, ConditionSummary, ProblemPair

__all__ = [
    "CheckResult",
    "ConditionSummary",
    "ProblemPair",
    "check_figure",
    "palette_check",
    "palette_dist",
    "simulate_palette",
]

__version__ = _distribution_version("cvdlint")
