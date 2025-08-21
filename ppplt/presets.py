"""
Presets that combine a style (IEEE/GB) and a color set.

API:
- list_paper_presets() -> list[str]
- get_paper_preset(name: str) -> dict
- apply_paper_preset(name: str) -> None
"""

from __future__ import annotations

from typing import Dict, List

from . import apply_style
from .colorset import apply_color_set


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
