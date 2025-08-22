import os
import numpy as np

import ppplt
from ppplt.draw import draw_grid, LegendConfig
import matplotlib.pyplot as plt


ppplt.init(log_time=False)
ppplt.set_style(preset="ieee-modern")

# Grid size (rows, cols) aligned with demo
GRID = (2, 3)

# Titles like (a) (b) ... similar to academic figure annotations
titles = [f"({chr(97+i)})" for i in range(GRID[0] * GRID[1])]


def cell(ax, r, c, idx, data):
    """Populate a single subplot.

    Mirrors logic in matplot_subplot_demo:
      - generate sample multi-series data
      - plot 3 curves (only label on first subplot to avoid legend duplicates)
      - set axis labels on bottom row / first column with contextual text
    """
    x = data["x"]
    curves = data["curves"]  # precomputed list
    # Only label on first subplot so legend has 3 entries
    show_label = r == 0 and c == 0
    labels = ["a", "b", "c"] if show_label else ["_nolegend_"] * 3
    for y, lab in zip(curves, labels):
        ax.plot(x, y, label=lab)

    # Axis labels pattern
    if r == GRID[0] - 1:  # bottom row -> x label
        ax.set_xlabel(f"x_{c+1} 坐标轴" if c == 1 else f"x_{c+1}")
    if c == 0:  # first column -> y label
        ax.set_ylabel(f"y_{r+1} $y_{r+1}$" if r == 1 else f"y_{r+1}")


# LegendConfig: auto handles/labels collected; layout similar to demo (lower center)
legend_cfg = LegendConfig(
    labels=None,  # auto collect
    handles=None,  # auto collect
    loc="lower center",
    ncol=None,  # auto column count based on figure width
    frameon=False,
    extra_tight={"w_pad": 0.5, "h_pad": 0.5, "pad": 0.1},
)

precomputed = {"x": np.arange(20), "curves": []}
precomputed["curves"] = [precomputed["x"], precomputed["x"] ** 1.2, precomputed["x"] ** 1.5]

fig = draw_grid(
    cell,
    grid=GRID,
    legend=legend_cfg,
    titles=titles,
    col_span=1,  # 单栏
    data=precomputed,
    return_axes=False,
)
ppplt.logger.info(f"axes cnt: {len(fig.axes)}")

# 保存到 img_output 目录
out_dir = os.path.dirname(ppplt.get_src_dir()) + "/img_output"
os.makedirs(out_dir, exist_ok=True)
ppplt.save(os.path.join(out_dir, "grid_demo"), formats=["png", "pdf"])  # 多格式输出
ppplt.logger.info("Saved grid_demo.[png|pdf] in img_output/")

# 如需交互查看取消下一行注释
# plt.show()

# 退出释放资源
ppplt.destroy()
