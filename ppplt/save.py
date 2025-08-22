"""Save utilities for last drawn figure.

Includes save() and save_step for pipeline.
"""

from __future__ import annotations
from typing import Optional, Sequence, Any, List
import os as _os

import ppplt as _core
from .pipeline import Step


def save(
    path: str,
    *,
    dpi: Optional[int] = None,
    formats: Optional[Sequence[str]] = None,
    bbox_inches: Optional[str] = "tight",
    **kwargs: Any,
) -> List[str]:
    from . import _require_phase, _Phase, logger

    _require_phase(_Phase.DRAWN, _Phase.SAVED)
    if _core._last_fig is None:
        raise _core.PaperPlotException("当前没有可保存的图形 (last_fig is None)")
    base, ext = _os.path.splitext(path)
    written: List[str] = []
    if formats is None:
        if not ext:
            raise _core.PaperPlotException("未提供格式且路径无扩展名")
        out_path = path
        _core._last_fig.savefig(out_path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
        written.append(out_path)
    else:
        for f in formats:
            f = f.lstrip(".")
            out_path = f"{base}.{f}"
            _core._last_fig.savefig(out_path, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
            written.append(out_path)
    _core._phase = _Phase.SAVED
    logger.info("💾 Figure saved: " + ", ".join(written))
    return written


def save_step(*args, **kwargs):
    return Step(save, *args, **kwargs)


__all__ = ["save", "save_step"]
