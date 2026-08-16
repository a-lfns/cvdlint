"""Public result models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProblemPair:
    """A pair of colours that falls below the configured tolerance."""

    condition: str
    first_index: int
    second_index: int
    first_color: str
    second_color: str
    distance: float
    tolerance: float


@dataclass(frozen=True, slots=True)
class ConditionSummary:
    """Distance summary for one viewing condition."""

    name: str
    color_count: int
    tolerance: float
    pair_count: int
    distinguishable_pair_count: int
    minimum_distance: float
    mean_distance: float
    maximum_distance: float


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Structured palette lint report."""

    colors: tuple[str, ...]
    summaries: tuple[ConditionSummary, ...]
    problems: tuple[ProblemPair, ...]

    @property
    def passed(self) -> bool:
        """Whether every simulated pair meets the tolerance."""
        return not self.problems

    def raise_for_failure(self) -> None:
        """Raise an assertion suitable for tests and CI."""
        if self.passed:
            return
        details = "\n".join(
            f"  {p.condition}: {p.first_color} / {p.second_color} "
            f"= {p.distance:.2f} < {p.tolerance:.2f}"
            for p in self.problems
        )
        raise AssertionError(f"Palette is not CVD-safe:\n{details}")
