"""
Color set utilities for paper_plot.

API:
- list_color_sets() -> list[str]
- get_color_set(name: str) -> list[str]
- apply_color_set(name: str) -> None

Behavior:
- Names are case-insensitive.
- apply_color_set sets Matplotlib axes.prop_cycle to the chosen scheme.
"""

from __future__ import annotations

from typing import Dict, List


colorsets: Dict[str, List[str]] = {
    "Contrast Set 1": [
        "#D55E00",
        "#0072B2",
        "#009E73",
        "#F0E442",
        "#CC79A7",
        "#56B4E9",
        "#E69F00",
        "#F4A582",
    ],
    "Contrast Set 2": [
        "#A6761D",
        "#666666",
        "#E7298A",
        "#66A61E",
        "#E6AB02",
        "#A6CEE3",
        "#1F78B4",
        "#B2DF8A",
    ],
    "Muted Yet Bold": [
        "#8B3A3A",
        "#2E8B57",
        "#4682B4",
        "#CD5C5C",
        "#5F9EA0",
        "#8A2BE2",
        "#FF6347",
        "#FFD700",
    ],
    "Refined Contrast": [
        "#8B4513",
        "#00CED1",
        "#808000",
        "#8FBC8F",
        "#2F4F4F",
        "#FF69B4",
        "#DAA520",
        "#4682B4",
    ],
    "Modern Scientific": [
        "#E41A1C",
        "#377EB8",
        "#4DAF4A",
        "#984EA3",
        "#FF7F00",
        "#FFFF33",
        "#A65628",
        "#F781BF",
    ],
    "Extended Elegance": [
        "#B22222",
        "#6A5ACD",
        "#2E8B57",
        "#FF8C00",
        "#20B2AA",
        "#9370DB",
        "#8FBC8F",
        "#A52A2A",
    ],
    "Pastel High Contrast": [
        "#F4A582",
        "#92C5DE",
        "#B2DF8A",
        "#FC9272",
        "#FFD92F",
        "#9E0142",
        "#D53E4F",
        "#F46D43",
    ],
    "Softened Bold Colors": [
        "#F28E2B",
        "#4E79A7",
        "#E15759",
        "#76B7B2",
        "#59A14F",
        "#EDC948",
        "#B07AA1",
        "#FF9DA7",
    ],
    # Color-blind friendly (Okabe-Ito)
    # Ref: Okabe & Ito: https://jfly.uni-koeln.de/color/
    "Okabe-Ito": [
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
        "#000000",
    ],
    # Brewer qualitative (Set2/Paired-like) selections (color-blind friendly-ish)
    "Brewer-Qual-Soft": [
        "#66C2A5",
        "#FC8D62",
        "#8DA0CB",
        "#E78AC3",
        "#A6D854",
        "#FFD92F",
        "#E5C494",
        "#B3B3B3",
    ],
    # Grayscale-safe (manually curated increasing luminance)
    # Grayscale-safe with spaced luminance steps (~0,10,25,40,55,70,85,95)
    "Grayscale-Safe": [
        "#000000",  # 0%
        "#1A1A1A",  # ~10%
        "#404040",  # ~25%
        "#666666",  # ~40%
        "#8C8C8C",  # ~55%
        "#B3B3B3",  # ~70%
        "#D9D9D9",  # ~85%
        "#F2F2F2",  # ~95%
    ],
}


def list_color_sets() -> List[str]:
    return list(colorsets.keys())


def get_color_set(name: str) -> List[str]:
    # Case-insensitive lookup
    key = None
    lname = name.lower()
    for k in colorsets.keys():
        if k.lower() == lname:
            key = k
            break
    if key is None:
        raise ValueError(f"Color set '{name}' not found. Available: {list_color_sets()}")
    return list(colorsets[key])


def apply_color_set(name: str) -> None:
    from matplotlib import rcParams
    from cycler import cycler

    colors = get_color_set(name)
    rcParams["axes.prop_cycle"] = cycler(color=colors)


def is_grayscale_discriminable(name: str, min_delta: float = 8.0) -> bool:
    """Rudimentary grayscale discriminability check.

    Converts hex colors to perceived luminance (Y) and checks if adjacent
    colors differ by at least `min_delta` on 0-100 scale.
    """
    import colorsys

    def luminance_hex(h: str) -> float:
        h = h.lstrip("#")
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        # Rec. 709 luma approximation scaled 0-100
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return y * 100.0

    cols = get_color_set(name)
    ys = [luminance_hex(c) for c in cols]
    ys_sorted = sorted(ys)
    for a, b in zip(ys_sorted, ys_sorted[1:]):
        if abs(b - a) < min_delta:
            return False
    return True
