from typing import Optional, Tuple
import argparse
import math
from ppplt import (
    apply_paper_preset,
)

# inches
FIG_WIDTH = [3.5, 7.16]
FIG_HEIGHT = [2.5, 4.5]
BOREDR_LAYOUT = [0, 0, 1, 1]
TIGHT_LAYOUT = {"pad": 0.1, "w_pad": 0.6, "h_pad": 0.4, "rect": BOREDR_LAYOUT}
LG_WIDTH = 0.875
LG_HEIGHT = 0.15


def main(args):
    # DEFAULT SETTINGS
    fig_height = args.height or 2.5

    apply_paper_preset("ieee-modern")
    # raw matplotlib pipeline
    # 1. start the fig and axes layout
    # Note: axes can be single Axes or a tuple——array
    import matplotlib.pyplot as plt

    figure_size = (FIG_WIDTH[int(args.col - 1)], args.grid_y / args.grid_x * fig_height)
    fig, axes_arr = plt.subplots(
        nrows=args.grid_y,
        ncols=args.grid_x,
        layout="tight",
        figsize=figure_size,
        sharex=args.sharex,
        sharey=args.sharey,
    )
    fig.get_layout_engine().set(**TIGHT_LAYOUT)

    # 2. plot/draw/imshow inside each axes
    def random_plot_data(data_point_length: int = 20):
        import numpy as np

        x = np.arange(data_point_length)
        y = np.c_[x, x**1.2, x**1.5]
        return x, y

    x, y = random_plot_data(20)
    handles = []
    for axes_row in axes_arr:
        for axes in axes_row:
            line = axes.plot(x, y)
            handles += line
            axes.set_title("(a)")

    for i in range(args.grid_x):
        x_label = f"x_{i+1} 坐标轴" if i == 1 else f"x_{i+1}"
        axes_arr[-1, i].set_xlabel(x_label)

    for j in range(args.grid_y):
        y_label = f"y_{j+1} $y_{j+1}$" if j == 1 else f"y_{j+1}"
        axes_arr[j, 0].set_ylabel(y_label)

    # 3. deal with legend
    # _loc possible choices
    # ['best', 'upper right', 'upper left', 'lower left',
    # 'lower right', 'right', 'center left', 'center right',
    # 'lower center', 'upper center', 'center']
    _loc = "lower center"
    _col: Optional[int] = None
    labels = ["a", "b", "c", "d"] * 3

    figure_size = plt.gcf().get_size_inches()
    legend_col = int(round(figure_size[0] / LG_WIDTH)) if _col is None else _col
    legend_row = math.ceil(labels.__len__() / legend_col)

    updated_figure_size = (figure_size[0], legend_row * LG_HEIGHT + figure_size[1])

    border_ratio = LG_HEIGHT * legend_row / updated_figure_size[1]
    border = BOREDR_LAYOUT
    if _loc == "upper center":
        border[3] -= border_ratio
    elif _loc == "lower center":
        border[1] += border_ratio
    legend_tight_layout = {"pad": 0.1, "w_pad": 0.5, "h_pad": 0.5, "rect": border}
    plt.gcf().set_size_inches(updated_figure_size)
    plt.gcf().get_layout_engine().set(**legend_tight_layout)
    plt.figlegend(handles, labels, loc=_loc, bbox_to_anchor=(0.45, -0.03, 0.1, 0.1), ncol=legend_col, frameon=False)

    # 4. show the whole
    plt.show()

    # layout = PaperPlot()
    # layout.create_layout(args.grid_y, args.grid_x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paper Plot Layout")
    parser.add_argument("--col", "-c", type=int, default=1, choices=[1, 2], help="Plot occupy columns of single page")
    parser.add_argument("--grid_x", "-x", type=int, default=2, help="InPlot columns [for subplot]")
    parser.add_argument("--grid_y", "-y", type=int, default=3, help="InPlot rows [for subplot]")
    parser.add_argument("--height", "-H", type=float, default=2.5, help="Height of the plot [inches]")
    parser.add_argument("--sharex", "-sx", action="store_true", default=False, help="Share x-axis between subplots")
    parser.add_argument("--sharey", "-sy", action="store_true", default=False, help="Share y-axis between subplots")
    args = parser.parse_args()
    main(args)
