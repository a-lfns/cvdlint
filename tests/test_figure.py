from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pytest

from cvdlint import check_figure


def test_dispatches_matplotlib_figure() -> None:
    figure, axes = plt.subplots()
    axes.plot([0, 1], color="#E41A1C")
    axes.plot([1, 0], color="#377EB8")
    assert check_figure(figure, tolerance=0).passed
    plt.close(figure)


def test_dispatches_plotly_figure() -> None:
    figure = go.Figure()
    figure.add_scatter(y=[0, 1], line={"color": "#E41A1C"})
    figure.add_scatter(y=[1, 0], line={"color": "#377EB8"})
    assert check_figure(figure, tolerance=0).passed


def test_dispatches_root_canvas(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = object()
    received: dict[str, Any] = {}

    class Canvas:
        def InheritsFrom(self, name: str) -> bool:
            return name == "TPad"

    def fake_check_canvas(canvas: Any, **options: Any) -> Any:
        received["canvas"] = canvas
        received.update(options)
        return expected

    monkeypatch.setattr("cvdlint.adapters.root.check_canvas", fake_check_canvas)
    canvas = Canvas()
    result = check_figure(canvas, tolerance=12, severity=0.8)

    assert result is expected
    assert received == {
        "canvas": canvas,
        "tolerance": 12,
        "relative": False,
        "severity": 0.8,
        "metric": "CIEDE2000",
    }


def test_rejects_unsupported_object() -> None:
    with pytest.raises(TypeError, match=r"unsupported figure type builtins\.object"):
        check_figure(object())
