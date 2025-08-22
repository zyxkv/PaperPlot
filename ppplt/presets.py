"""
Style & preset utilities (expanded).

Includes:
1. Low level style/font helpers (moved from __init__):
    - styles_dir / fonts_dir / available_styles / register_fonts / apply_style / set_style
2. Preset registry & application combining style + color set.
3. style_step: pipeline step (uses Step from pipeline module).

NOTE: These functions access global state (_phase, logger, etc.) defined in ppplt.__init__.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

import importlib

# Import shared state & helpers lazily to avoid circular import at module import time.
import ppplt as _core
from .pipeline import Step
from .colorset import apply_color_set

# ---------------------------
# Font & style filesystem helpers
# ---------------------------


def styles_dir() -> Path:
    pkg = Path(__file__).resolve().parent / "styles"
    if pkg.exists():
        return pkg
    # fallback: repository root (editable install)
    root = Path(__file__).resolve().parent.parent
    if (root / "styles").exists():
        return root / "styles"
    return pkg


def fonts_dir() -> Path:
    pkg = Path(__file__).resolve().parent / "fonts"
    if pkg.exists():
        return pkg
    root = Path(__file__).resolve().parent.parent
    if (root / "fonts").exists():
        return root / "fonts"
    return pkg


def available_styles() -> List[str]:
    d = styles_dir()
    if not d.exists():
        return []
    return [p.stem for p in d.glob("*.mplstyle")]


def register_fonts() -> None:
    from matplotlib import font_manager as fm

    fdir = fonts_dir()
    if not fdir.exists():
        return
    for name in ("SimsunExtG.ttf", "times.ttf", "MapleMono-NF-CN-Regular.ttf"):
        fp = fdir / name
        if fp.exists():
            try:
                fm.fontManager.addfont(str(fp))
            except Exception:
                pass
    try:
        fm._load_fontmanager(try_read_cache=False)  # type: ignore[attr-defined]
    except Exception:
        fm.fontManager.refresh_fonts()


def apply_style(name: str, *, register_font: bool = True) -> None:
    import matplotlib as mpl

    if register_font:
        register_fonts()
    target = styles_dir() / f"{name.upper()}.mplstyle"
    if not target.exists():
        raise ValueError(f"Style '{name}' not found. Available: {available_styles()}")
    mpl.style.use(str(target))


def set_style(*, style: Optional[str] = None, preset: Optional[str] = None, register_font: bool = True) -> None:
    from .presets import apply_paper_preset as _apply_preset  # self-reference ok
    from . import _phase, _Phase  # state
    from . import _require_phase  # type: ignore
    from . import logger

    _require_phase(_Phase.INITIALIZED, _Phase.STYLE_SET, _Phase.DRAWN, _Phase.SAVED)
    if style and preset:
        raise _core.PaperPlotException("'style' 与 'preset' 不能同时指定")
    if not style and not preset:
        raise _core.PaperPlotException("需要提供 'style' 或 'preset'")
    if preset:
        _apply_preset(preset)
    else:
        apply_style(style, register_font=register_font)  # type: ignore[arg-type]
    _core._phase = _Phase.STYLE_SET  # update global phase
    logger.info(f"🎨 Style set -> {_core._phase.name} ({'preset:'+preset if preset else 'style:'+style})")


# ---------------------------
# Presets registry
# ---------------------------


_PRESETS: Dict[str, Dict[str, str]] = {
    # name: {style, colors}
    "ieee-modern": {"style": "IEEE", "colors": "Modern Scientific"},
    "ieee-contrast1": {"style": "IEEE", "colors": "Contrast Set 1"},
    "ieee-okabe": {"style": "IEEE", "colors": "Okabe-Ito"},
    "gb-modern": {"style": "GB", "colors": "Modern Scientific"},
    "gb-contrast2": {"style": "GB", "colors": "Contrast Set 2"},
    "gb-okabe": {"style": "GB", "colors": "Okabe-Ito"},
    # grayscale-safe presets (for printing/photocopy)
    "ieee-gray": {"style": "IEEE", "colors": "Grayscale-Safe"},
    "gb-gray": {"style": "GB", "colors": "Grayscale-Safe"},
}


def list_paper_presets() -> List[str]:
    return list(_PRESETS.keys())


def get_paper_preset(name: str) -> Dict[str, str]:
    key = name.lower()
    if key not in _PRESETS:
        raise ValueError(f"Preset '{name}' not found. Available: {list_paper_presets()}")
    return dict(_PRESETS[key])


def apply_paper_preset(name: str) -> None:
    info = get_paper_preset(name)
    apply_style(info["style"])  # also registers fonts
    apply_color_set(info["colors"])  # set color cycle


# ---------------------------
# Pipeline step
# ---------------------------
def style_step(*args, **kwargs):
    return Step(set_style, *args, **kwargs)


__all__ = [
    # style helpers
    "styles_dir",
    "fonts_dir",
    "available_styles",
    "register_fonts",
    "apply_style",
    "set_style",
    # presets
    "list_paper_presets",
    "get_paper_preset",
    "apply_paper_preset",
    # pipeline
    "style_step",
]
