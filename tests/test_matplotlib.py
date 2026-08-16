import matplotlib.pyplot as plt

from cvdlint.adapters.matplotlib import check_figure, colors_from_figure


def test_extracts_line_colors() -> None:
    figure, axes = plt.subplots()
    axes.plot([0, 1], [0, 1], color="#E41A1C")
    axes.plot([0, 1], [1, 0], color="#377EB8")
    assert colors_from_figure(figure) == ("#E41A1C", "#377EB8")
    assert check_figure(figure, tolerance=0).passed
    plt.close(figure)
