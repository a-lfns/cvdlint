import plotly.graph_objects as go

from cvdlint.adapters.plotly import check_figure, colors_from_figure


def test_extracts_explicit_hex_colors() -> None:
    figure = go.Figure()
    figure.add_scatter(y=[1, 2], line={"color": "#E41A1C"})
    figure.add_scatter(y=[2, 1], marker={"color": "#377EB8"}, mode="markers")
    assert colors_from_figure(figure) == ("#E41A1C", "#377EB8")
    assert check_figure(figure, tolerance=0).passed
