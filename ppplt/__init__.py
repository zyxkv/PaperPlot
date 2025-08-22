"""paper_plot (ppplt)

出版级 Matplotlib 图表样式与实用工具（IEEE / GB），并提供 **函数式 + 链式 (``>>``)** 绘图体验。

最小心智模型：
    init() -> set_style()/preset -> draw() -> save()

或使用链式步骤：
    (init_step() >> style_step(preset="ieee-modern") >> draw_step(... ) >> save_step("out.png")).run()

本模块只保留：
    - 生命周期 / 全局状态 (_phase, _last_fig, _last_axes)
    - 异常类型 & 顺序校验 (_require_phase, PaperPlotException)
    - 初始化 / 销毁 (init, destroy)
    - 末次图对象访问 (last_figure / last_axes)
其余功能已拆分至: presets.py, colorset.py, draw.py, save.py, pipeline.py。
"""

from __future__ import annotations

import os
import sys
import atexit
import logging as _logging
import traceback
from pathlib import Path
from typing import Optional
from enum import Enum, auto
from contextlib import redirect_stdout

from .logging import Logger
from .version import __version__
from .misc import redirect_libc_stderr, get_platform, get_src_dir, get_style_dir

_initialized = False


class _Phase(Enum):  # 内部有限状态机
    UNINITIALIZED = auto()
    INITIALIZED = auto()
    STYLE_SET = auto()
    DRAWN = auto()
    SAVED = auto()


_phase: _Phase = _Phase.UNINITIALIZED
_last_fig = None
_last_axes = None  # could be Axes or ndarray of Axes


def init(
    debug: bool = False,
    log_time: bool = True,
    logging_level=None,
    theme: str = "dark",
    logger_verbose_time: bool = False,
    preset: str = "ieee-modern",
):
    global _initialized, _phase
    if _initialized:
        raise_exception("PaperPlot already initialized.")
    # Make sure evertything is properly destroyed, just in case initialization failed previously
    destroy()

    # ppplot._theme
    global _theme
    is_theme_valid = theme in ("dark", "light", "dumb")
    # Set fallback theme if necessary to be able to initialize logger
    _theme = theme if is_theme_valid else "dark"

    # ppplot.logger
    global logger
    if logging_level is None:
        logging_level = _logging.DEBUG if debug else _logging.INFO
    logger = Logger(logging_level, log_time, logger_verbose_time)
    atexit.register(destroy)

    if not is_theme_valid:
        raise_exception(f"Unsupported theme: {theme}")

    # Dealing with default backend
    global platform
    platform = get_platform()

    # verbose repr
    global _verbose
    _verbose = False

    # Check preset
    global _preset
    _preset = preset

    # greeting message
    _display_greeting(logger.INFO_length)

    global exit_callbacks
    exit_callbacks = []

    logger.info(f"♾️  PaperPlot Init. 🔖 version: ~~<{__version__}>~~, 🎨 style: '~~<{preset}>~~'.")

    _initialized = True
    _phase = _Phase.INITIALIZED


def destroy():
    global _initialized, _phase, _last_fig, _last_axes
    if not _initialized:
        return
    _initialized = False
    _phase = _Phase.UNINITIALIZED
    _last_fig = None
    _last_axes = None
    # Unregister at-exit callback that is not longer relevant.
    # This is important when `init` / `destory` is called multiple times, which is typically the case for unit tests.
    atexit.unregister(destroy)
    # Display any buffered error message if logger is configured
    global logger
    if logger:
        logger.info("🌌 PaperPlot Exit...")

    # Call all exit callbacks
    for cb in exit_callbacks:
        cb()
    exit_callbacks.clear()


def _display_greeting(INFO_length):
    try:
        terminal_size = os.get_terminal_size()[0]
    except OSError as e:
        terminal_size = 80
    wave_width = int((terminal_size - INFO_length - 11) / 2)
    if wave_width % 2 == 0:
        wave_width -= 1
    wave_width = max(0, min(38, wave_width))
    bar_width = wave_width * 2 + 11
    wave = ("  " * wave_width)[:wave_width]
    global logger
    logger.info(f"~<╭{'─'*(bar_width)}╮>~")
    logger.info(f"~<│{wave}>~ ~~~~<PaperPlot>~~~~ ~<{wave}│>~")
    logger.info(f"~<╰{'─'*(bar_width)}╯>~")


# ------------------------------
# Exception/Error handling
# ------------------------------
class PaperPlotException(Exception):
    def __init__(self, message):  # 保留简单结构
        self.message = message
        super().__init__(self.message)


def _custom_excepthook(exctype, value, tb):
    print("".join(traceback.format_exception(exctype, value, tb)))

    # Logger the exception right before exit if possible
    global logger
    try:
        logger.error(f"{exctype.__name__}: {value}")
    except (AttributeError, NameError):
        # Logger may not be configured at this point
        pass


# Set the custom excepthook to handle EzSimException
sys.excepthook = _custom_excepthook


def _require_phase(*allowed: _Phase):
    if _phase not in allowed:
        raise PaperPlotException(
            f"Invalid call sequence: current phase {_phase.name}, allowed: {[p.name for p in allowed]}"
        )


def last_figure():
    return _last_fig


def last_axes():
    return _last_axes


# ----------------  链式入口（包装 init） -----------------
from .pipeline import Step  # noqa: E402


def init_step(*args, allow_reinit: bool = True, **kwargs):
    """init 的惰性/可链式包装。"""

    def _maybe_init(*a, **k):
        if _initialized and allow_reinit:
            logger.debug("init_step skipped (already initialized)")
            return None
        return init(*a, **k)

    return Step(_maybe_init, *args, **kwargs)


# Re-export color set utilities
from .colorset import list_color_sets, get_color_set, apply_color_set, is_grayscale_discriminable  # noqa: E402
from .presets import (
    list_paper_presets,
    get_paper_preset,
    apply_paper_preset,
    styles_dir,
    fonts_dir,
    available_styles,
    register_fonts,
    apply_style,
    set_style,
    style_step,
)  # noqa: E402
from .draw import draw, draw_step  # noqa: E402
from .save import save, save_step  # noqa: E402
from .misc import (
    assert_style_set,
    assert_style_unset,
    assert_initialized,
    raise_exception,
    raise_exception_from,
)  # noqa: E402

__all__ = [
    # core lifecycle
    "init",
    "destroy",
    "PaperPlotException",
    # style & presets
    "apply_style",
    "set_style",
    "list_paper_presets",
    "get_paper_preset",
    "apply_paper_preset",
    "available_styles",
    "register_fonts",
    "styles_dir",
    "fonts_dir",
    # drawing & saving
    "draw",
    "save",
    "last_figure",
    "last_axes",
    # colors
    "list_color_sets",
    "get_color_set",
    "apply_color_set",
    "is_grayscale_discriminable",
    # pipeline
    "Step",
    "init_step",
    "style_step",
    "draw_step",
    "save_step",
]
