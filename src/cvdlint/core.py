"""Framework-independent palette analysis."""

from __future__ import annotations

from itertools import combinations
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .color import (
    delta_e_76,
    delta_e_94,
    delta_e_2000,
    hex_to_rgb,
    normalize_hex,
    rgb_to_hex,
    simulate,
    srgb_to_lab,
)
from .models import CheckResult, ConditionSummary, ProblemPair

Condition = Literal["protanopia", "deuteranopia", "tritanopia"]
Metric = Literal["CIE76", "CIE94", "CIEDE2000"]
CONDITIONS: tuple[Condition, ...] = (
    "deuteranopia",
    "protanopia",
    "tritanopia",
)


def simulate_palette(
    colors: list[str] | tuple[str, ...],
    condition: Condition,
    *,
    severity: float = 1.0,
) -> tuple[str, ...]:
    """Return a palette as perceived under one CVD condition."""
    return rgb_to_hex(simulate(hex_to_rgb(colors), condition, severity))


def palette_dist(
    colors: list[str] | tuple[str, ...],
    *,
    condition: Condition | None = None,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> NDArray[np.float64]:
    """Return an upper-triangular pairwise colour-distance matrix."""
    if len(colors) < 2:
        raise ValueError("A palette must contain at least two colours")
    rgb = hex_to_rgb(colors)
    if condition is not None:
        rgb = simulate(rgb, condition, severity)
    lab = srgb_to_lab(rgb)
    distance_functions = {
        "CIE76": delta_e_76,
        "CIE94": delta_e_94,
        "CIEDE2000": delta_e_2000,
    }
    if metric not in distance_functions:
        raise ValueError(f"Unsupported metric: {metric!r}")
    distance = distance_functions[metric]
    matrix = np.full((len(colors), len(colors)), np.nan)
    for first, second in combinations(range(len(colors)), 2):
        matrix[first, second] = distance(lab[first], lab[second])
    return matrix


def palette_check(
    colors: list[str] | tuple[str, ...],
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
    conditions: tuple[Condition, ...] = CONDITIONS,
) -> CheckResult:
    """Analyse a palette under normal vision and simulated CVD vision.

    CIEDE2000 uses an absolute tolerance of 10 by default. Set ``relative``
    to use the smallest normal-vision distance instead. Other metrics require
    an explicit tolerance or relative mode.
    """
    if relative and tolerance is not None:
        raise ValueError("tolerance and relative mode are mutually exclusive")
    if tolerance is None and not relative:
        if metric != "CIEDE2000":
            raise ValueError(
                f"metric {metric} requires an explicit tolerance or relative mode"
            )
        tolerance = 10.0
    normalized = tuple(normalize_hex(color) for color in colors)
    matrices: dict[str, NDArray[np.float64]] = {
        "normal": palette_dist(normalized, metric=metric)
    }
    matrices.update(
        {
            condition: palette_dist(
                normalized,
                condition=condition,
                severity=severity,
                metric=metric,
            )
            for condition in conditions
        }
    )
    normal_values = matrices["normal"][~np.isnan(matrices["normal"])]
    threshold = float(normal_values.min()) if relative else float(tolerance)
    if threshold < 0:
        raise ValueError("tolerance must not be negative")

    summaries: list[ConditionSummary] = []
    problems: list[ProblemPair] = []
    pair_count = len(normalized) * (len(normalized) - 1) // 2
    for name, matrix in matrices.items():
        values = matrix[~np.isnan(matrix)]
        summaries.append(
            ConditionSummary(
                name=name,
                color_count=len(normalized),
                tolerance=threshold,
                pair_count=pair_count,
                distinguishable_pair_count=int(np.count_nonzero(values >= threshold)),
                minimum_distance=float(values.min()),
                mean_distance=float(values.mean()),
                maximum_distance=float(values.max()),
            )
        )
        if name == "normal":
            continue
        for first, second in combinations(range(len(normalized)), 2):
            value = float(matrix[first, second])
            if value < threshold:
                problems.append(
                    ProblemPair(
                        condition=name,
                        first_index=first,
                        second_index=second,
                        first_color=normalized[first],
                        second_color=normalized[second],
                        distance=value,
                        tolerance=threshold,
                    )
                )
    return CheckResult(normalized, tuple(summaries), tuple(problems))
