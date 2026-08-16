import numpy as np
import pytest

from cvdlint import palette_check, palette_dist, simulate_palette

RAINBOW = (
    "#FF0000",
    "#FFDB00",
    "#49FF00",
    "#00FF92",
    "#0092FF",
    "#4900FF",
    "#FF00DB",
)


def test_distance_matrix_is_upper_triangular() -> None:
    distances = palette_dist(RAINBOW)
    assert distances.shape == (7, 7)
    assert np.isnan(np.diag(distances)).all()
    assert np.isnan(distances[np.tril_indices_from(distances)]).all()


def test_normal_distances_match_colorblindcheck_reference() -> None:
    distances = palette_dist(RAINBOW)
    # Values published by Nowosad/colorblindcheck for this exact palette.
    assert distances[0, 1] == pytest.approx(52.96503, abs=0.03)
    assert distances[2, 3] == pytest.approx(12.13226, abs=0.03)
    assert distances[0, 6] == pytest.approx(39.46279, abs=0.03)


def test_check_returns_all_conditions() -> None:
    report = palette_check(RAINBOW, relative=True)
    assert tuple(summary.name for summary in report.summaries) == (
        "normal",
        "deuteranopia",
        "protanopia",
        "tritanopia",
    )
    assert report.summaries[0].pair_count == 21
    assert report.problems
    assert not report.passed
    # colorblindcheck 1.0.4 reports the same differentiable-pair counts.
    assert tuple(
        summary.distinguishable_pair_count for summary in report.summaries
    ) == (
        21,
        19,
        17,
        20,
    )
    reference_minima = (12.132257, 2.572062, 3.647681, 2.025647)
    for summary, reference in zip(report.summaries, reference_minima, strict=True):
        # Small simulation differences arise from cross-language RGB rounding.
        assert summary.minimum_distance == pytest.approx(reference, abs=0.25)


def test_explicit_safe_threshold() -> None:
    report = palette_check(("#000000", "#FFFFFF"), tolerance=10)
    assert report.passed
    report.raise_for_failure()


def test_default_uses_absolute_ciede2000_tolerance() -> None:
    report = palette_check(("#4DAF4A", "#377EB8"))
    assert report.passed
    assert all(summary.tolerance == 10 for summary in report.summaries)


def test_relative_mode_uses_normal_vision_minimum() -> None:
    report = palette_check(("#4DAF4A", "#377EB8"), relative=True)
    assert report.summaries[0].tolerance == pytest.approx(
        report.summaries[0].minimum_distance
    )
    assert not report.passed


def test_relative_mode_rejects_explicit_tolerance() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        palette_check(("#000000", "#FFFFFF"), tolerance=10, relative=True)


def test_invalid_input() -> None:
    with pytest.raises(ValueError, match="expected #RRGGBB"):
        palette_check(("red", "#FFFFFF"))
    with pytest.raises(ValueError, match="at least two"):
        palette_check(("#FFFFFF",))


def test_simulation_returns_hex() -> None:
    result = simulate_palette(("#FF0000", "#00FF00"), "deuteranopia")
    assert len(result) == 2
    assert all(color.startswith("#") and len(color) == 7 for color in result)


@pytest.mark.parametrize("metric", ["CIE76", "CIE94", "CIEDE2000"])
def test_supported_metrics(metric: str) -> None:
    distances = palette_dist(("#000000", "#FFFFFF"), metric=metric)  # type: ignore[arg-type]
    assert distances[0, 1] > 0
