"""
Drawing utilities & pipeline steps.

This module exposes:
  - draw(): Simple single/multi subplot creation with optional callback
  - draw_grid(): Higher-level grid helper (titles, legend auto layout)
  - draw_step / draw_grid_step: pipeline (>> ) steps
  - LegendConfig: configure figure-level legend occupying extra vertical space

Design goals:
  * Keep core __init__ small; advanced grid logic lives here.
  * Avoid premature abstraction: minimal helpers with clear responsibilities.
"""

from __future__ import annotations
from typing import Callable, Any, Optional, Tuple, Sequence, Iterable, List
from dataclasses import dataclass, field
import math
import matplotlib.pyplot as plt

import ppplt as _core
from .pipeline import Step

DefPlotFn = Optional[Callable[[Any, Any], Any]]


# -----------------------
# Basic draw
# -----------------------
def draw(
    plot_fn: DefPlotFn = None,
    *,
    subplots: Tuple[int, int] = (1, 1),
    figsize: Optional[Tuple[float, float]] = None,
    tight: bool = True,
    return_axes: bool = False,
    **plot_kwargs: Any,
):
    from . import _require_phase, _Phase, logger

    _require_phase(_Phase.STYLE_SET, _Phase.DRAWN, _Phase.SAVED)
    fig, axes = plt.subplots(*subplots, figsize=figsize)  # type: ignore[arg-type]
    if plot_fn:
        try:
            plot_fn(fig, axes, **plot_kwargs)
        except Exception as e:  # wrap
            raise _core.PaperPlotException(f"绘图函数执行失败: {e}") from e
    if tight:
        try:
            fig.tight_layout()
        except Exception:
            pass
    _core._last_fig = fig
    _core._last_axes = axes
    _core._phase = _Phase.DRAWN
    logger.info("🖊️  Figure drawn")
    return (fig, axes) if return_axes else fig


def draw_step(*args, **kwargs):
    return Step(draw, *args, **kwargs)


# --------------------------------------------------
# Grid / subplot utilities (publication-oriented)
# --------------------------------------------------
_FIG_WIDTHS = {1: 3.5, 2: 7.16}  # typical single / double column widths (inches)
_DEFAULT_BASE_HEIGHT = 2.5  # heuristic per-row height


@dataclass
class LegendConfig:
    labels: Sequence[str] | None = None
    handles: Optional[Sequence[Any]] = None
    loc: str = "lower center"
    ncol: Optional[int] = None
    lg_width: float = 0.875
    lg_height: float = 0.15
    border_layout: List[float] = field(default_factory=lambda: [0, 0, 1, 1])
    frameon: bool = False
    bbox_to_anchor: Optional[Tuple[float, float, float, float]] = (0.45, -0.03, 0.1, 0.1)
    extra_tight: Optional[dict] = None


def _create_grid_figure(
    grid: Tuple[int, int],
    *,
    col_span: int = 1,
    base_height: float = _DEFAULT_BASE_HEIGHT,
    sharex: bool = False,
    sharey: bool = False,
    layout: str = "tight",
    figsize: Optional[Tuple[float, float]] = None,
    tight_rect: Optional[Tuple[float, float, float, float]] = None,
):
    rows, cols = grid
    if figsize is None:
        fw = _FIG_WIDTHS.get(col_span, _FIG_WIDTHS[1])
        fh = (rows / cols) * base_height
        figsize = (fw, fh)
    fig, axes = plt.subplots(nrows=rows, ncols=cols, layout=layout, figsize=figsize, sharex=sharex, sharey=sharey)
    if tight_rect is not None:
        try:
            fig.get_layout_engine().set(rect=tight_rect)  # type: ignore[attr-defined]
        except Exception:
            pass
    return fig, axes


def _iterate_axes(axes) -> Iterable:
    try:
        import numpy as _np

        if isinstance(axes, _np.ndarray):
            for ax in axes.flat:
                yield ax
        else:
            # could be list/tuple of axes (1-D) or single Axes
            if hasattr(axes, "__iter__") and not hasattr(axes, "plot"):
                for a in axes:  # type: ignore
                    yield a
            else:
                yield axes
    except Exception:
        if isinstance(axes, (list, tuple)):
            for a in axes:
                yield a
        else:
            yield axes


def _invoke_cell(fn: Callable, ax, r: int, c: int, idx: int, data):  # helper with backward compatibility
    if data is None:
        return fn(ax, r, c, idx)
    try:
        return fn(ax, r, c, idx, data)
    except TypeError:
        # Fallback to old signature silently if user did not add data param
        return fn(ax, r, c, idx)


def _populate_grid(axes, plot_cell: Callable, *, titles: Optional[Sequence[str]] = None, data=None):
    if hasattr(axes, "shape") and len(getattr(axes, "shape")) == 2:
        rows, cols = axes.shape
        idx = 0
        for r in range(rows):
            for c in range(cols):
                ax = axes[r, c]
                _invoke_cell(plot_cell, ax, r, c, idx, data)
                if titles and idx < len(titles):
                    ax.set_title(titles[idx])
                idx += 1
    else:
        idx = 0
        for ax in _iterate_axes(axes):
            _invoke_cell(plot_cell, ax, 0, idx, idx, data)
            if titles and idx < len(titles):
                ax.set_title(titles[idx])
            idx += 1


def _collect_line_handles_labels(axes):
    handles: List[Any] = []
    labels: List[str] = []
    for ax in _iterate_axes(axes):
        h, l = ax.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)
    return handles, labels


def _apply_legend(fig, axes, cfg: LegendConfig):
    if cfg is None:
        return None
    handles = list(cfg.handles) if cfg.handles is not None else None
    labels = list(cfg.labels) if cfg.labels is not None else None
    if handles is None or labels is None:
        auto_h, auto_l = _collect_line_handles_labels(axes)
        if handles is None:
            handles = auto_h
        if labels is None:
            labels = auto_l
    if not handles or not labels:
        return None
    figure_size = fig.get_size_inches()
    legend_col = cfg.ncol or max(1, int(round(figure_size[0] / cfg.lg_width)))
    legend_row = math.ceil(len(labels) / legend_col)
    updated_figure_size = (figure_size[0], legend_row * cfg.lg_height + figure_size[1])
    border_ratio = cfg.lg_height * legend_row / updated_figure_size[1]
    border = list(cfg.border_layout)
    if cfg.loc == "upper center":
        border[3] -= border_ratio
    elif cfg.loc == "lower center":
        border[1] += border_ratio
    tight_params = {"pad": 0.1, "w_pad": 0.5, "h_pad": 0.5}
    if cfg.extra_tight:
        tight_params.update(cfg.extra_tight)
    tight_params["rect"] = border
    try:
        fig.set_size_inches(updated_figure_size)
        fig.get_layout_engine().set(**tight_params)  # type: ignore[attr-defined]
    except Exception:
        pass
    legend = fig.legend(
        handles,
        labels,
        loc=cfg.loc,
        bbox_to_anchor=cfg.bbox_to_anchor,
        ncol=legend_col,
        frameon=cfg.frameon,
    )
    return legend


def draw_grid(
    plot_cell: Callable[[Any, int, int, int], Any],
    *,
    grid: Tuple[int, int] = (1, 1),
    col_span: int = 1,
    base_height: float = _DEFAULT_BASE_HEIGHT,
    sharex: bool = False,
    sharey: bool = False,
    legend: Optional[LegendConfig] = None,
    titles: Optional[Sequence[str]] = None,
    tight: bool = True,
    return_axes: bool = False,
    figsize: Optional[Tuple[float, float]] = None,
    data: Any = None,
):
    from . import _require_phase, _Phase, logger

    _require_phase(_Phase.STYLE_SET, _Phase.DRAWN, _Phase.SAVED)
    fig, axes = _create_grid_figure(
        grid, col_span=col_span, base_height=base_height, sharex=sharex, sharey=sharey, figsize=figsize
    )
    _populate_grid(axes, plot_cell, titles=titles, data=data)
    if tight:
        try:
            fig.tight_layout()
        except Exception:
            pass
    if legend:
        _apply_legend(fig, axes, legend)
    _core._last_fig = fig
    _core._last_axes = axes
    _core._phase = _Phase.DRAWN
    logger.info("🖊️  Grid figure drawn")
    return (fig, axes) if return_axes else fig


def draw_grid_step(*args, **kwargs):
    return Step(draw_grid, *args, **kwargs)


__all__ = [
    "draw",
    "draw_step",
    "draw_grid",
    "draw_grid_step",
    "LegendConfig",
]
